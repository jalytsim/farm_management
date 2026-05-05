"""
dashboard_utils.py — Utilitaires pour le tableau de bord administrateur.

Toutes les fonctions retournent des dictionnaires Python serialisables JSON.
"""

from sqlalchemy import func, and_, desc
from datetime import datetime, timedelta
from app import db
from app.models import (
    User, Farm, FarmData, Forest, Tree, District, Store, Product,
    FarmReport, ForestReport, Point, GFWLog, SMSLog, PaidFeatureAccess
)


# ─────────────────────────────────────────────
#  1. UTILISATEURS
# ─────────────────────────────────────────────

def count_users_by_type():
    """Nombre d'utilisateurs par user_type."""
    result = db.session.query(
        User.user_type,
        func.count(User.id)
    ).group_by(User.user_type).all()
    return {ut: c for ut, c in result}


# ─────────────────────────────────────────────
#  2. ENTITÉS — comptages globaux
# ─────────────────────────────────────────────

def count_all_entities():
    return {
        "farms":    Farm.query.count(),
        "forests":  Forest.query.count(),
        "trees":    Tree.query.count(),
        "farmdata": FarmData.query.count(),
        "stores":   Store.query.count(),
        "products": Product.query.count(),
    }


# ─────────────────────────────────────────────
#  3. ACREAGE DYNAMIQUE
# ─────────────────────────────────────────────

def _compute_area_ha_from_coords(coords):
    """
    Calcule la superficie en ha depuis une liste de (lon, lat).
    Retourne None si le calcul échoue.
    """
    try:
        from shapely.geometry import Polygon
        import pyproj
        from shapely.ops import transform as shapely_transform

        if len(coords) < 3:
            return None

        polygon = Polygon(coords)
        if not polygon.is_valid or polygon.is_empty:
            return None

        cx = polygon.centroid.x
        cy = polygon.centroid.y
        zone = int((cx + 180) / 6) + 1
        hemisphere = 'north' if cy >= 0 else 'south'
        epsg = 32600 + zone if hemisphere == 'north' else 32700 + zone

        proj_wgs84 = pyproj.CRS('EPSG:4326')
        proj_utm   = pyproj.CRS(f'EPSG:{epsg}')
        transformer = pyproj.Transformer.from_crs(
            proj_wgs84, proj_utm, always_xy=True
        )
        from shapely.ops import transform as shapely_transform
        projected = shapely_transform(transformer.transform, polygon)
        return round(projected.area / 10_000, 4)

    except Exception:
        return None


def _build_area_map_from_points():
    """
    Charge tous les Points 'farmer' en une seule requête,
    calcule la superficie de chaque ferme depuis son polygone.
    Retourne {farm_id(str): area_ha(float)}.
    """
    all_points = (
        Point.query
        .filter_by(owner_type='farmer')
        .order_by(Point.owner_id, Point.id)
        .all()
    )

    from collections import defaultdict
    groups = defaultdict(list)
    for p in all_points:
        groups[str(p.owner_id)].append((p.longitude, p.latitude))

    area_map = {}
    for owner_id, coords in groups.items():
        area_ha = _compute_area_ha_from_coords(coords)
        if area_ha is not None:
            area_map[owner_id] = area_ha

    return area_map


def _get_fallback_acreage_map():
    """
    Retourne {farm_id(str): tilled_land_size} pour les fermes
    sans polygone (dernière saison FarmData uniquement).
    """
    latest_sq = (
        db.session.query(
            FarmData.farm_id,
            func.max(FarmData.id).label('max_id')
        )
        .group_by(FarmData.farm_id)
        .subquery()
    )
    rows = (
        db.session.query(FarmData.farm_id, FarmData.tilled_land_size)
        .join(latest_sq, FarmData.id == latest_sq.c.max_id)
        .all()
    )
    return {farm_id: (tilled or 0.0) for farm_id, tilled in rows}


def get_farm_area_ha(farm_db_id, area_map, fallback_map, farm_farm_id):
    """
    Retourne (area_ha, source) :
      'gps'      → calculé depuis le polygone Points
      'declared' → tilled_land_size saisi manuellement
    """
    poly_area = area_map.get(str(farm_db_id))
    if poly_area is not None:
        return poly_area, 'gps'
    return round(float(fallback_map.get(farm_farm_id, 0.0)), 4), 'declared'


def get_total_acreage():
    """Superficie totale dynamique : GPS en priorité, tilled en fallback."""
    area_map     = _build_area_map_from_points()
    fallback_map = _get_fallback_acreage_map()

    farms = Farm.query.all()
    total = 0.0
    for farm in farms:
        area, _ = get_farm_area_ha(farm.id, area_map, fallback_map, farm.farm_id)
        total += area
    return round(total, 2)


def get_total_acreage_by_user(user_id):
    """Superficie totale pour un utilisateur donné."""
    area_map     = _build_area_map_from_points()
    fallback_map = _get_fallback_acreage_map()

    farms = Farm.query.filter_by(created_by=user_id).all()
    total = 0.0
    for farm in farms:
        area, _ = get_farm_area_ha(farm.id, area_map, fallback_map, farm.farm_id)
        total += area
    return round(total, 2)


# ─────────────────────────────────────────────
#  ★ NOUVEAU — AREA STATS POUR LE DASHBOARD
# ─────────────────────────────────────────────

def get_area_stats(user_id=None):
    """
    Retourne la décomposition complète des superficies pour le dashboard.

    user_id=None → admin : toutes les fermes / forêts
    user_id=X    → seulement les entités créées par cet utilisateur

    Champs retournés (tous en hectares) :
      farmer_area_ha      – total fermes (GPS + declared)
      farmer_gps_ha       – GPS polygons uniquement
      farmer_declared_ha  – tilled_land_size uniquement
      forest_area_ha      – polygones forêts
      gps_farm_count      – nombre de fermes avec polygone GPS
      forest_with_polygon – nombre de forêts avec polygone
      total_area_ha       – farmer + forest
    """
    area_map     = _build_area_map_from_points()
    fallback_map = _get_fallback_acreage_map()

    # ── Fermes ──────────────────────────────────────────────────
    farm_query = Farm.query
    if user_id:
        farm_query = farm_query.filter_by(created_by=user_id)
    farms = farm_query.all()

    farmer_gps_ha      = 0.0
    farmer_declared_ha = 0.0
    gps_farm_count     = 0

    for farm in farms:
        area, source = get_farm_area_ha(farm.id, area_map, fallback_map, farm.farm_id)
        if source == 'gps':
            farmer_gps_ha  += area
            gps_farm_count += 1
        else:
            farmer_declared_ha += area

    farmer_area_ha = farmer_gps_ha + farmer_declared_ha

    # ── Forêts ──────────────────────────────────────────────────
    forest_area_ha      = 0.0
    forest_with_polygon = 0

    try:
        from shapely.geometry import Polygon
        import pyproj
        from shapely.ops import transform as shapely_transform
        shapely_ok = True
    except ImportError:
        shapely_ok = False

    forest_query = Forest.query
    if user_id:
        forest_query = forest_query.filter_by(created_by=user_id)
    forests = forest_query.all()

    for forest in forests:
        if not shapely_ok:
            break
        points = (
            Point.query
            .filter_by(owner_type='forest', owner_id=str(forest.id))
            .order_by(Point.id)
            .all()
        )
        if len(points) < 3:
            continue
        try:
            coords  = [(p.longitude, p.latitude) for p in points]
            polygon = Polygon(coords)
            if not polygon.is_valid:
                continue
            # UTM auto-zone
            cx   = polygon.centroid.x
            cy   = polygon.centroid.y
            zone = int((cx + 180) / 6) + 1
            hemi = 'north' if cy >= 0 else 'south'
            epsg = 32600 + zone if hemi == 'north' else 32700 + zone
            transformer = pyproj.Transformer.from_crs(
                pyproj.CRS('EPSG:4326'), pyproj.CRS(f'EPSG:{epsg}'), always_xy=True
            )
            projected = shapely_transform(transformer.transform, polygon)
            ha = round(projected.area / 10_000, 4)
            forest_area_ha      += ha
            forest_with_polygon += 1
        except Exception:
            continue

    return {
        'farmer_area_ha':      round(farmer_area_ha, 4),
        'farmer_gps_ha':       round(farmer_gps_ha, 4),
        'farmer_declared_ha':  round(farmer_declared_ha, 4),
        'forest_area_ha':      round(forest_area_ha, 4),
        'gps_farm_count':      gps_farm_count,
        'forest_with_polygon': forest_with_polygon,
        'total_area_ha':       round(farmer_area_ha + forest_area_ha, 4),
    }


# ─────────────────────────────────────────────
#  4. FARMERS PAR COMPTE
# ─────────────────────────────────────────────

def get_farmers_per_account():
    rows = (
        db.session.query(
            User.id,
            User.username,
            User.company_name,
            User.user_type,
            func.count(Farm.id).label('farm_count')
        )
        .outerjoin(Farm, Farm.created_by == User.id)
        .group_by(User.id)
        .order_by(desc('farm_count'))
        .all()
    )

    area_map     = _build_area_map_from_points()
    fallback_map = _get_fallback_acreage_map()

    user_farms = {}
    for farm in Farm.query.all():
        uid = farm.created_by
        if uid not in user_farms:
            user_farms[uid] = []
        user_farms[uid].append(farm)

    result = []
    for user_id, username, company, user_type, farm_count in rows:
        farms_for_user = user_farms.get(user_id, [])
        acreage   = 0.0
        gps_count = 0
        for f in farms_for_user:
            area, source = get_farm_area_ha(f.id, area_map, fallback_map, f.farm_id)
            acreage += area
            if source == 'gps':
                gps_count += 1
        result.append({
            "user_id":    user_id,
            "username":   username,
            "company":    company or username,
            "user_type":  user_type,
            "farm_count": farm_count,
            "acreage_ha": round(acreage, 2),
            "gps_farms":  gps_count,
        })
    return result


# ─────────────────────────────────────────────
#  5. COMPLIANCE PAR COMPTE
# ─────────────────────────────────────────────

def get_compliance_farmers_per_account():
    rows = (
        db.session.query(
            User.id,
            User.username,
            User.company_name,
            func.count(Farm.id).label('total'),
            func.sum(
                db.case(
                    (FarmReport.eudr_compliance_assessment.ilike('%compliant%'), 1),
                    else_=0
                )
            ).label('compliant')
        )
        .outerjoin(Farm,       Farm.created_by == User.id)
        .outerjoin(FarmReport, FarmReport.farm_id == Farm.id)
        .group_by(User.id)
        .order_by(desc('total'))
        .all()
    )

    result = []
    for uid, uname, company, total, compliant in rows:
        compliant = int(compliant or 0)
        total     = int(total     or 0)
        result.append({
            "user_id":       uid,
            "username":      uname,
            "company":       company or uname,
            "total_farms":   total,
            "compliant":     compliant,
            "not_compliant": total - compliant,
            "rate_pct":      round(compliant / total * 100, 1) if total else 0,
        })
    return result


# ─────────────────────────────────────────────
#  6. FARMERS PAR PAYS + RÉGION
# ─────────────────────────────────────────────

def get_farmers_per_country_and_region():
    by_country_rows = (
        db.session.query(
            func.coalesce(Farm.country, 'Unknown').label('country'),
            func.count(Farm.id).label('count')
        )
        .group_by('country')
        .order_by(desc('count'))
        .all()
    )
    by_country = {row.country: row.count for row in by_country_rows}

    by_region_rows = (
        db.session.query(
            func.coalesce(District.region, 'Unknown').label('region'),
            func.count(Farm.id).label('count')
        )
        .outerjoin(District, Farm.district_id == District.id)
        .group_by('region')
        .order_by(desc('count'))
        .all()
    )
    by_region = {row.region: row.count for row in by_region_rows}

    return {"by_country": by_country, "by_region": by_region}


# ─────────────────────────────────────────────
#  7. FORESTS PAR PAYS
# ─────────────────────────────────────────────

def get_forests_per_country():
    rows = (
        db.session.query(
            func.coalesce(Forest.country, 'Unknown').label('country'),
            func.count(Forest.id).label('count')
        )
        .group_by('country')
        .order_by(desc('count'))
        .all()
    )
    return {row.country: row.count for row in rows}


# ─────────────────────────────────────────────
#  8. RÉSUMÉ DES MAGASINS
# ─────────────────────────────────────────────

def get_store_summaries():
    stores = Store.query.order_by(desc(Store.revenue)).all()
    return [
        {
            "id":              s.id,
            "name":            s.name,
            "country":         s.country,
            "district":        s.district,
            "store_type":      s.store_type,
            "status":          "Active" if s.status else "Inactive",
            "inventory_count": s.inventory_count,
            "sales_count":     s.sales_count,
            "revenue":         round(s.revenue or 0, 2),
        }
        for s in stores
    ]


# ─────────────────────────────────────────────
#  9. STATISTIQUES GFW
# ─────────────────────────────────────────────

def get_gfw_stats():
    total_views = GFWLog.query.filter_by(action_type='page_view').count()
    total_pdf   = GFWLog.query.filter_by(action_type='pdf_download').count()
    total_cert  = GFWLog.query.filter_by(action_type='certificate_generated').count()

    now         = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    monthly_views = GFWLog.query.filter(
        GFWLog.action_type == 'page_view',
        GFWLog.created_at  >= month_start
    ).count()

    monthly_pdf = GFWLog.query.filter(
        GFWLog.action_type == 'pdf_download',
        GFWLog.created_at  >= month_start
    ).count()

    return {
        "total_page_views":      total_views,
        "total_pdf_downloads":   total_pdf,
        "total_certificates":    total_cert,
        "monthly_page_views":    monthly_views,
        "monthly_pdf_downloads": monthly_pdf,
        "total_sessions":        total_views + total_pdf,
    }


# ─────────────────────────────────────────────
#  10. STATISTIQUES SMS
# ─────────────────────────────────────────────

def get_sms_stats():
    total      = SMSLog.query.count()
    successful = SMSLog.query.filter_by(status='success').count()
    failed     = SMSLog.query.filter_by(status='failed').count()

    now         = datetime.utcnow()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    monthly     = SMSLog.query.filter(SMSLog.created_at >= month_start).count()

    return {
        "total_sent":       total,
        "successful":       successful,
        "failed":           failed,
        "this_month":       monthly,
        "success_rate_pct": round(successful / total * 100, 1) if total else 0,
    }


# ─────────────────────────────────────────────
#  11. STATS FORÊT / ARBRES
# ─────────────────────────────────────────────

def get_forest_tree_stats(user_id=None):
    try:
        from shapely.geometry import Polygon
        import pyproj
        from shapely.ops import transform as shapely_transform
        shapely_available = True
    except ImportError:
        shapely_available = False

    q = Forest.query
    if user_id:
        q = q.filter(Forest.created_by == user_id)
    forests = q.all()

    result = []
    for forest in forests:
        tree_count = Tree.query.filter_by(forest_id=forest.id).count()
        area_ha    = None

        if shapely_available:
            points = (
                Point.query
                .filter_by(owner_type='forest', owner_id=str(forest.id))
                .order_by(Point.id)
                .all()
            )
            if len(points) >= 3:
                try:
                    coords  = [(p.longitude, p.latitude) for p in points]
                    polygon = Polygon(coords)
                    if polygon.is_valid:
                        proj_in  = pyproj.CRS('EPSG:4326')
                        proj_out = pyproj.CRS('EPSG:32636')
                        transformer = pyproj.Transformer.from_crs(
                            proj_in, proj_out, always_xy=True
                        )
                        projected = shapely_transform(transformer.transform, polygon)
                        area_ha = round(projected.area / 10_000, 4)
                except Exception:
                    area_ha = None

        result.append({
            "forest_id":   forest.id,
            "forest_name": forest.name,
            "tree_type":   forest.tree_type,
            "country":     getattr(forest, 'country', None),
            "tree_count":  tree_count,
            "area_ha":     area_ha,
            "created_by":  forest.created_by,
        })

    return result


# ─────────────────────────────────────────────
#  12. STATS COMPLÈTES (Admin full)
# ─────────────────────────────────────────────

def get_admin_full_stats():
    return {
        "users_by_type":              count_users_by_type(),
        "entities":                   count_all_entities(),
        "total_acreage_ha":           get_total_acreage(),
        "farmers_per_account":        get_farmers_per_account(),
        "compliance_per_account":     get_compliance_farmers_per_account(),
        "farmers_per_country_region": get_farmers_per_country_and_region(),
        "forests_per_country":        get_forests_per_country(),
        "store_summaries":            get_store_summaries(),
        "gfw_stats":                  get_gfw_stats(),
        "sms_stats":                  get_sms_stats(),
        "forest_tree_stats":          get_forest_tree_stats(),
    }


# ─────────────────────────────────────────────
#  ANCIENS HELPERS conservés
# ─────────────────────────────────────────────

def get_user_activity(user_id=None):
    from flask_login import current_user
    uid = user_id or current_user.id
    activity = {}
    for model in [FarmData, Farm, Forest, Tree, District, Store, Product]:
        activity[model.__tablename__] = {
            "created": db.session.query(model).filter_by(created_by=uid).count(),
            "updated": db.session.query(model).filter_by(modified_by=uid).count(),
        }
    return activity


def get_latest_updates(model, limit=10):
    return model.query.order_by(model.date_updated.desc()).limit(limit).all()