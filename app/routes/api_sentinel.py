"""
api_sentinel.py — Blueprint /api/sentinel

GET  /api/sentinel/farm/<farm_id>/sat-index
GET  /api/sentinel/forest/<forest_id>/sat-index
GET  /api/sentinel/farm/<farm_id>/sat-index/pdf
"""

from flask import Blueprint, jsonify, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User

sentinel_bp = Blueprint('api_sentinel', __name__, url_prefix='/api/sentinel')


def _get_user():
    identity = get_jwt_identity()
    uid = identity['id'] if isinstance(identity, dict) else identity
    return User.query.get(uid)


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
    return jsonify(result), 200


@sentinel_bp.route('/forest/<int:forest_id>/sat-index', methods=['GET'])
@jwt_required()
def forest_sat_index(forest_id):
    from app.utils.sentinel_utils import get_sat_index_full
    import asyncio
    result, error = asyncio.run(get_sat_index_full('forest', forest_id))
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


@sentinel_bp.route('/farm/<string:farm_id>/sat-index/pdf', methods=['GET'])
@jwt_required()
def farm_sat_index_pdf(farm_id):
    from app.utils.sentinel_utils import get_sat_index_full
    from datetime import datetime
    import io

    loan_amount    = request.args.get('loan_amount',    type=float)
    yield_t_per_ha = request.args.get('yield_t_per_ha', type=float, default=1.5)
    price_per_t    = request.args.get('price_per_t',    type=float, default=500)
    hist_yield_1   = request.args.get('hist_yield_1',   type=float)
    hist_yield_2   = request.args.get('hist_yield_2',   type=float)

    result, error = asyncio.run(get_sat_index_full(
        'farm', farm_id,
        loan_amount=loan_amount,
        yield_t_per_ha=yield_t_per_ha,
        price_per_t=price_per_t,
        hist_yield_1=hist_yield_1,
        hist_yield_2=hist_yield_2,
    ))
    if error:
        return jsonify({'error': error}), 500

    html_str = _build_pdf_html(result)

    try:
        from weasyprint import HTML
        # Générer le PDF directement en mémoire
        pdf_bytes = HTML(string=html_str).write_pdf()
        if not pdf_bytes:
            return jsonify({'error': 'PDF generation produced empty output'}), 500

        filename = f"sat_index_{farm_id}_{datetime.utcnow().strftime('%Y%m%d')}.pdf"
        return send_file(
            io.BytesIO(pdf_bytes),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=filename,
        )
    except ImportError:
        return jsonify({'error': 'WeasyPrint not installed. Run: pip install weasyprint'}), 500
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500



def _build_chart_b64(history, forecast, index_name, color):
    """Generate a chart as base64 PNG for PDF embedding."""
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from matplotlib.dates import DateFormatter
        import pandas as pd, io, base64

        def _val(h, idx):
            v = h.get(idx)
            return v.get('value') if isinstance(v, dict) else v

        dates  = pd.to_datetime([h['date'] for h in history])
        values = [_val(h, index_name) for h in history]
        valid  = [(d, v) for d, v in zip(dates, values) if v is not None]
        if not valid:
            return None
        vd, vv = zip(*valid)

        fc   = forecast.get(index_name, [])
        fc_d = pd.to_datetime([f['date']      for f in fc])
        fc_v = [f['value']                    for f in fc]
        fc_lo= [f.get('lower_80', f['value']) for f in fc]
        fc_hi= [f.get('upper_80', f['value']) for f in fc]

        fig, ax = plt.subplots(figsize=(11, 2.8))
        bg = '#0f172a'
        fig.patch.set_facecolor(bg)
        ax.set_facecolor(bg)

        ax.plot(vd, vv, color=color, linewidth=2, label='Historical')
        ax.fill_between(vd, vv, alpha=0.12, color=color)

        if len(fc_d):
            ax.plot([vd[-1], fc_d[0]], [vv[-1], fc_v[0]],
                    color=color, linewidth=1.5, linestyle='--', alpha=0.6)
            ax.plot(fc_d, fc_v, color=color, linewidth=1.5, linestyle='--', label='Forecast')
            ax.fill_between(fc_d, fc_lo, fc_hi, alpha=0.18, color=color, label='80% CI')

        for spine in ax.spines.values():
            spine.set_color('#334155')
        ax.tick_params(colors='#64748b', labelsize=7.5)
        ax.xaxis.set_major_formatter(DateFormatter('%Y-%m'))
        plt.xticks(rotation=40)
        ax.set_ylim(-1.05, 1.05)
        ax.set_ylabel(index_name.upper(), color='#94a3b8', fontsize=9)
        ax.grid(axis='y', color='#1e293b', alpha=0.6, linewidth=0.7)
        ax.legend(facecolor='#1e293b', labelcolor='#94a3b8',
                  fontsize=7.5, loc='upper left', framealpha=0.8)
        ax.set_title(index_name.upper(), color='#e2e8f0',
                     fontsize=10, fontweight='bold', pad=4)
        plt.tight_layout(pad=0.5)

        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=130, facecolor=bg, bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception:
        return None


def _build_pdf_html(data):
    """Generate PDF HTML — includes charts, forecast table, historical table, and Multi-Index LTV analysis."""
    from datetime import datetime
    now_str  = datetime.utcnow().strftime('%B %d, %Y')
    name     = data.get('name', 'N/A')
    period   = data.get('period', {})
    ltv      = data.get('ltv')
    history  = data.get('history', [])
    forecast = data.get('forecast', {})

    IDX_META = {
        'ndvi': ('NDVI',  '#16a34a'),
        'evi':  ('EVI',   '#0d9488'),
        'savi': ('SAVI',  '#65a30d'),
        'ndmi': ('NDMI',  '#0284c7'),
        'ndwi': ('NDWI',  '#0ea5e9'),
        'nmdi': ('NMDI',  '#f97316'),
        'nbr':  ('NBR',   '#ef4444'),
        'bsi':  ('BSI',   '#92400e'),
    }

    last = history[-1] if history else {}

    def _get_val(row, idx):
        d = row.get(idx)
        if isinstance(d, dict):
            return d.get('value'), d.get('tier', {})
        return d, {}

    def idx_summary_row(idx, icon):
        label, color = IDX_META.get(idx, (idx.upper(), '#9ca3af'))
        val, tier = _get_val(last, idx)
        val_str   = f'{val:.4f}' if val is not None else 'N/A'
        tier_lbl  = tier.get('label', 'N/A')
        tier_c    = tier.get('color', '#9ca3af')
        return (
            f'<div class="idx-summary">'
            f'<span class="idx-icon">{icon}</span>'
            f'<span class="idx-name">{label}</span>'
            f'<span class="idx-val" style="color:{tier_c}">{val_str}</span>'
            f'<span class="idx-tier" style="background:{tier_c}22;color:{tier_c};'
            f'border:1px solid {tier_c}44">{tier_lbl}</span>'
            f'</div>'
        )

    summaries = (
        idx_summary_row('ndvi', '🌱') + idx_summary_row('evi',  '🌿') +
        idx_summary_row('savi', '🌾') + idx_summary_row('ndmi', '💧') +
        idx_summary_row('ndwi', '🌊') + idx_summary_row('nmdi', '☀️') +
        idx_summary_row('nbr',  '🔥') + idx_summary_row('bsi',  '⛰️')
    )

    # Charts for 4 main indices
    chart_rows = ''
    for idx, icon in [('ndvi','🌱'), ('ndmi','💧'), ('evi','🌿'), ('nmdi','☀️')]:
        _, color = IDX_META[idx]
        b64 = _build_chart_b64(history, forecast, idx, color)
        if b64:
            chart_rows += (
                f'<div class="chart-block">'
                f'<img src="data:image/png;base64,{b64}" '
                f'style="width:100%;border-radius:6px;display:block;"/>'
                f'</div>'
            )

    # Forecast/History table headers
    th = ''.join(f'<th>{v[0]}</th>' for v in IDX_META.values())

    # Forecast rows
    fc_quarters = forecast.get('ndvi', [])
    fc_body = ''
    for i, fc_q in enumerate(fc_quarters):
        cells = ''
        for idx, (_, color) in IDX_META.items():
            flist = forecast.get(idx) or []
            f = flist[i] if i < len(flist) else None
            if f:
                tc = f.get('tier', {}).get('color', color)
                cells += f'<td style="color:{tc};font-weight:600">{f["value"]:.4f}</td>'
            else:
                cells += '<td style="color:#4b5563">—</td>'
        fc_body += f'<tr><td class="qtr">{fc_q["quarter"]}</td>{cells}</tr>'
    if not fc_body:
        fc_body = '<tr><td colspan="9" style="color:#4b5563;text-align:center;padding:10px">No forecast data</td></tr>'

    # Historical rows
    hist_body = ''
    for row in reversed(history):
        cells = ''
        for idx, (_, color) in IDX_META.items():
            val, tier = _get_val(row, idx)
            if val is not None:
                tc = tier.get('color', color)
                cells += f'<td style="color:{tc}">{val:.4f}</td>'
            else:
                cells += '<td style="color:#4b5563">—</td>'
        hist_body += f'<tr><td class="qtr">{row["date"]}</td>{cells}</tr>'
    if not hist_body:
        hist_body = '<tr><td colspan="9" style="color:#4b5563;text-align:center;padding:10px">No data</td></tr>'

    # ── CONSTRUIRE LA SECTION MULTI-INDEX LTV EN TABLEAU ──
    ltv_section = ''
    if ltv and 'indices' in ltv:
        indices_data = ltv['indices']
        composite_data = ltv.get('composite', {})
        
        ltv_table_rows = ''
        # Parcourir chaque indice calculé par sentinel_utils.py
        for idx_key, idx_ltv in indices_data.items():
            val_raw = idx_ltv.get('index_value')
            val_str = f"{val_raw:.4f}" if val_raw is not None else "N/A"
            
            ltv_pct = idx_ltv.get('ltv_ratio_pct')
            ltv_str = f"{ltv_pct}%" if ltv_pct is not None else "N/A"
            
            ltv_table_rows += f"""
            <tr>
                <td style="text-align:left; font-weight:600; color:{idx_ltv['color']}">
                    {idx_ltv['icon']} {idx_ltv['label'].split('—')[0].strip()}
                </td>
                <td>{val_str}</td>
                <td>{idx_ltv.get('factor', 0.3):.4f}</td>
                <td>{idx_ltv.get('adjusted_yield_t_ha', 0):.3f} t/ha</td>
                <td style="text-align:right">USD {idx_ltv.get('estimated_crop_value_usd', 0):,.2f}</td>
                <td style="font-weight:600; color:#6ee7b7">{ltv_str}</td>
                <td>{idx_ltv.get('insurance_premium_pct', 3.0):.2f}%</td>
                <td>{idx_ltv.get('weight', 0)*100:.0f}%</td>
            </tr>
            """
            
        # Ajouter la ligne de résumé Composite Pondéré tout en bas du tableau
        comp_ltv = composite_data.get('ltv_ratio_pct')
        comp_ltv_str = f"{comp_ltv}%" if comp_ltv is not None else "N/A"
        
        ltv_table_rows += f"""
        <tr class="composite-row" style="background: #1e3a2a; border-top: 2px solid #34d399;">
            <td style="text-align:left; font-weight:bold; color:#34d399;">🧮 COMPOSITE PONDÉRÉ</td>
            <td>—</td>
            <td style="font-weight:bold;">{composite_data.get('factor', 0.3):.4f}</td>
            <td style="font-weight:bold;">{composite_data.get('adjusted_yield_t_ha', 0):.3f} t/ha</td>
            <td style="text-align:right; font-weight:bold;">USD {composite_data.get('estimated_crop_value_usd', 0):,.2f}</td>
            <td style="font-weight:bold; color:#34d399; font-size:9pt;">{comp_ltv_str}</td>
            <td style="font-weight:bold;">{composite_data.get('insurance_premium_pct', 3.0):.2f}%</td>
            <td style="font-weight:bold;">100%</td>
        </tr>
        """

        ltv_section = f"""
        <div class="section">
          <h2>Financial Analysis (LTV) — Multi-Index Breakdown</h2>
          <div class="ltv-meta-info" style="margin-bottom: 8px; font-size: 7.5pt; color: #94a3b8;">
            <strong>Paramètres de base :</strong> Superficie: {data['ltv'].get('area_ha', 'N/A')} ha &nbsp;&middot;&nbsp; 
            Rendement cible: {data['ltv'].get('yield_t_per_ha', 'N/A')} t/ha &nbsp;&middot;&nbsp; 
            Prix du marché: USD {data['ltv'].get('price_per_t', 0):,.0f}/t &nbsp;&middot;&nbsp; 
            Montant du prêt: USD {data['ltv'].get('loan_amount_usd', 0) or 0:,.0f}
          </div>
          <table class="ltv-table">
            <thead>
              <tr>
                <th style="text-align:left">Satellite Index</th>
                <th>Current Value</th>
                <th>Prod. Factor</th>
                <th>Adj. Yield</th>
                <th style="text-align:right">Est. Crop Value</th>
                <th>LTV Ratio</th>
                <th>Insurance Prem.</th>
                <th>Weight</th>
              </tr>
            </thead>
            <tbody>
              {ltv_table_rows}
            </tbody>
          </table>
        </div>
        """

    no_charts_msg = ('<p style="color:#4b5563;font-size:8pt;padding:8px 0">'
                     'Charts unavailable — install matplotlib: pip install matplotlib</p>')

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<style>
  body{{font-family:'Helvetica Neue',sans-serif;font-size:9pt;color:#e2e8f0;margin:0;padding:0;background:#0f172a}}
  .header{{background:linear-gradient(135deg,#0f2b12,#1a5e2a);color:white;padding:22px 30px}}
  .header h1{{font-size:19pt;margin:0 0 3px}}
  .header p{{margin:0;opacity:.65;font-size:8pt}}
  .body{{padding:18px 30px;background:#0f172a}}
  .section{{margin-bottom:20px}}
  h2{{font-size:10.5pt;color:#34d399;border-bottom:1px solid #1e3a2a;padding-bottom:4px;margin-bottom:10px}}
  .idx-summary{{display:flex;align-items:center;gap:10px;background:#1e293b;
               border:1px solid #334155;border-radius:7px;padding:7px 11px;margin-bottom:5px}}
  .idx-icon{{font-size:13pt;width:22px;text-align:center}}
  .idx-name{{flex:1;font-size:8.5pt;color:#94a3b8;font-weight:600}}
  .idx-val{{font-size:12pt;font-weight:700;min-width:65px;text-align:right}}
  .idx-tier{{font-size:7pt;font-weight:700;padding:2px 7px;border-radius:20px;white-space:nowrap}}
  .chart-block{{margin-bottom:8px}}
  table{{width:100%;border-collapse:collapse;font-size:7pt;margin-bottom:10px}}
  thead tr{{background:#1e3a2a}}
  th{{color:#6ee7b7;padding:5px 5px;text-align:center;font-weight:700;
      letter-spacing:.3px;text-transform:uppercase;white-space:nowrap}}
  th:first-child{{text-align:left}}
  td{{padding:4px 5px;text-align:center;border-bottom:1px solid #1a2535}}
  td.qtr{{font-family:monospace;color:#94a3b8;text-align:left;white-space:nowrap}}
  .footer{{margin-top:20px;padding-top:7px;border-top:1px solid #1e293b;
           font-size:6.5pt;color:#4b5563;text-align:center}}
  @page{{size:A4;margin:0}}
</style></head><body>
<div class="header">
  <h1>&#128225; Satellite Index Report</h1>
  <p>{name} &nbsp;&middot;&nbsp; {period.get('from','')} &rarr; {period.get('to','')} &nbsp;&middot;&nbsp; Generated {now_str}</p>
</div>
<div class="body">
  <div class="section">
    <h2>Current Index Status</h2>
    {summaries}
  </div>
  
  {ltv_section}
  
  <div class="section">
    <h2>Historical Trends &amp; Forecast &mdash; NDVI &middot; NDMI &middot; EVI &middot; NMDI</h2>
    {chart_rows if chart_rows else no_charts_msg}
  </div>
  <div class="section">
    <h2>1-Year Forecast &mdash; All Indices</h2>
    <table><thead><tr><th>Quarter</th>{th}</tr></thead><tbody>{fc_body}</tbody></table>
  </div>
  <div class="section">
    <h2>Historical Data &mdash; 5 Years</h2>
    <table><thead><tr><th>Date</th>{th}</tr></thead><tbody>{hist_body}</tbody></table>
  </div>
  <div class="footer">
    NKUSU Farm Management &middot; Sentinel-2 L2A &middot; Statistical API &middot;
    Max cloud cover 30% &middot; Quarterly aggregation &middot; Prophet ML &middot; 80% confidence intervals
  </div>
</div></body></html>"""

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
        return jsonify({'error': f'Index "{index_name}" non supporté'}), 400

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
        return jsonify({'error': f'Index "{index_name}" non supporté'}), 400

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
        force_refresh  = bool(data.get('refresh', False)),
        hist_yield_1   = data.get('hist_yield_1'),
        hist_yield_2   = data.get('hist_yield_2'),
    ))
    if error:
        code = 400 if 'polygon' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200

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