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
    loan_amount    = request.args.get('loan_amount',    type=float)
    yield_t_per_ha = request.args.get('yield_t_per_ha', type=float, default=1.5)
    price_per_t    = request.args.get('price_per_t',    type=float, default=500)
    force_refresh  = request.args.get('refresh', '').lower() == 'true'

    result, error = get_sat_index_full(
        'farm', farm_id,
        loan_amount=loan_amount,
        yield_t_per_ha=yield_t_per_ha,
        price_per_t=price_per_t,
        force_refresh=force_refresh,
    )
    if error:
        code = 404 if 'not found' in error.lower() else 500
        return jsonify({'error': error}), code
    return jsonify(result), 200


@sentinel_bp.route('/forest/<int:forest_id>/sat-index', methods=['GET'])
@jwt_required()
def forest_sat_index(forest_id):
    from app.utils.sentinel_utils import get_sat_index_full
    result, error = get_sat_index_full('forest', forest_id)
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

    result, error = get_sat_index_full(
        'farm', farm_id,
        loan_amount=loan_amount,
        yield_t_per_ha=yield_t_per_ha,
        price_per_t=price_per_t,
    )
    if error:
        return jsonify({'error': error}), 500

    html_str = _build_pdf_html(result)

    try:
        from weasyprint import HTML
        # Générer le PDF directement en mémoire (évite les problèmes Windows)
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


def _build_pdf_html(data):
    """Génère le HTML du rapport PDF Sat-Index."""
    from datetime import datetime
    now_str = datetime.utcnow().strftime('%B %d, %Y')
    name    = data.get('name', 'N/A')
    period  = data.get('period', {})
    ltv     = data.get('ltv')
    history = data.get('history', [])
    forecast= data.get('forecast', {})

    # Dernières valeurs
    last = history[-1] if history else {}

    def index_card(idx_name, label, icon):
        val  = last.get(idx_name, {}).get('value')
        tier = last.get(idx_name, {}).get('tier', {})
        val_str  = f"{val:.4f}" if val is not None else 'N/A'
        tier_lbl = tier.get('label', 'N/A')
        color    = tier.get('color', '#9ca3af')
        fc = forecast.get(idx_name, [])
        fc_rows = ''.join(
            f"<tr><td>{q['quarter']}</td><td>{q['value']:.4f}</td>"
            f"<td style='color:{q['tier']['color']}'>{q['tier']['label']}</td></tr>"
            for q in fc
        )
        return f"""
        <div class="index-card">
          <div class="idx-header">
            <span class="idx-icon">{icon}</span>
            <span class="idx-name">{label}</span>
            <span class="idx-val" style="color:{color}">{val_str}</span>
            <span class="idx-tier" style="background:{color}22;color:{color}">{tier_lbl}</span>
          </div>
          <table class="fc-table">
            <tr><th>Quarter</th><th>Forecast</th><th>Tier</th></tr>
            {fc_rows}
          </table>
        </div>"""

    ltv_section = ''
    if ltv:
        ltv_section = f"""
        <div class="section">
          <h2>Financial Analysis</h2>
          <div class="ltv-grid">
            <div class="ltv-box"><p class="ltv-lbl">Area</p><p class="ltv-val">{ltv.get('area_ha','N/A')} ha</p></div>
            <div class="ltv-box"><p class="ltv-lbl">Adjusted Yield</p><p class="ltv-val">{ltv.get('adjusted_yield_t_ha','N/A')} t/ha</p></div>
            <div class="ltv-box"><p class="ltv-lbl">Est. Crop Value</p><p class="ltv-val">USD {ltv.get('estimated_crop_value_usd','N/A'):,.0f}</p></div>
            <div class="ltv-box"><p class="ltv-lbl">LTV Ratio</p><p class="ltv-val">{ltv.get('ltv_ratio_pct') or 'N/A'}{'%' if ltv.get('ltv_ratio_pct') else ''}</p></div>
            <div class="ltv-box"><p class="ltv-lbl">Insurance Premium</p><p class="ltv-val">{ltv.get('insurance_premium_pct','N/A')}%</p></div>
          </div>
        </div>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"/>
<style>
  body{{font-family:'Helvetica Neue',sans-serif;font-size:10pt;color:#1a2e1a;margin:0;padding:0}}
  .header{{background:linear-gradient(135deg,#0f2b12,#1a5e2a);color:white;padding:28px 36px}}
  .header h1{{font-size:22pt;margin:0 0 4px}}
  .header p{{margin:0;opacity:.7;font-size:9pt}}
  .body{{padding:24px 36px}}
  .section{{margin-bottom:24px}}
  h2{{font-size:13pt;color:#1a5e2a;border-bottom:2px solid #d0e8d0;padding-bottom:4px;margin-bottom:12px}}
  .index-card{{background:#f9fafb;border:1px solid #e5e7eb;border-radius:8px;padding:14px;margin-bottom:12px}}
  .idx-header{{display:flex;align-items:center;gap:10px;margin-bottom:10px}}
  .idx-icon{{font-size:18pt}}
  .idx-name{{font-weight:700;font-size:11pt;flex:1}}
  .idx-val{{font-size:16pt;font-weight:700}}
  .idx-tier{{font-size:8pt;font-weight:600;padding:2px 8px;border-radius:20px}}
  .fc-table{{width:100%;border-collapse:collapse;font-size:8.5pt}}
  .fc-table th{{background:#1a5e2a;color:white;padding:5px 8px;text-align:left}}
  .fc-table td{{padding:4px 8px;border-bottom:1px solid #e5e7eb}}
  .ltv-grid{{display:flex;gap:10px;flex-wrap:wrap}}
  .ltv-box{{flex:1;min-width:100px;background:#f0fdf4;border:1px solid #d0e8d0;border-radius:8px;padding:10px;text-align:center}}
  .ltv-lbl{{font-size:7.5pt;color:#5a8a5a;text-transform:uppercase;letter-spacing:.5px;margin:0 0 4px}}
  .ltv-val{{font-size:13pt;font-weight:700;color:#1a5e2a;margin:0}}
  .footer{{margin-top:30px;padding-top:10px;border-top:1px solid #d0e8d0;font-size:7pt;color:#9ca3af;text-align:center}}
  @page{{size:A4;margin:0}}
</style></head><body>
<div class="header">
  <h1>🛰️ Satellite Index Report</h1>
  <p>{name} &nbsp;·&nbsp; {period.get('from','')} → {period.get('to','')} &nbsp;·&nbsp; Generated {now_str}</p>
</div>
<div class="body">
  <div class="section">
    <h2>Spectral Indices — Current Status &amp; Forecast</h2>
    {index_card('ndvi','NDVI — Vegetation Health','🌱')}
    {index_card('savi','SAVI — Soil Adjusted Vegetation','🏜️')}
    {index_card('evi','EVI — Enhanced Vegetation','🌿')}
    {index_card('nmdi','NMDI — Drought Index','☀️')}
  </div>
  {ltv_section}
  <div class="footer">NKUSU Farm Management · Sentinel-2 L2A · Statistical API · 80% confidence intervals</div>
</div></body></html>"""