# app/routes/api_forestreport.py

from datetime import datetime
from flask import Blueprint, jsonify, request
from app.models import db, ForestReport, Forest
import json

api_forestreport_bp = Blueprint('api_forestreport', __name__, url_prefix='/api/forestreport')


# 🟢 Récupérer tous les rapports
@api_forestreport_bp.route('/', methods=['GET'])
def index():
    reports = ForestReport.query.all()
    reports_list = []
    for report in reports:
        reports_list.append({
            "id": report.id,
            "forest_id": report.forest_id,
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
@api_forestreport_bp.route('/create', methods=['POST'])
def create_forestreport():
    data = request.json
    
    forest_id = data.get('forest_id')
    
    print("📝 Creating/updating forest report for forest_id:", forest_id)
    
    if not forest_id:
        return jsonify({"msg": "forest_id is required"}), 400
    
    # Vérifier si la forêt existe
    forest = Forest.query.get(forest_id)
    if not forest:
        return jsonify({"msg": "Forest not found"}), 404
    
    # Vérifier si un rapport existe déjà
    existing_report = ForestReport.query.filter_by(forest_id=forest_id).first()
    
    if existing_report:
        # Mettre à jour le rapport existant
        print("🔄 Updating existing forest report")
        existing_report.project_area = data.get('project_area', existing_report.project_area)
        existing_report.country_deforestation_risk_level = data.get('country_deforestation_risk_level', existing_report.country_deforestation_risk_level)
        existing_report.radd_alert = data.get('radd_alert', existing_report.radd_alert)
        existing_report.tree_cover_loss = data.get('tree_cover_loss', existing_report.tree_cover_loss)
        existing_report.forest_cover_2020 = data.get('forest_cover_2020', existing_report.forest_cover_2020)
        existing_report.eudr_compliance_assessment = data.get('eudr_compliance_assessment', existing_report.eudr_compliance_assessment)
        existing_report.protected_area_status = data.get('protected_area_status', existing_report.protected_area_status)
        existing_report.tree_cover_drivers = data.get('tree_cover_drivers', existing_report.tree_cover_drivers)
        existing_report.cover_extent_area = data.get('cover_extent_area', existing_report.cover_extent_area)
        existing_report.date_updated = datetime.utcnow()
        
        # Gérer cover_extent_summary
        cover_summary = data.get('cover_extent_summary')
        if cover_summary:
            # Si c'est un objet/dict, le convertir en JSON string
            if isinstance(cover_summary, dict):
                cover_summary = json.dumps(cover_summary)
            existing_report.set_cover_extent_summary(cover_summary)
        
        db.session.commit()
        print("✅ Forest report updated successfully")
        return jsonify({"msg": "Forest report updated successfully!", "report_id": existing_report.id}), 200
    
    # Créer un nouveau rapport
    print("➕ Creating new forest report")
    report = ForestReport(
        forest_id=forest_id,
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

    # Gérer cover_extent_summary
    cover_summary = data.get('cover_extent_summary')
    if cover_summary:
        # Si c'est un objet/dict, le convertir en JSON string
        if isinstance(cover_summary, dict):
            cover_summary = json.dumps(cover_summary)
        report.set_cover_extent_summary(cover_summary)

    db.session.add(report)
    db.session.commit()

    print("✅ Forest report created successfully")
    return jsonify({"msg": "Forest report created successfully!", "report_id": report.id}), 201


# 🟡 Récupérer un rapport par ID
@api_forestreport_bp.route('/<int:id>', methods=['GET'])
def get_forestreport(id):
    report = ForestReport.query.get_or_404(id)
    return jsonify({
        "id": report.id,
        "forest_id": report.forest_id,
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
@api_forestreport_bp.route('/<int:id>/edit', methods=['PUT'])
def edit_forestreport(id):
    report = ForestReport.query.get_or_404(id)
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

    # Gérer cover_extent_summary
    if 'cover_extent_summary' in data and data['cover_extent_summary']:
        cover_summary = data['cover_extent_summary']
        # Si c'est un objet/dict, le convertir en JSON string
        if isinstance(cover_summary, dict):
            cover_summary = json.dumps(cover_summary)
        report.set_cover_extent_summary(cover_summary)

    report.date_updated = datetime.utcnow()
    db.session.commit()
    return jsonify({"msg": "Forest report updated successfully!"})


# 🔴 Supprimer un rapport
@api_forestreport_bp.route('/<int:id>/delete', methods=['DELETE'])
def delete_forestreport(id):
    report = ForestReport.query.get_or_404(id)
    db.session.delete(report)
    db.session.commit()
    return jsonify({"msg": "Forest report deleted successfully!"})


# 🔍 Récupérer un rapport par forêt
@api_forestreport_bp.route('/byforest/<int:forest_id>', methods=['GET'])
def get_forestreport_by_forest(forest_id):
    report = ForestReport.query.filter_by(forest_id=forest_id).first()
    if report:
        return jsonify({
            'status': 'success',
            'report': {
                "id": report.id,
                "forest_id": report.forest_id,
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
            'message': 'No report found for the provided forest ID'
        }), 404


# 📊 Compter tous les rapports
@api_forestreport_bp.route('/count/total', methods=['GET'])
def count_all_reports():
    total = ForestReport.query.count()
    return jsonify({
        'status': 'success',
        'total_reports': total
    })


# 📈 Statistiques des rapports de conformité
@api_forestreport_bp.route('/stats/compliance', methods=['GET'])
def compliance_stats():
    """Statistiques de conformité EUDR pour tous les rapports forestiers"""
    reports = ForestReport.query.all()
    
    stats = {
        'total': len(reports),
        'compliant_100': 0,
        'likely_compliant': 0,
        'not_compliant': 0,
        'unknown': 0
    }
    
    for report in reports:
        assessment = report.eudr_compliance_assessment
        if assessment:
            if '100% Compliant' in assessment:
                stats['compliant_100'] += 1
            elif 'Likely Compliant' in assessment:
                stats['likely_compliant'] += 1
            elif 'Not Compliant' in assessment:
                stats['not_compliant'] += 1
            else:
                stats['unknown'] += 1
        else:
            stats['unknown'] += 1
    
    return jsonify({
        'status': 'success',
        'stats': stats
    })