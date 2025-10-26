from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
from app.models import db, Certificate, User

certificate_bp = Blueprint('certificate', __name__)

# ----------------------------------------------------
# 1) GÉNÉRATION / ENREGISTREMENT DU CERTIFICAT
# ----------------------------------------------------
@certificate_bp.route('/api/certificate/generate', methods=['POST'])
@jwt_required()
def generate_certificate():
    try:
        data = request.get_json()

        if not data:
            return jsonify({'status': 'error', 'message': 'Invalid JSON input'}), 400

        user_id = data.get('userId')
        certificate_type = data.get('certificateType', 'all')
        stats = data.get('stats', {})
        pdf_base64 = data.get('pdfBase64')

        # Vérifier que la personne pour qui on génère le certificat existe
        user = User.query.get(user_id)
        if not user:
            return jsonify({'status': 'error', 'message': 'User not found'}), 404

        # Utilisateur authentifié (celui qui génère)
        identity = get_jwt_identity()
        created_by = identity['id']

        # Génération d'un ID unique
        certificate_id = f"{user_id}-{datetime.utcnow().year}-{certificate_type.upper()}"

        issue_date = datetime.utcnow()
        valid_until = issue_date + timedelta(days=365)

        title_map = {
            'compliant': 'CERTIFICATE OF FULL COMPLIANCE',
            'likely_compliant': 'CERTIFICATE OF LIKELY COMPLIANCE',
            'not_compliant': 'CERTIFICATE OF NON-COMPLIANCE',
            'all': 'GLOBAL COMPLIANCE CERTIFICATE'
        }
        title = title_map.get(certificate_type, 'COMPLIANCE CERTIFICATE')

        compliance_status = stats.get('compliance_status', {})
        percentages = stats.get('compliance_percentages', {})

        if certificate_type == 'all':
            overall_rate = percentages.get('compliant_100_percent', 0)
        else:
            overall_rate = percentages.get(f'{certificate_type}_percent', 0)

        qr_data = f"UserID:{user_id}|Type:{certificate_type}|Rate:{overall_rate}%|Cert:{certificate_id}"

        certificate = Certificate(
            certificate_id=certificate_id,
            user_id=user_id,
            certificate_type=certificate_type,
            total_farms=stats.get('total_farms', 0),
            compliant_100_count=compliance_status.get('compliant_100', 0),
            likely_compliant_count=compliance_status.get('likely_compliant', 0),
            not_compliant_count=compliance_status.get('not_compliant', 0),
            compliant_100_percent=percentages.get('compliant_100_percent', 0),
            likely_compliant_percent=percentages.get('likely_compliant_percent', 0),
            not_compliant_percent=percentages.get('not_compliant_percent', 0),
            overall_compliance_rate=overall_rate,
            title=title,
            issue_date=issue_date,
            valid_until=valid_until,
            pdf_data_base64=pdf_base64,
            qr_code_data=qr_data,
            status='active',
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent'),
            created_by=created_by
        )

        db.session.add(certificate)
        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Certificate generated successfully',
            'data': certificate.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ----------------------------------------------------
# 2) TRACKER UN TÉLÉCHARGEMENT
# ----------------------------------------------------
@certificate_bp.route('/api/certificate/download/<int:certificate_id>', methods=['POST'])
@jwt_required()
def track_download(certificate_id):
    try:
        certificate = Certificate.query.get(certificate_id)
        if not certificate:
            return jsonify({'status': 'error', 'message': 'Certificate not found'}), 404

        identity = get_jwt_identity()
        certificate.download_count += 1
        certificate.last_downloaded = datetime.utcnow()
        certificate.modified_by = identity['id']

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Download tracked',
            'download_count': certificate.download_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ----------------------------------------------------
# 3) LISTE DES CERTIFICATS D’UN UTILISATEUR
# ----------------------------------------------------
@certificate_bp.route('/api/certificate/user/<int:user_id>', methods=['GET'])
@jwt_required()
def get_user_certificates(user_id):
    try:
        certificates = Certificate.query.filter_by(user_id=user_id).order_by(
            Certificate.date_created.desc()
        ).all()

        return jsonify({
            'status': 'success',
            'data': [cert.to_dict() for cert in certificates]
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ----------------------------------------------------
# 4) VÉRIFIER (PUBLIC)
# ----------------------------------------------------
@certificate_bp.route('/api/certificate/verify/<certificate_id>', methods=['GET'])
def verify_certificate(certificate_id):
    try:
        certificate = Certificate.query.filter_by(certificate_id=certificate_id).first()

        if not certificate:
            return jsonify({
                'status': 'error',
                'message': 'Certificate not found',
                'valid': False
            }), 404

        is_expired = datetime.utcnow() > certificate.valid_until
        is_valid = certificate.status == 'active' and not is_expired

        return jsonify({
            'status': 'success',
            'valid': is_valid,
            'data': {
                'certificate_id': certificate.certificate_id,
                'user_id': certificate.user_id,
                'type': certificate.certificate_type,
                'issue_date': certificate.issue_date.isoformat(),
                'valid_until': certificate.valid_until.isoformat(),
                'status': certificate.status,
                'is_expired': is_expired,
                'compliance_rate': certificate.overall_compliance_rate
            }
        }), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


# ----------------------------------------------------
# 5) RÉVOQUER (ADMIN ou PROPRIO)
# ----------------------------------------------------
@certificate_bp.route('/api/certificate/<int:certificate_id>', methods=['DELETE'])
@jwt_required()
def revoke_certificate(certificate_id):
    try:
        certificate = Certificate.query.get(certificate_id)
        if not certificate:
            return jsonify({'status': 'error', 'message': 'Certificate not found'}), 404

        identity = get_jwt_identity()
        requester_id = identity['id']
        requester = User.query.get(requester_id)

        # autorisations
        if requester_id != certificate.user_id and not requester.is_admin:
            return jsonify({'status': 'error', 'message': 'Unauthorized'}), 403

        certificate.status = 'revoked'
        certificate.modified_by = requester_id

        db.session.commit()

        return jsonify({
            'status': 'success',
            'message': 'Certificate revoked successfully'
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': str(e)}), 500
