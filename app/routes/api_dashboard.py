"""
api_dashboard.py — Blueprint /api/dashboard

Endpoints :
  GET  /api/dashboard/users/by-type          (existant)
  GET  /api/dashboard/user/<id>/activity     (existant)
  GET  /api/dashboard/entities/count         (existant)
  GET  /api/dashboard/latest-updates/<model> (existant)
  GET  /api/dashboard/area-stats             ★ NOUVEAU — superficies fermes + forêts
  GET  /api/dashboard/admin/full             ★ NOUVEAU — toutes les métriques
  GET  /api/dashboard/admin/export/csv       ★ NOUVEAU — export CSV
  GET  /api/dashboard/admin/export/pdf       ★ NOUVEAU — export PDF pro (WeasyPrint)
  POST /api/dashboard/gfw/log               ★ NOUVEAU — log visite GFW
  GET  /api/dashboard/forest/tree-stats      ★ NOUVEAU — forêt : arbres + superficie
"""

import csv
import io
import tempfile
from datetime import datetime

from flask import Blueprint, Response, jsonify, request, send_file
from flask_jwt_extended import get_jwt_identity, jwt_required

from app import db
from app.models import (District, Farm, FarmData, Forest, GFWLog, Product,
                        SMSLog, Store, Tree, User)
from app.utils.dashboard_utils import (count_all_entities, count_users_by_type,
                                       get_admin_full_stats, get_area_stats,
                                       get_forest_tree_stats, get_gfw_stats,
                                       get_latest_updates)

dashboard_api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')


# ══════════════════════════════════════════════
#  ENDPOINTS EXISTANTS (conservés / enrichis)
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/users/by-type', methods=['GET'])
@jwt_required()
def users_by_type():
    return jsonify(count_users_by_type())


@dashboard_api_bp.route('/user/<int:user_id>/activity', methods=['GET'])
@jwt_required()
def user_activity(user_id):
    models = [FarmData, Farm, Forest, District, Store, Product]
    activity = {}
    for model in models:
        activity[model.__tablename__] = {
            "created": db.session.query(model).filter_by(created_by=user_id).count(),
            "updated": db.session.query(model).filter_by(modified_by=user_id).count(),
        }
    return jsonify(activity)


@dashboard_api_bp.route('/entities/count', methods=['GET'])
@jwt_required()
def count_all():
    return jsonify(count_all_entities())


@dashboard_api_bp.route('/latest-updates/<string:model_name>', methods=['GET'])
@jwt_required()
def latest_updates(model_name):
    limit = int(request.args.get('limit', 10))
    model_map = {
        'farm': Farm, 'forest': Forest, 'farmdata': FarmData,
        'store': Store, 'product': Product, 'district': District,
    }
    model = model_map.get(model_name.lower())
    if not model:
        return jsonify({'error': f'Model {model_name} not found'}), 404
    records = model.query.order_by(model.date_updated.desc()).limit(limit).all()
    return jsonify([
        {col.name: getattr(r, col.name) for col in model.__table__.columns}
        for r in records
    ])


# ══════════════════════════════════════════════
#  ★ NOUVEAU — AREA STATS (widget Coverage)
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/area-stats', methods=['GET'])
@jwt_required()
def area_stats():
    """
    Retourne les statistiques de superficie pour le widget Coverage du dashboard.

    Réponse JSON :
    {
      farmer_area_ha,      # total fermes (GPS + declared)
      farmer_gps_ha,       # GPS polygons seulement
      farmer_declared_ha,  # tilled_land_size seulement
      forest_area_ha,      # polygones forêts
      gps_farm_count,      # fermes avec polygone GPS
      forest_with_polygon, # forêts avec polygone
      total_area_ha,       # farmer + forest
    }

    Admin → toutes les entités.
    Non-admin → seulement ses propres fermes/forêts.
    """
    identity = get_jwt_identity()
    user_id  = identity['id'] if isinstance(identity, dict) else identity
    user     = User.query.get(user_id)

    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Admin sans filtre → toutes les entités
    target_user_id = None if user.is_admin else user_id

    return jsonify(get_area_stats(user_id=target_user_id))


# ══════════════════════════════════════════════
#  NOUVEAU — ADMIN : TOUTES LES MÉTRIQUES
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/admin/full', methods=['GET'])
@jwt_required()
def admin_full():
    """Retourne toutes les métriques admin en un seul appel."""
    identity = get_jwt_identity()
    user = User.query.get(identity['id'] if isinstance(identity, dict) else identity)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin only'}), 403

    return jsonify(get_admin_full_stats())


# ══════════════════════════════════════════════
#  NOUVEAU — ADMIN : EXPORT CSV
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/admin/export/csv', methods=['GET'])
@jwt_required()
def export_csv():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'] if isinstance(identity, dict) else identity)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin only'}), 403

    stats = get_admin_full_stats()
    output = io.StringIO()

    # ── Section 1 : Résumé global ──
    _write_section(output, "GLOBAL SUMMARY")
    w = csv.writer(output)
    w.writerow(["Metric", "Value"])
    entities = stats['entities']
    w.writerow(["Total Users",    sum(stats['users_by_type'].values())])
    w.writerow(["Total Farms",    entities.get('farms', 0)])
    w.writerow(["Total Forests",  entities.get('forests', 0)])
    w.writerow(["Total Trees",    entities.get('trees', 0)])
    w.writerow(["Total Acreage (ha)", stats['total_acreage_ha']])
    w.writerow([])

    # ── Section 2 : Utilisateurs par type ──
    _write_section(output, "USERS BY TYPE")
    w.writerow(["User Type", "Count"])
    for k, v in stats['users_by_type'].items():
        w.writerow([k, v])
    w.writerow([])

    # ── Section 3 : Farmers par compte ──
    _write_section(output, "FARMERS PER ACCOUNT")
    w.writerow(["Username", "Company", "User Type", "Farm Count", "Acreage (ha)"])
    for row in stats['farmers_per_account']:
        w.writerow([
            row['username'], row['company'], row['user_type'],
            row['farm_count'], row['acreage_ha']
        ])
    w.writerow([])

    # ── Section 4 : Compliance par compte ──
    _write_section(output, "COMPLIANCE FARMERS PER ACCOUNT")
    w.writerow(["Username", "Total Farms", "Compliant", "Not Compliant", "Rate %"])
    for row in stats['compliance_per_account']:
        w.writerow([
            row['username'], row['total_farms'],
            row['compliant'], row['not_compliant'], row['rate_pct']
        ])
    w.writerow([])

    # ── Section 5 : Farmers par pays / région ──
    _write_section(output, "FARMERS BY COUNTRY")
    w.writerow(["Country", "Count"])
    for k, v in stats['farmers_per_country_region']['by_country'].items():
        w.writerow([k, v])
    w.writerow([])

    _write_section(output, "FARMERS BY REGION")
    w.writerow(["Region", "Count"])
    for k, v in stats['farmers_per_country_region']['by_region'].items():
        w.writerow([k, v])
    w.writerow([])

    # ── Section 6 : Forêts par pays ──
    _write_section(output, "FORESTS BY COUNTRY")
    w.writerow(["Country", "Count"])
    for k, v in stats['forests_per_country'].items():
        w.writerow([k, v])
    w.writerow([])

    # ── Section 7 : Stores ──
    _write_section(output, "STORE SUMMARIES")
    w.writerow(["Name", "Country", "District", "Type", "Status",
                "Inventory", "Sales", "Revenue"])
    for s in stats['store_summaries']:
        w.writerow([
            s['name'], s['country'], s['district'], s['store_type'], s['status'],
            s['inventory_count'], s['sales_count'], s['revenue']
        ])
    w.writerow([])

    # ── Section 8 : GFW + SMS ──
    _write_section(output, "GFW STATISTICS")
    w.writerow(["Metric", "Value"])
    for k, v in stats['gfw_stats'].items():
        w.writerow([k.replace('_', ' ').title(), v])
    w.writerow([])

    _write_section(output, "SMS STATISTICS")
    w.writerow(["Metric", "Value"])
    for k, v in stats['sms_stats'].items():
        w.writerow([k.replace('_', ' ').title(), v])
    w.writerow([])

    # ── Section 9 : Forest / Tree stats ──
    _write_section(output, "FOREST & TREE STATISTICS")
    w.writerow(["Forest Name", "Tree Type", "Country", "Tree Count", "Area (ha)"])
    for row in stats['forest_tree_stats']:
        w.writerow([
            row['forest_name'], row['tree_type'],
            row['country'] or 'N/A', row['tree_count'],
            row['area_ha'] if row['area_ha'] is not None else 'N/A'
        ])

    filename = f"admin_dashboard_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename={filename}'}
    )


def _write_section(output, title):
    """Ajoute un en-tête de section dans le CSV."""
    w = csv.writer(output)
    w.writerow([f"### {title} ###"])


# ══════════════════════════════════════════════
#  NOUVEAU — ADMIN : EXPORT PDF (WeasyPrint)
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/admin/export/pdf', methods=['GET'])
@jwt_required()
def export_pdf():
    identity = get_jwt_identity()
    user = User.query.get(identity['id'] if isinstance(identity, dict) else identity)
    if not user or not user.is_admin:
        return jsonify({'error': 'Admin only'}), 403

    stats    = get_admin_full_stats()
    html_str = _build_pdf_html(stats, user.username)

    try:
        from weasyprint import HTML
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
            HTML(string=html_str).write_pdf(f.name)
            filename = f"admin_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.pdf"
            return send_file(
                f.name,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=filename
            )
    except Exception as e:
        return jsonify({'error': f'PDF generation failed: {str(e)}'}), 500


def _build_pdf_html(stats, generated_by):
    """Génère le HTML complet pour WeasyPrint → PDF professionnel."""

    entities = stats['entities']
    gfw      = stats['gfw_stats']
    sms      = stats['sms_stats']
    now_str  = datetime.utcnow().strftime('%B %d, %Y at %H:%M UTC')

    # ── Tableau helpers ──
    def kv_rows(d):
        return ''.join(
            f'<tr><td class="label">{k.replace("_", " ").title()}</td>'
            f'<td class="value">{v}</td></tr>'
            for k, v in d.items()
        )

    # ── Farmers per account table ──
    farmer_rows = ''.join(
        f'''<tr>
            <td>{r["username"]}</td>
            <td>{r["company"]}</td>
            <td><span class="badge">{r["user_type"]}</span></td>
            <td class="num">{r["farm_count"]}</td>
            <td class="num">{r["acreage_ha"]} ha</td>
        </tr>'''
        for r in stats['farmers_per_account'][:20]
    )

    # ── Compliance table ──
    compliance_rows = ''.join(
        f'''<tr>
            <td>{r["username"]}</td>
            <td class="num">{r["total_farms"]}</td>
            <td class="num compliant">{r["compliant"]}</td>
            <td class="num danger">{r["not_compliant"]}</td>
            <td class="num">{r["rate_pct"]}%</td>
        </tr>'''
        for r in stats['compliance_per_account'][:20]
    )

    # ── Store table ──
    store_rows = ''.join(
        f'''<tr>
            <td>{s["name"]}</td>
            <td>{s["country"]}</td>
            <td class="num">{s["inventory_count"]}</td>
            <td class="num">{s["sales_count"]}</td>
            <td class="num revenue">{s["revenue"]:,.0f}</td>
            <td><span class="badge {'active' if s['status']=='Active' else 'inactive'}">{s["status"]}</span></td>
        </tr>'''
        for s in stats['store_summaries'][:15]
    )

    # ── Forest / tree table ──
    forest_rows = ''.join(
        f'''<tr>
            <td>{r["forest_name"]}</td>
            <td>{r["tree_type"]}</td>
            <td>{r.get("country") or "N/A"}</td>
            <td class="num">{r["tree_count"]}</td>
            <td class="num">{f'{r["area_ha"]} ha' if r["area_ha"] is not None else "N/A"}</td>
        </tr>'''
        for r in stats['forest_tree_stats'][:20]
    )

    # ── Country distribution ──
    country_rows = ''.join(
        f'<tr><td>{c}</td><td class="num">{n}</td></tr>'
        for c, n in stats['farmers_per_country_region']['by_country'].items()
    )
    region_rows = ''.join(
        f'<tr><td>{r}</td><td class="num">{n}</td></tr>'
        for r, n in stats['farmers_per_country_region']['by_region'].items()
    )

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>Admin Dashboard Report</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Source+Sans+3:wght@300;400;600&display=swap');

  * {{ box-sizing: border-box; margin: 0; padding: 0; }}

  body {{
    font-family: 'Source Sans 3', sans-serif;
    font-weight: 400;
    font-size: 10pt;
    color: #1a2e1a;
    background: #fff;
  }}

  /* ── HEADER ── */
  .header {{
    background: linear-gradient(135deg, #1a5e2a 0%, #2d8a45 60%, #3aad5a 100%);
    color: white;
    padding: 32px 40px 24px;
    position: relative;
    overflow: hidden;
  }}
  .header::after {{
    content: '';
    position: absolute;
    bottom: -20px; right: -20px;
    width: 160px; height: 160px;
    border-radius: 50%;
    background: rgba(255,255,255,0.06);
  }}
  .header-logo {{
    font-family: 'Playfair Display', serif;
    font-size: 28pt;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
  }}
  .header-subtitle {{
    font-size: 11pt;
    font-weight: 300;
    opacity: 0.85;
    letter-spacing: 0.5px;
    text-transform: uppercase;
  }}
  .header-meta {{
    margin-top: 16px;
    font-size: 8.5pt;
    opacity: 0.7;
    border-top: 1px solid rgba(255,255,255,0.2);
    padding-top: 12px;
  }}

  /* ── KPI CARDS ── */
  .kpi-grid {{
    display: flex;
    gap: 0;
    border-bottom: 2px solid #e8f0e9;
    margin-bottom: 28px;
  }}
  .kpi-card {{
    flex: 1;
    padding: 20px 16px;
    border-right: 1px solid #e8f0e9;
    text-align: center;
  }}
  .kpi-card:last-child {{ border-right: none; }}
  .kpi-label {{
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #5a8a5a;
    margin-bottom: 6px;
    font-weight: 600;
  }}
  .kpi-value {{
    font-family: 'Playfair Display', serif;
    font-size: 22pt;
    color: #1a5e2a;
    line-height: 1;
  }}

  /* ── BODY AREA ── */
  .body {{ padding: 28px 40px 40px; }}

  /* ── SECTION ── */
  .section {{ margin-bottom: 32px; page-break-inside: avoid; }}
  .section-title {{
    font-family: 'Playfair Display', serif;
    font-size: 14pt;
    color: #1a5e2a;
    border-bottom: 2px solid #2d8a45;
    padding-bottom: 6px;
    margin-bottom: 14px;
  }}

  /* ── TABLES ── */
  table {{ width: 100%; border-collapse: collapse; font-size: 8.5pt; }}
  th {{
    background: #1a5e2a;
    color: white;
    padding: 7px 10px;
    text-align: left;
    font-weight: 600;
    font-size: 7.5pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }}
  td {{
    padding: 6px 10px;
    border-bottom: 1px solid #e8f0e9;
  }}
  tr:nth-child(even) td {{ background: #f4faf5; }}
  td.num   {{ text-align: right; font-weight: 600; }}
  td.label {{ color: #4a7a4a; font-weight: 600; }}
  td.value {{ font-weight: 400; }}
  td.compliant {{ color: #1a7a2a; }}
  td.danger    {{ color: #c0392b; }}
  td.revenue   {{ color: #1a5e2a; font-weight: 700; }}

  /* ── BADGES ── */
  .badge {{
    display: inline-block;
    padding: 2px 8px;
    border-radius: 20px;
    font-size: 7.5pt;
    font-weight: 600;
    text-transform: uppercase;
    background: #e8f5e9;
    color: #2d8a45;
  }}
  .badge.active   {{ background: #e8f5e9; color: #1a7a2a; }}
  .badge.inactive {{ background: #fdecea; color: #c0392b; }}

  /* ── TWO COLUMN ── */
  .two-col {{ display: flex; gap: 24px; }}
  .two-col .col {{ flex: 1; }}

  /* ── STAT ROW (GFW / SMS) ── */
  .stat-grid {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .stat-box {{
    flex: 1;
    min-width: 100px;
    background: #f4faf5;
    border: 1px solid #d0e8d0;
    border-radius: 6px;
    padding: 12px;
    text-align: center;
  }}
  .stat-box .s-label {{
    font-size: 7pt;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #5a8a5a;
    margin-bottom: 4px;
  }}
  .stat-box .s-val {{
    font-family: 'Playfair Display', serif;
    font-size: 16pt;
    color: #1a5e2a;
    line-height: 1.1;
  }}

  /* ── FOOTER ── */
  .footer {{
    margin-top: 40px;
    padding-top: 12px;
    border-top: 1px solid #d0e8d0;
    font-size: 7.5pt;
    color: #8aaa8a;
    text-align: center;
  }}

  @page {{
    size: A4;
    margin: 0;
    @bottom-center {{
      content: "Page " counter(page) " of " counter(pages);
      font-family: 'Source Sans 3', sans-serif;
      font-size: 7pt;
      color: #8aaa8a;
    }}
  }}

  .page-break {{ page-break-before: always; }}
</style>
</head>
<body>

<!-- ══ HEADER ══ -->
<div class="header">
  <div class="header-logo">NKUSU</div>
  <div class="header-subtitle">Farm Management System — Admin Dashboard Report</div>
  <div class="header-meta">
    Generated on {now_str} &nbsp;·&nbsp; Generated by <strong>{generated_by}</strong>
  </div>
</div>

<!-- ══ KPI CARDS ══ -->
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">Total Users</div>
    <div class="kpi-value">{sum(stats['users_by_type'].values())}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Farms</div>
    <div class="kpi-value">{entities.get('farms', 0)}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Forests</div>
    <div class="kpi-value">{entities.get('forests', 0)}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Trees</div>
    <div class="kpi-value">{entities.get('trees', 0)}</div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">Total Acreage</div>
    <div class="kpi-value">{stats['total_acreage_ha']}<span style="font-size:10pt"> ha</span></div>
  </div>
</div>

<!-- ══ BODY ══ -->
<div class="body">

  <!-- Farmers per account -->
  <div class="section">
    <div class="section-title">Farmers per Account</div>
    <table>
      <thead>
        <tr>
          <th>Username</th><th>Company / Name</th><th>Type</th>
          <th>Farms</th><th>Acreage (ha)</th>
        </tr>
      </thead>
      <tbody>{farmer_rows}</tbody>
    </table>
  </div>

  <!-- Compliance -->
  <div class="section">
    <div class="section-title">EUDR Compliance per Account</div>
    <table>
      <thead>
        <tr>
          <th>Username</th><th>Total Farms</th><th>Compliant</th>
          <th>Not Compliant</th><th>Rate</th>
        </tr>
      </thead>
      <tbody>{compliance_rows}</tbody>
    </table>
  </div>

  <!-- Country / Region -->
  <div class="section two-col">
    <div class="col">
      <div class="section-title">Farmers by Country</div>
      <table>
        <thead><tr><th>Country</th><th>Farms</th></tr></thead>
        <tbody>{country_rows}</tbody>
      </table>
    </div>
    <div class="col">
      <div class="section-title">Farmers by Region</div>
      <table>
        <thead><tr><th>Region</th><th>Farms</th></tr></thead>
        <tbody>{region_rows}</tbody>
      </table>
    </div>
  </div>

  <!-- GFW + SMS -->
  <div class="section">
    <div class="section-title">GFW Activity</div>
    <div class="stat-grid">
      <div class="stat-box">
        <div class="s-label">Page Views</div>
        <div class="s-val">{gfw.get('total_page_views', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">PDF Downloads</div>
        <div class="s-val">{gfw.get('total_pdf_downloads', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">Certificates</div>
        <div class="s-val">{gfw.get('total_certificates', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">Sessions (Total)</div>
        <div class="s-val">{gfw.get('total_sessions', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">This Month</div>
        <div class="s-val">{gfw.get('monthly_page_views', 0)}</div>
      </div>
    </div>
  </div>

  <div class="section">
    <div class="section-title">SMS Statistics</div>
    <div class="stat-grid">
      <div class="stat-box">
        <div class="s-label">Total Sent</div>
        <div class="s-val">{sms.get('total_sent', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">Successful</div>
        <div class="s-val">{sms.get('successful', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">Failed</div>
        <div class="s-val">{sms.get('failed', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">This Month</div>
        <div class="s-val">{sms.get('this_month', 0)}</div>
      </div>
      <div class="stat-box">
        <div class="s-label">Success Rate</div>
        <div class="s-val">{sms.get('success_rate_pct', 0)}%</div>
      </div>
    </div>
  </div>

  <!-- Stores -->
  <div class="section page-break">
    <div class="section-title">Store Summaries</div>
    <table>
      <thead>
        <tr>
          <th>Store Name</th><th>Country</th><th>Inventory</th>
          <th>Sales</th><th>Revenue</th><th>Status</th>
        </tr>
      </thead>
      <tbody>{store_rows}</tbody>
    </table>
  </div>

  <!-- Forest / Tree -->
  <div class="section">
    <div class="section-title">Forest &amp; Tree Statistics</div>
    <table>
      <thead>
        <tr>
          <th>Forest Name</th><th>Tree Type</th><th>Country</th>
          <th>Trees</th><th>Area</th>
        </tr>
      </thead>
      <tbody>{forest_rows}</tbody>
    </table>
  </div>

  <div class="footer">
    NKUSU Farm Management System &nbsp;·&nbsp;
    Confidential — Admin use only &nbsp;·&nbsp;
    {now_str}
  </div>

</div>
</body>
</html>"""

    return html


# ══════════════════════════════════════════════
#  NOUVEAU — LOG GFW SESSION
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/gfw/log', methods=['POST'])
def log_gfw_event():
    """
    Enregistre une action GFW (visite page / téléchargement PDF / certificat).
    Appelé automatiquement par le frontend sur mount et on génération PDF.
    Authentification optionnelle (fonctionne aussi pour les guests).
    """
    data        = request.get_json() or {}
    action_type = data.get('action_type', 'page_view')   # page_view | pdf_download | certificate_generated
    entity_type = data.get('entity_type')                 # farm | forest
    entity_id   = data.get('entity_id')

    # Récupérer l'utilisateur si token présent
    user_id = None
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
        if identity:
            user_id = identity['id'] if isinstance(identity, dict) else identity
    except Exception:
        pass

    log = GFWLog(
        user_id     = user_id,
        action_type = action_type,
        entity_type = entity_type,
        entity_id   = str(entity_id) if entity_id else None,
        ip_address  = request.remote_addr,
        user_agent  = request.headers.get('User-Agent', '')[:255],
    )
    db.session.add(log)
    db.session.commit()
    return jsonify({'logged': True}), 201


# ══════════════════════════════════════════════
#  NOUVEAU — STATS FORÊT / ARBRES
# ══════════════════════════════════════════════

@dashboard_api_bp.route('/forest/tree-stats', methods=['GET'])
@jwt_required()
def forest_tree_stats():
    identity = get_jwt_identity()
    uid = identity['id'] if isinstance(identity, dict) else identity
    user = User.query.get(uid)
    if not user:
        return jsonify({'error': 'User not found'}), 404

    # Admin voit tout, les autres voient leurs propres forêts
    user_filter = None if user.is_admin else uid
    return jsonify(get_forest_tree_stats(user_id=user_filter))