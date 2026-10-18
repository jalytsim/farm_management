"""
api_sentinel.py — Blueprint /api/sentinel

GET  /api/sentinel/farm/<farm_id>/sat-index
GET  /api/sentinel/forest/<forest_id>/sat-index
GET  /api/sentinel/farm/<farm_id>/sat-index/pdf
POST /api/sentinel/guest/sat-index/pdf
"""

import asyncio

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

sentinel_bp = Blueprint('api_sentinel', __name__, url_prefix='/api/sentinel')


def _get_user():
    identity = get_jwt_identity()
    uid = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(uid)


def _attach_agb_trend(result, property_type, entity_id=None, crop_name=None, area_ha=None):
    """Ajoute result['agb_trend'] : AGB (t/ha) calculé depuis l'historique 5 ans
    et la prévision des indices. Ne fait jamais échouer la route."""
    from app.utils.carbon_index_utils import compute_agb_trend
    try:
        if entity_id is not None:
            from app.models import Point
            from app.utils.sentinel_utils import _compute_area_ha_from_points
            owner_type = 'farmer' if property_type == 'farm' else 'forest'
            points = Point.query.filter_by(owner_type=owner_type, owner_id=str(entity_id)).order_by(Point.id).all()
            area_ha = _compute_area_ha_from_points(points)[0] or area_ha
        if property_type == 'farm' and entity_id is not None and not crop_name:
            from app.models import Farm
            from app.routes.api_gfw import _build_farm_info
            farm = Farm.query.filter_by(farm_id=entity_id).first()
            if farm:
                crops = [c.get('crop') for c in _build_farm_info(farm).get('crops', [])
                         if c.get('crop') not in (None, 'N/A')]
                crop_name = crops[-1] if crops else None
        area_ha = area_ha or (result.get('ltv') or {}).get('area_ha')
        result['agb_trend'] = compute_agb_trend(
            result.get('history'), result.get('forecast'), crop_name, property_type, area_ha)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f'[AGB trend] {property_type} {entity_id}: {e}')
        result['agb_trend'] = None
    return result


@sentinel_bp.route('/farm/<string:farm_id>/sat-index', methods=['GET'])
@jwt_required()
def farm_sat_index(farm_id):
    from app.utils.sentinel_utils import get_sat_index_full
    import asyncio
    loan_amount    = request.args.get('loan_amount',    type=float)
    yield_t_per_ha = request.args.get('yield_t_per_ha', type=float, default=1.5)
    price_per_t    = request.args.get('price_per_t',    type=float, default=500)
    force_refresh  = request.args.get('refresh', '').lower() == 'true'
    hist_yield_1   = request.args.get('hist_yield_1',   type=float)
    hist_yield_2   = request.args.get('hist_yield_2',   type=float)

    result, error = asyncio.run(get_sat_index_full(
        'farm', farm_id,
        loan_amount=loan_amount,
        yield_t_per_ha=yield_t_per_ha,
        price_per_t=price_per_t,
        force_refresh=force_refresh,
        hist_yield_1=hist_yield_1,
        hist_yield_2=hist_yield_2,
    ))
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(_attach_agb_trend(result, 'farm', farm_id)), 200

@sentinel_bp.route('/guest/classification/<string:index_name>', methods=['POST'])
def guest_classification_image(index_name):
    """Version guest de la classification : géométrie fournie directement (POST body),
    pas de lookup Farm/Point en DB. Même format de réponse que la route account."""
    from app.utils.sentinel_utils import (
        _extract_polygon_coords, _compute_class_areas, CLASSIFICATION_THRESHOLDS,
        _compute_area_ha_from_coords
    )
    from app.utils.feature_payment_utils import has_guest_access
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import base64
    import logging
    logger = logging.getLogger(__name__)

    if index_name not in CLASSIFICATION_THRESHOLDS:
        return jsonify({'error': f'Index "{index_name}" is not supported'}), 400

    data    = request.get_json(silent=True) or {}
    phone   = data.get('phone')
    geojson = data.get('geojson')

    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400

    try:
        if not has_guest_access(phone, 'reportndviguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    coords = _extract_polygon_coords(geojson)
    if not coords:
        return jsonify({'error': 'Invalid or missing polygon geometry'}), 400

    ring = list(coords)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    geometry = {'type': 'Polygon', 'coordinates': [ring]}

    now = datetime.utcnow()
    date_to = now.strftime('%Y-%m-%dT23:59:59Z')
    date_from = (now - relativedelta(months=1)).strftime('%Y-%m-%dT00:00:00Z')

    try:
        area_ha, _ = _compute_area_ha_from_coords(coords)
        # points=None : _compute_class_areas ne calcule pas la surface elle-même dans ce cas
        class_areas, png_bytes = _compute_class_areas(
            geometry, date_from, date_to, index_name,
            points=None, width=800, height=800
        )
        poly_area_km2 = area_ha / 100.0
        for c in class_areas:
            c['area_km2'] = round((c['pct'] / 100.0) * poly_area_km2, 4)
    except Exception as e:
        logger.error(f'[guest_classification] {index_name} failed: {e}')
        return jsonify({'error': f'Classification failed: {str(e)}'}), 500

    return jsonify({
        'index':        index_name,
        'classes':      class_areas,
        'image_base64': base64.b64encode(png_bytes).decode('utf-8'),
        'period':       {'from': date_from[:10], 'to': date_to[:10]},
    }), 200 

@sentinel_bp.route('/forest/<int:forest_id>/sat-index', methods=['GET'])
@jwt_required()
def forest_sat_index(forest_id):
    from app.utils.sentinel_utils import get_sat_index_full
    import asyncio
    result, error = asyncio.run(get_sat_index_full('forest', forest_id))
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(_attach_agb_trend(result, 'forest', forest_id)), 200


def _sat_pdf_response(result, report_id, farm_info, ring, filename, browser_safe=False):
    """
    PDF « Satellite Index » (ReportLab, même gabarit que Carbon / EUDR), conservé
    7 jours avec l'en-tête X-Report-Token (re-téléchargement après rechargement).
    browser_safe : Content-Type octet-stream pour les PDF invités affichés dans
    la page (les gestionnaires de téléchargement type IDM interceptent sinon
    application/pdf) — le frontend re-type le blob.
    """
    import io
    from app.routes.api_gfw import LOGO_AGRI, LOGO_PARROT
    from app.utils.pdf_reports import build_sat_index_pdf
    from app.utils.stored_reports import attach_stored_report

    pdf_bytes = build_sat_index_pdf(
        report_id, farm_info, result, coords=ring,
        logo_parrot=LOGO_PARROT, logo_agri=LOGO_AGRI,
    )
    response = send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/octet-stream' if browser_safe else 'application/pdf',
        as_attachment=not browser_safe,
        download_name=filename,
    )
    return attach_stored_report(response, pdf_bytes, filename)


@sentinel_bp.route('/farm/<string:farm_id>/sat-index/pdf', methods=['GET'])
@jwt_required()
def farm_sat_index_pdf(farm_id):
    from app.models import Farm
    from app.routes.api_gfw import _build_farm_info, _owner_ring
    from app.utils.report_access import check_owner_access
    from app.utils.sentinel_utils import get_sat_index_full

    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm:
        return jsonify({'error': 'Farm not found'}), 404
    denied = check_owner_access(farm, 'farm')
    if denied:
        return denied

    result, error = asyncio.run(get_sat_index_full(
        'farm', farm_id,
        loan_amount    = request.args.get('loan_amount',    type=float),
        yield_t_per_ha = request.args.get('yield_t_per_ha', type=float, default=1.5),
        price_per_t    = request.args.get('price_per_t',    type=float, default=500),
        hist_yield_1   = request.args.get('hist_yield_1',   type=float),
        hist_yield_2   = request.args.get('hist_yield_2',   type=float),
    ))
    if error:
        return jsonify({'error': error}), 500

    farm_info = _build_farm_info(farm)
    crops = [c.get('crop') for c in farm_info.get('crops', []) if c.get('crop') not in (None, 'N/A')]
    farm_info['crop'] = crops[-1] if crops else None
    result = _attach_agb_trend(result, 'farm', farm_id)
    try:
        return _sat_pdf_response(result, farm_id, farm_info, _owner_ring('farmer', farm_id, farm.geolocation),
                                 f'Satellite_Index_Report_{farm_id}.pdf')
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500



@sentinel_bp.route('/farm/<string:farm_id>/classification/<string:index_name>', methods=['GET'])
@jwt_required()
def farm_classification_image(farm_id, index_name):
    """Retourne l'image classifiée PNG + les surfaces par classe en JSON."""
    from app.utils.sentinel_utils import (
        _build_geometry, _compute_class_areas, CLASSIFICATION_THRESHOLDS
    )
    from app.models import Point, Farm
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import base64, io

    if index_name not in CLASSIFICATION_THRESHOLDS:
        return jsonify({'error': f'Index "{index_name}" is not supported'}), 400

    entity = Farm.query.filter_by(farm_id=farm_id).first()
    if not entity:
        return jsonify({'error': 'Farm not found'}), 404

    points = Point.query.filter_by(owner_type='farmer', owner_id=str(farm_id)).order_by(Point.id).all()
    geometry = _build_geometry(points, entity.geolocation)
    if not geometry:
        return jsonify({'error': 'No geometry available'}), 400

    now = datetime.utcnow()
    date_to = now.strftime('%Y-%m-%dT23:59:59Z')
    date_from = (now - relativedelta(months=1)).strftime('%Y-%m-%dT00:00:00Z')

    try:
        class_areas, png_bytes = _compute_class_areas(geometry, date_from, date_to, index_name, points=points)
    except Exception as e:
        return jsonify({'error': f'Classification failed: {str(e)}'}), 500

    return jsonify({
        'index':        index_name,
        'classes':      class_areas,
        'image_base64': base64.b64encode(png_bytes).decode('utf-8'),
        'period':       {'from': date_from[:10], 'to': date_to[:10]},
    }), 200


@sentinel_bp.route('/forest/<int:forest_id>/classification/<string:index_name>', methods=['GET'])
@jwt_required()
def forest_classification_image(forest_id, index_name):
    """Retourne l'image classifiée PNG + les surfaces par classe en JSON (forêt)."""
    from app.utils.sentinel_utils import (
        _build_geometry, _compute_class_areas, CLASSIFICATION_THRESHOLDS
    )
    from app.models import Point, Forest
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    import base64, io

    if index_name not in CLASSIFICATION_THRESHOLDS:
        return jsonify({'error': f'Index "{index_name}" is not supported'}), 400

    entity = Forest.query.get(forest_id)
    if not entity:
        return jsonify({'error': 'Forest not found'}), 404

    points = Point.query.filter_by(owner_type='forest', owner_id=str(forest_id)).order_by(Point.id).all()
    geometry = _build_geometry(points, None)
    if not geometry:
        return jsonify({'error': 'No geometry available'}), 400

    now = datetime.utcnow()
    date_to = now.strftime('%Y-%m-%dT23:59:59Z')
    date_from = (now - relativedelta(months=1)).strftime('%Y-%m-%dT00:00:00Z')

    try:
        class_areas, png_bytes = _compute_class_areas(geometry, date_from, date_to, index_name, points=points)
    except Exception as e:
        return jsonify({'error': f'Classification failed: {str(e)}'}), 500

    return jsonify({
        'index':        index_name,
        'classes':      class_areas,
        'image_base64': base64.b64encode(png_bytes).decode('utf-8'),
        'period':       {'from': date_from[:10], 'to': date_to[:10]},
    }), 200
    
@sentinel_bp.route('/farm/<string:farm_id>/weekly-trend', methods=['GET'])   # <-- LIGNE À AJOUTER
@jwt_required()
def farm_weekly_trend(farm_id):
    from app.utils.sentinel_utils import get_weekly_trend
    weeks = request.args.get('weeks', type=int, default=13)
    weeks = max(1, min(weeks, 260))  # garde-fou : 1 semaine à 5 ans max

    result, error = get_weekly_trend('farm', farm_id, weeks=weeks)
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


@sentinel_bp.route('/forest/<int:forest_id>/weekly-trend', methods=['GET'])
@jwt_required()
def forest_weekly_trend(forest_id):
    from app.utils.sentinel_utils import get_weekly_trend
    weeks = request.args.get('weeks', type=int, default=13)
    weeks = max(1, min(weeks, 260))

    result, error = get_weekly_trend('forest', forest_id, weeks=weeks)
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200

@sentinel_bp.route('/farm/<string:farm_id>/monthly-trend', methods=['GET'])
@jwt_required()
def farm_monthly_trend(farm_id):
    from app.utils.sentinel_utils import get_monthly_trend
    months = request.args.get('months', type=int, default=12)
    months = max(1, min(months, 60))  # garde-fou : 1 mois à 5 ans max

    result, error = get_monthly_trend('farm', farm_id, months=months)
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


@sentinel_bp.route('/forest/<int:forest_id>/monthly-trend', methods=['GET'])
@jwt_required()
def forest_monthly_trend(forest_id):
    from app.utils.sentinel_utils import get_monthly_trend
    months = request.args.get('months', type=int, default=12)
    months = max(1, min(months, 60))

    result, error = get_monthly_trend('forest', forest_id, months=months)
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200

@sentinel_bp.route('/guest/sat-index', methods=['POST'])
def guest_sat_index():
    from app.utils.sentinel_utils import get_sat_index_full_guest
    from app.utils.feature_payment_utils import has_guest_access
    import asyncio
    import logging
    import traceback

    logger = logging.getLogger(__name__)

    data     = request.get_json(silent=True) or {}
    phone    = data.get('phone')
    geojson  = data.get('geojson')
    # ✅ agent_id (référent terrain, saisi dans StepUserInfo.jsx) manquait ici —
    # ce rapport n'était pas suivi dans /api/gfw/admin/agents/summary alors que
    # EUDR et Carbon le sont déjà (voir _log_gfw plus bas).
    agent_id = data.get('agent_id')

    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400

    try:
        if not has_guest_access(phone, 'reportndviguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        logger.error(f'[guest_sat_index] has_guest_access failed: {e}\n{traceback.format_exc()}')
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    try:
        result, error = asyncio.run(get_sat_index_full_guest(
            geojson, phone,
            loan_amount    = data.get('loan_amount'),
            yield_t_per_ha = data.get('yield_t_per_ha', 1.5),
            price_per_t    = data.get('price_per_t', 500),
            force_refresh  = bool(data.get('refresh', False)),
            hist_yield_1   = data.get('hist_yield_1'),
            hist_yield_2   = data.get('hist_yield_2'),
        ))
    except Exception as e:
        # ✅ FIX : sans ce try/except, toute exception non prévue (ex: table
        # 'guestsentinelcache' absente en base, erreur DB, etc.) remontait en
        # 500 Flask générique sans aucun détail exploitable côté frontend/logs.
        logger.error(f'[guest_sat_index] Unhandled exception: {e}\n{traceback.format_exc()}')
        return jsonify({'error': f'Internal error while generating guest report: {str(e)}'}), 500

    if error:
        code = 400 if 'polygon' in error.lower() else 500
        return jsonify({'error': error}), code

    from app.routes.api_gfw import _log_gfw
    _log_gfw('guest_sentinel_report', 'guest', phone, agent_id=agent_id)

    return jsonify(_attach_agb_trend(result, 'farm', crop_name=data.get('crop'))), 200


@sentinel_bp.route('/guest/sat-index/pdf', methods=['POST'])
def guest_sat_index_pdf():
    """
    PDF du rapport d'indices satellite invité — 100 % backend ReportLab, comme
    /api/gfw/guest/eudr-pdf et /api/gfw/guest/carbon-pdf. Mêmes données que
    /guest/sat-index (servies par GuestSentinelCache), même contrôle d'accès payé.
    Body : {geojson, phone, farm_info?, crop?, agent_id?, loan_amount?, ...}
    """
    from app.routes.api_gfw import _log_gfw
    from app.utils.feature_payment_utils import has_guest_access
    from app.utils.sentinel_utils import _extract_polygon_coords, get_sat_index_full_guest

    data    = request.get_json(silent=True) or {}
    phone   = data.get('phone')
    geojson = data.get('geojson')
    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400
    if not has_guest_access(phone, 'reportndviguest'):
        return jsonify({'error': 'No active paid access for this phone number'}), 403

    result, error = asyncio.run(get_sat_index_full_guest(
        geojson, phone,
        loan_amount    = data.get('loan_amount'),
        yield_t_per_ha = data.get('yield_t_per_ha', 1.5),
        price_per_t    = data.get('price_per_t', 500),
        hist_yield_1   = data.get('hist_yield_1'),
        hist_yield_2   = data.get('hist_yield_2'),
    ))
    if error:
        return jsonify({'error': error}), 400 if 'polygon' in error.lower() else 500

    farm_info = data.get('farm_info') or {}
    crop = data.get('crop') or farm_info.get('crop') or next(
        (c.get('crop') for c in reversed(farm_info.get('crops') or []) if c.get('crop')), None)
    farm_info = {**farm_info, 'crop': crop}
    report_id = str(farm_info.get('farm_id') or data.get('guest_id') or 'GUEST')
    if not farm_info.get('name'):
        result['name'] = None    # « Guest polygon » n'a pas de sens dans le PDF
    coords = _extract_polygon_coords(geojson)
    ring = [[float(lon), float(lat)] for lon, lat in coords] if coords else None

    try:
        response = _sat_pdf_response(_attach_agb_trend(result, 'farm', crop_name=crop), report_id,
                                     farm_info, ring, f'Satellite_Index_Report_{report_id}.pdf',
                                     browser_safe=True)
    except Exception as e:
        import traceback; traceback.print_exc()
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500
    _log_gfw('guest_sentinel_pdf', 'guest', phone, agent_id=data.get('agent_id'))
    return response


@sentinel_bp.route('/farm/<string:farm_id>/crop-biomass', methods=['GET'])
@jwt_required()
def farm_crop_biomass(farm_id):
    """
    GET /api/sentinel/farm/<farm_id>/crop-biomass
    Biomasse de la parcelle selon la formule de sa culture (maize, rice, wheat,
    cocoa via indices Sentinel ; coffee via allométrie).
    Query : crop (sinon culture du dernier FarmData), dbh_cm, height_m,
            wood_density, trees (café uniquement).
    """
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    from app.models import Farm, FarmData, Crop, Point
    from app.utils.sentinel_utils import (
        _build_geometry, _compute_area_ha_from_points, _call_statistics, _parse_response,
    )
    from app.utils.crop_biomass_utils import (
        INDEX_MODELS, SUPPORTED_CROPS, compute_crop_biomass, resolve_crop_key,
    )

    farm = Farm.query.filter_by(farm_id=farm_id).first()
    if not farm:
        return jsonify({'error': 'Farm not found'}), 404

    farm_data = (FarmData.query.filter_by(farm_id=farm_id)
                 .order_by(FarmData.date_created.desc()).first())
    crop_name = request.args.get('crop')
    if not crop_name and farm_data:
        crop = Crop.query.get(farm_data.crop_id)
        crop_name = crop.name if crop else None
    if not crop_name:
        return jsonify({'error': f"No crop recorded for this farm — pass ?crop={'|'.join(SUPPORTED_CROPS)}"}), 400

    points = Point.query.filter_by(owner_type='farmer', owner_id=str(farm_id)).order_by(Point.id).all()
    area_ha, _ = _compute_area_ha_from_points(points)
    if not area_ha and farm_data and farm_data.tilled_land_size:
        area_ha = farm_data.tilled_land_size

    rows = []
    # Les indices ne servent qu'aux cultures à modèle satellite (cacao inclus,
    # qui bascule sur l'allométrie si dbh_cm est fourni).
    if resolve_crop_key(crop_name) in INDEX_MODELS:
        geometry = _build_geometry(points, farm.geolocation)
        if not geometry:
            return jsonify({'error': 'No geometry available — add polygon points first'}), 400
        now = datetime.utcnow()
        try:
            raw = _call_statistics(
                geometry,
                (now - relativedelta(months=6)).strftime('%Y-%m-%dT00:00:00Z'),
                now.strftime('%Y-%m-%dT23:59:59Z'),
                interval='P1M',
            )
            rows, _ = _parse_response(raw)
        except Exception as e:
            import traceback; traceback.print_exc()
            return jsonify({'error': f'Sentinel query failed: {str(e)}'}), 500

    result, error = compute_crop_biomass(
        crop_name, rows, area_ha,
        dbh_cm=request.args.get('dbh_cm', type=float),
        height_m=request.args.get('height_m', type=float),
        wood_density=request.args.get('wood_density', type=float),
        number_of_trees=request.args.get('trees', type=int) or (farm_data.number_of_tree if farm_data else None),
    )
    if error:
        return jsonify({'error': error}), 400
    result.update({'farm_id': farm_id, 'farm_name': farm.name})
    return jsonify(result), 200


@sentinel_bp.route('/guest/carbon-extra', methods=['POST'])
def guest_carbon_extra():
    """
    Complément au Carbon Report guest existant (chiffres GFW émissions/
    absorptions, inchangés) — affiché en plus, pas à la place :
      - property_type='forest' : AGB/BGB estimés depuis le NDVI (même modèle
        que /api/tree-co2/forest/<id>/biomass-index côté admin).
      - property_type='farm'   : Carbone organique du sol (SoilGrids ISRIC,
        au centroïde) + culture prédite (même modèle RandomForest que
        CropPredictionPanel.jsx côté admin).
    POST body : { geojson, phone, property_type: 'forest'|'farm', agent_id? }
    """
    import asyncio
    import logging
    import traceback
    from app.utils.feature_payment_utils import has_guest_access
    from app.utils.sentinel_utils import (
        _extract_polygon_coords, _compute_area_ha_from_coords,
        get_sat_index_full_guest, _fetch_soc_soilgrids,
    )
    from app.utils.tree_co2_utils import compute_forest_biomass_from_index
    from app.utils.crop_classifier_utils import predict_crop_from_geojson

    logger = logging.getLogger(__name__)

    data          = request.get_json(silent=True) or {}
    phone         = data.get('phone')
    geojson       = data.get('geojson')
    property_type = data.get('property_type')
    agent_id      = data.get('agent_id')

    if not phone or not geojson or property_type not in ('forest', 'farm'):
        return jsonify({'error': "phone, geojson and property_type ('forest'|'farm') are required"}), 400

    try:
        # Même feature payante que le Carbon Report principal — pas de
        # paiement séparé pour ce complément.
        if not has_guest_access(phone, 'reportcarbonguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        logger.error(f'[guest_carbon_extra] has_guest_access failed: {e}\n{traceback.format_exc()}')
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    coords = _extract_polygon_coords(geojson)
    if not coords:
        return jsonify({'error': 'Invalid or missing polygon geometry'}), 400

    try:
        history_result, error = asyncio.run(get_sat_index_full_guest(geojson, phone))
    except Exception as e:
        logger.error(f'[guest_carbon_extra] Sentinel fetch failed: {e}\n{traceback.format_exc()}')
        return jsonify({'error': f'Internal error while fetching satellite data: {str(e)}'}), 500

    if error:
        return jsonify({'error': error}), 400

    result = {'property_type': property_type}

    if property_type == 'forest':
        # ✅ FIX : contrairement à la route admin (/api/tree-co2/forest/<id>/
        # biomass-index, alimentée par _parse_response bruts), l'historique
        # guest (get_sat_index_full_guest) enveloppe chaque indice dans
        # {value, raw, oob, tier} — même format que celui géré par _val()
        # dans crop_classifier_utils.py. Sans ce déballage, compute_forest_
        # biomass_from_index recevait un dict au lieu d'un float.
        def _ndvi_value(row):
            v = row.get('ndvi')
            return v.get('value') if isinstance(v, dict) else v

        ndvi_rows = [r for r in (history_result.get('history') or []) if _ndvi_value(r) is not None]
        if not ndvi_rows:
            return jsonify({'error': 'No cloud-free NDVI reading available for this polygon'}), 404
        latest = max(ndvi_rows, key=lambda r: r['date'])
        area_ha, _ = _compute_area_ha_from_coords(coords)
        if not area_ha:
            return jsonify({'error': 'Could not compute area from polygon'}), 400
        try:
            result['biomass'] = compute_forest_biomass_from_index(_ndvi_value(latest), area_ha, index_date=latest['date'])
            result['area_ha'] = round(area_ha, 4)
        except Exception as e:
            logger.error(f'[guest_carbon_extra] biomass calc failed: {e}\n{traceback.format_exc()}')
            return jsonify({'error': str(e)}), 500

    else:  # farm
        lons = [c[0] for c in coords]
        lats = [c[1] for c in coords]
        lon_c, lat_c = sum(lons) / len(lons), sum(lats) / len(lats)
        try:
            soc = asyncio.run(_fetch_soc_soilgrids(lat_c, lon_c))
        except Exception as e:
            logger.error(f'[guest_carbon_extra] SoilGrids fetch failed: {e}\n{traceback.format_exc()}')
            soc = None
        result['soc'] = soc
        result['centroid'] = {'lat': lat_c, 'lon': lon_c}

        # Prédiction de culture : purement complémentaire — une erreur ici
        # (modèle pas encore entraîné, historique insuffisant) ne doit pas
        # faire échouer le SOC, qui est la donnée principale demandée.
        crop_result, crop_error = predict_crop_from_geojson(geojson, phone)
        result['crop_prediction'] = crop_result
        if crop_error:
            result['crop_prediction_error'] = crop_error

        # Biomasse par culture : culture déclarée (body.crop) sinon culture prédite.
        # Complémentaire comme la prédiction : un échec n'invalide pas la réponse.
        from app.utils.crop_biomass_utils import compute_crop_biomass
        crop_name = data.get('crop') or (crop_result or {}).get('predicted_crop')
        if crop_name:
            area_ha, _ = _compute_area_ha_from_coords(coords)
            try:
                crop_biomass, biomass_error = compute_crop_biomass(
                    crop_name, history_result.get('history') or [], area_ha,
                    dbh_cm=data.get('dbh_cm'), height_m=data.get('height_m'),
                    wood_density=data.get('wood_density'), number_of_trees=data.get('trees'),
                )
            except Exception as e:
                logger.error(f'[guest_carbon_extra] crop biomass failed: {e}\n{traceback.format_exc()}')
                crop_biomass, biomass_error = None, str(e)
            result['crop_biomass'] = crop_biomass
            if biomass_error:
                result['crop_biomass_error'] = biomass_error

    from app.routes.api_gfw import _log_gfw
    _log_gfw('guest_carbon_extra', 'guest', phone, agent_id=agent_id)

    return jsonify(result), 200


# ══════════════════════════════════════════════════════════════════════════
# Guest parity for SentinelDashboard.jsx — Seasonal NDVI/Rainfall, Soil
# Carbon and Crop Prediction all required a real farm_id + JWT before, which
# a guest polygon submission never has. These three mirror the account-based
# routes above but take {geojson, phone} instead, gated by the same
# 'reportndviguest' paid feature as /guest/sat-index.
# ══════════════════════════════════════════════════════════════════════════

@sentinel_bp.route('/guest/monthly-trend', methods=['POST'])
def guest_monthly_trend():
    from app.utils.sentinel_utils import get_monthly_trend_guest
    from app.utils.feature_payment_utils import has_guest_access

    data    = request.get_json(silent=True) or {}
    phone   = data.get('phone')
    geojson = data.get('geojson')
    months  = int(data.get('months', 12))

    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400
    try:
        if not has_guest_access(phone, 'reportndviguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    result, error = get_monthly_trend_guest(geojson, months=months)
    if error:
        code = 400 if 'polygon' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


@sentinel_bp.route('/guest/soc', methods=['POST'])
def guest_soc():
    from app.utils.sentinel_utils import _extract_polygon_coords, _fetch_soc_soilgrids
    from app.utils.feature_payment_utils import has_guest_access
    import asyncio

    data    = request.get_json(silent=True) or {}
    phone   = data.get('phone')
    geojson = data.get('geojson')

    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400
    try:
        if not has_guest_access(phone, 'reportndviguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    coords = _extract_polygon_coords(geojson)
    if not coords:
        return jsonify({'error': 'Invalid or missing polygon geometry'}), 400

    lons = [c[0] for c in coords]
    lats = [c[1] for c in coords]
    lon_c, lat_c = sum(lons) / len(lons), sum(lats) / len(lats)

    result = asyncio.run(_fetch_soc_soilgrids(lat_c, lon_c))
    if not result:
        return jsonify({'error': 'SoilGrids API failed'}), 500
    return jsonify({'soc': result, 'centroid': {'lat': lat_c, 'lon': lon_c}}), 200


@sentinel_bp.route('/guest/soc-seq', methods=['POST'])
def guest_soc_seq():
    from app.utils.sentinel_utils import _extract_polygon_coords
    from app.utils.soc_seq_utils import get_gsocseq_ssm3, is_available
    from app.utils.feature_payment_utils import has_guest_access

    data    = request.get_json(silent=True) or {}
    phone   = data.get('phone')
    geojson = data.get('geojson')

    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400
    try:
        if not has_guest_access(phone, 'reportndviguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    if not is_available():
        return jsonify({'error': 'GSOCseq rasters not installed on this server yet'}), 503

    coords = _extract_polygon_coords(geojson)
    if not coords:
        return jsonify({'error': 'Invalid or missing polygon geometry'}), 400

    ring = list(coords)
    if ring[0] != ring[-1]:
        ring.append(ring[0])
    geometry = {'type': 'Polygon', 'coordinates': [ring]}

    result = get_gsocseq_ssm3(geometry)
    return jsonify(result), 200


@sentinel_bp.route('/guest/predict-crop', methods=['POST'])
def guest_predict_crop():
    from app.utils.crop_classifier_utils import predict_crop_from_geojson
    from app.utils.feature_payment_utils import has_guest_access

    data    = request.get_json(silent=True) or {}
    phone   = data.get('phone')
    geojson = data.get('geojson')

    if not phone or not geojson:
        return jsonify({'error': 'phone and geojson are required'}), 400
    try:
        if not has_guest_access(phone, 'reportndviguest'):
            return jsonify({'error': 'No active paid access for this phone number'}), 403
    except Exception as e:
        return jsonify({'error': f'Access check failed: {str(e)}'}), 500

    result, error = predict_crop_from_geojson(geojson, phone)
    if error:
        code = 400 if 'not trained' in error.lower() or 'not enough' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


# ── Calibration indice → biomasse des cultures pérennes (parcelles terrain) ──

def _require_admin():
    user = _get_user()
    if not user or not user.is_admin:
        return None, (jsonify({'error': 'Admin access required'}), 403)
    return user, None


@sentinel_bp.route('/crop-calibration', methods=['GET'])
@jwt_required()
def crop_calibration_status():
    """État de calibration par culture + parcelles de mesure enregistrées."""
    _, denied = _require_admin()
    if denied:
        return denied
    from app.models import CropCalibrationPlot
    from app.utils.crop_calibration_utils import (
        FAMILY_LABELS, MIN_LOO_R2, MIN_PLOTS, WINDOW_DAYS, all_calibration_status,
    )
    plots = CropCalibrationPlot.query.order_by(CropCalibrationPlot.measured_on.desc()).all()
    return jsonify({
        'families':    all_calibration_status(),
        'plots':       [p.to_dict() for p in plots],
        'crops':       FAMILY_LABELS,
        'rules':       {'min_plots': MIN_PLOTS, 'min_loo_r2': MIN_LOO_R2, 'window_days': WINDOW_DAYS},
    }), 200


@sentinel_bp.route('/crop-calibration/plots', methods=['POST'])
@jwt_required()
def crop_calibration_add_plot():
    """
    Body : {farm_id, crop, measured_on, mean_dbh_cm, mean_height_m,
            plants_per_ha, wood_density?, notes?}
    """
    user, denied = _require_admin()
    if denied:
        return denied
    from app.models import Farm
    from app.utils.crop_calibration_utils import create_plot
    data = request.get_json(silent=True) or {}
    farm = Farm.query.filter_by(farm_id=str(data.get('farm_id') or '').strip()).first()
    if not farm:
        return jsonify({'error': 'Farm not found'}), 404
    plot, error = create_plot(farm, data, user_id=user.id)
    if error:
        return jsonify({'error': error}), 400
    return jsonify(plot.to_dict()), 201


@sentinel_bp.route('/crop-calibration/plots/<int:plot_id>', methods=['DELETE'])
@jwt_required()
def crop_calibration_delete_plot(plot_id):
    _, denied = _require_admin()
    if denied:
        return denied
    from app import db
    from app.models import CropCalibrationPlot
    plot = CropCalibrationPlot.query.get(plot_id)
    if not plot:
        return jsonify({'error': 'Plot not found'}), 404
    db.session.delete(plot)
    db.session.commit()
    return jsonify({'deleted': plot_id}), 200


@sentinel_bp.route('/crop-model/train', methods=['POST'])
@jwt_required()
def train_crop_model():
    user = _get_user()
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin access required'}), 403

    from app.utils.crop_classifier_utils import train_model
    data = request.get_json(silent=True) or {}
    fetch_missing = bool(data.get('fetch_missing', False))
    max_fetch = int(data.get('max_fetch', 15))

    metrics, error = train_model(fetch_missing=fetch_missing, max_fetch=max_fetch)
    if error:
        return jsonify({'error': error}), 400
    return jsonify({'status': 'trained', 'metrics': metrics}), 200


@sentinel_bp.route('/crop-model/status', methods=['GET'])
@jwt_required()
def crop_model_status():
    from app.utils.crop_classifier_utils import get_model_status
    return jsonify(get_model_status()), 200


@sentinel_bp.route('/farm/<string:farm_id>/predict-crop', methods=['GET'])
@jwt_required()
def farm_predict_crop(farm_id):
    from app.utils.crop_classifier_utils import predict_crop
    result, error = predict_crop('farm', farm_id)
    if error:
        code = 400 if 'not trained' in error.lower() or 'not enough' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


@sentinel_bp.route('/farm/<string:farm_id>/confirm-crop', methods=['POST'])
@jwt_required()
def farm_confirm_crop(farm_id):
    """
    Confirme (ou corrige) la culture prédite pour une ferme — voir bouton
    "Confirmer" dans CropPredictionPanel.jsx. Stocke la confirmation dans
    CropPredictionConfirmation (pas FarmData) ; la ferme entrera dans la
    banque d'entraînement au prochain /crop-model/train, via
    _get_farm_crop_label() qui retombe dessus quand FarmData.crop_id est absent.
    """
    from app.utils.crop_classifier_utils import confirm_crop_prediction

    data = request.get_json(silent=True) or {}
    crop_id = data.get('crop_id')
    if not crop_id:
        return jsonify({'error': 'crop_id is required'}), 400

    entry, error = confirm_crop_prediction(
        farm_id, crop_id,
        confirmed_by=_get_user().id if _get_user() else None,
        predicted_crop=data.get('predicted_crop'),
        confidence=data.get('confidence'),
    )
    if error:
        return jsonify({'error': error}), 400

    return jsonify({
        'status':     'confirmed',
        'farm_id':    farm_id,
        'crop_id':    entry.crop_id,
        'confirmed_at': entry.confirmed_at.isoformat() if entry.confirmed_at else None,
    }), 200


@sentinel_bp.route('/farm/<string:farm_id>/soc', methods=['GET'])
@jwt_required()
def farm_soc(farm_id):
    from app.utils.sentinel_utils import _fetch_soc_soilgrids, _build_geometry
    from app.models import Farm, Point
    import asyncio

    entity = Farm.query.filter_by(farm_id=farm_id).first()
    if not entity:
        return jsonify({'error': 'Farm not found'}), 404
    points = Point.query.filter_by(owner_type='farmer', owner_id=str(farm_id)).all()
    if not points:
        return jsonify({'error': 'No boundary points'}), 400

    lon_c = sum(float(p.longitude) for p in points) / len(points)
    lat_c = sum(float(p.latitude) for p in points) / len(points)
    result = asyncio.run(_fetch_soc_soilgrids(lat_c, lon_c))
    if not result:
        return jsonify({'error': 'SoilGrids API failed'}), 500
    return jsonify({'soc': result, 'centroid': {'lat': lat_c, 'lon': lon_c}}), 200


@sentinel_bp.route('/farm/<string:farm_id>/soc-seq', methods=['GET'])
@jwt_required()
def farm_soc_seq(farm_id):
    """
    GET /api/sentinel/farm/<farm_id>/soc-seq
    Stock de carbone organique du sol + potentiel de séquestration, scénario
    FAO GSOCseq SSM3 — statistique zonale sur l'ensemble du polygone de la
    ferme (contrairement à /soc qui n'interroge que le centroïde).
    """
    from app.utils.sentinel_utils import _build_geometry
    from app.utils.soc_seq_utils import get_gsocseq_ssm3, is_available
    from app.models import Farm, Point

    entity = Farm.query.filter_by(farm_id=farm_id).first()
    if not entity:
        return jsonify({'error': 'Farm not found'}), 404

    if not is_available():
        return jsonify({'error': 'GSOCseq rasters not installed on this server yet'}), 503

    points = Point.query.filter_by(owner_type='farmer', owner_id=str(farm_id)).all()
    geometry = _build_geometry(points, getattr(entity, 'geolocation', None))
    if not geometry:
        return jsonify({'error': 'No boundary points or geolocation for this farm'}), 400

    result = get_gsocseq_ssm3(geometry)
    return jsonify(result), 200