"""
Contrôles d'accès des rapports (EUDR, Carbon, CO2…).

Même règle que les listes de fermes/forêts (api_farm.py, api_forest.py) :
un utilisateur ne voit que ce qu'il a créé (created_by), un admin voit tout.
Les rapports invités, eux, exigent un paiement actif pour le numéro de
téléphone (même contrôle que /api/sentinel/guest/sat-index).

Chaque fonction renvoie None si l'accès est autorisé, sinon une réponse
d'erreur Flask prête à être retournée par la route.
"""
from flask import jsonify, request
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models import User
from app.utils.feature_payment_utils import has_guest_access, has_user_access


def current_user():
    """Utilisateur du JWT (en-tête Authorization), ou None si absent/invalide."""
    try:
        verify_jwt_in_request(optional=True)
        identity = get_jwt_identity()
    except Exception:
        return None
    user_id = identity.get('id') if isinstance(identity, dict) else identity
    return User.query.get(user_id) if user_id is not None else None


def check_owner_access(entity, label='resource'):
    """Accès à une ferme/forêt : admin (vérifié en base, pas dans le JWT) ou créateur."""
    user = current_user()
    if user is None:
        return jsonify({"error": "Authentication required"}), 401
    if user.is_admin or entity.created_by == user.id:
        return None
    return jsonify({"error": f"You do not have access to this {label}"}), 403


def check_guest_report_access(feature_name, phone=None):
    """
    Rapport invité : paiement actif pour ce numéro (body `phone` ou en-tête
    X-Guest-Phone). Un utilisateur connecté passe s'il est admin ou a lui-même
    payé la fonctionnalité.
    """
    user = current_user()
    if user is not None and (user.is_admin or has_user_access(user.id, feature_name)):
        return None

    phone = phone or request.headers.get('X-Guest-Phone')
    if not phone:
        return jsonify({"error": "Phone number required"}), 400
    if not has_guest_access(phone, feature_name):
        return jsonify({"error": "No active paid access for this phone number"}), 403
    return None
