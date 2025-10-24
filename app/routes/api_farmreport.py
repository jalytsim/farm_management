from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import db, FarmReport
import base64

api_farmreport_bp = Blueprint('api_farmreport', __name__, url_prefix='/api/farmreport')


# 🟢 Récupérer tous les rapports
@api_farmreport_bp.route('/', methods=['GET'])
def index():
    reports = FarmReport.query.all()
    reports_list = []
    for report in reports:
        reports_list.append({
            "id": report.id,
            "farm_id": report.farm_id,
            "project_area": report.project_area,
            "country_deforestation_risk_level": report.country_deforestation_risk_level,
            "radd_alert": report.radd_alert,
            "tree_cover_loss": report.tree_cover_loss,
            "forest_cover_2020": report.forest_cover_2020,
            "eudr_compliance_assessment": report.eudr_compliance_assessment,
            "protected_area_status": report.protected_area_status,
            "cover_extent_summary": report.get_cover_extent_summary() if report.cover_extent_summary_b64 else None,
            "tree_cover_drivers": report.tree_cover_drivers,
            "cover_extent_area": report.cover_extent_area,
            "date_created": report.date_created,
            "date_updated": report.date_updated
        })
    return jsonify(reports=reports_list)


# 🟢 Créer un nouveau rapport
@api_farmreport_bp.route('/create', methods=['POST'])
def create_farmreport():
    data = request.json

    report = FarmReport(
        farm_id=data.get('farm_id'),
        project_area=data.get('project_area'),
        country_deforestation_risk_level=data.get('country_deforestation_risk_level'),
        radd_alert=data.get('radd_alert'),
        tree_cover_loss=data.get('tree_cover_loss'),
        forest_cover_2020=data.get('forest_cover_2020'),
        eudr_compliance_assessment=data.get('eudr_compliance_assessment'),
        protected_area_status=data.get('protected_area_status'),
        tree_cover_drivers=data.get('tree_cover_drivers'),
        cover_extent_area=data.get('cover_extent_area'),
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )

    cover_summary = data.get('cover_extent_summary')
    if cover_summary:
        report.set_cover_extent_summary(cover_summary)

    db.session.add(report)
    db.session.commit()

    return jsonify({"msg": "Farm report created successfully!"}), 201


# 🟡 Récupérer un rapport par ID
@api_farmreport_bp.route('/<int:id>', methods=['GET'])
def get_farmreport(id):
    report = FarmReport.query.get_or_404(id)
    return jsonify({
        "id": report.id,
        "farm_id": report.farm_id,
        "project_area": report.project_area,
        "country_deforestation_risk_level": report.country_deforestation_risk_level,
        "radd_alert": report.radd_alert,
        "tree_cover_loss": report.tree_cover_loss,
        "forest_cover_2020": report.forest_cover_2020,
        "eudr_compliance_assessment": report.eudr_compliance_assessment,
        "protected_area_status": report.protected_area_status,
        "cover_extent_summary": report.get_cover_extent_summary(),
        "tree_cover_drivers": report.tree_cover_drivers,
        "cover_extent_area": report.cover_extent_area,
        "date_created": report.date_created,
        "date_updated": report.date_updated
    })


# 🟠 Modifier un rapport
@api_farmreport_bp.route('/<int:id>/edit', methods=['PUT'])
def edit_farmreport(id):
    report = FarmReport.query.get_or_404(id)
    data = request.json

    report.project_area = data.get('project_area', report.project_area)
    report.country_deforestation_risk_level = data.get('country_deforestation_risk_level', report.country_deforestation_risk_level)
    report.radd_alert = data.get('radd_alert', report.radd_alert)
    report.tree_cover_loss = data.get('tree_cover_loss', report.tree_cover_loss)
    report.forest_cover_2020 = data.get('forest_cover_2020', report.forest_cover_2020)
    report.eudr_compliance_assessment = data.get('eudr_compliance_assessment', report.eudr_compliance_assessment)
    report.protected_area_status = data.get('protected_area_status', report.protected_area_status)
    report.tree_cover_drivers = data.get('tree_cover_drivers', report.tree_cover_drivers)
    report.cover_extent_area = data.get('cover_extent_area', report.cover_extent_area)

    if 'cover_extent_summary' in data and data['cover_extent_summary']:
        report.set_cover_extent_summary(data['cover_extent_summary'])

    report.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Farm report updated successfully!"})


# 🔴 Supprimer un rapport
@api_farmreport_bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_farmreport(id):
    report = FarmReport.query.get_or_404(id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({"msg": "Farm report deleted successfully!"})


# 🔍 Récupérer un rapport par ferme
@api_farmreport_bp.route('/byfarm/<int:farm_id>', methods=['GET'])
def get_farmreport_by_farm(farm_id):
    report = FarmReport.query.filter_by(farm_id=farm_id).first()
    if report:
        return jsonify({
            'status': 'success',
            'report': {
                "id": report.id,
                "farm_id": report.farm_id,
                "project_area": report.project_area,
                "country_deforestation_risk_level": report.country_deforestation_risk_level,
                "radd_alert": report.radd_alert,
                "tree_cover_loss": report.tree_cover_loss,
                "forest_cover_2020": report.forest_cover_2020,
                "eudr_compliance_assessment": report.eudr_compliance_assessment,
                "protected_area_status": report.protected_area_status,
                "cover_extent_summary": report.get_cover_extent_summary(),
                "tree_cover_drivers": report.tree_cover_drivers,
                "cover_extent_area": report.cover_extent_area,
                "date_created": report.date_created,
                "date_updated": report.date_updated
            }
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No report found for the provided farm ID'
        }), 404


# 📊 Compter tous les rapports
@api_farmreport_bp.route('/count/total', methods=['GET'])
def count_all_reports():
    total = FarmReport.query.count()
    return jsonify({
        'status': 'success',
        'total_reports': total
    })
