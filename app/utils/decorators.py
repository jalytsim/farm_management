# app/utils/decorators.py
# =============================================================================
#  Autorisation côté serveur.
#
#  Ton guard React `UserTypeRoute` empêche d'AFFICHER l'écran admin, mais
#  n'empêche personne d'appeler l'API directement. Aujourd'hui un compte
#  'farmer' peut supprimer tes produits avec un simple curl. Ce fichier ferme
#  la porte là où elle compte vraiment.
# =============================================================================

from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import User


def _identity_dict():
    identity = get_jwt_identity()
    return identity if isinstance(identity, dict) else {'id': identity}


def current_user_id():
    return _identity_dict().get('id')


def load_current_user():
    """Relit l'utilisateur EN BASE plutôt que de faire confiance au JWT.

    Le token peut avoir été émis avant qu'on retire les droits d'admin à
    quelqu'un : tant qu'il n'a pas expiré, il continue d'affirmer is_admin=True.
    Une requête en base coûte une milliseconde et supprime le problème.
    """
    uid = current_user_id()
    return User.query.get(uid) if uid else None


def admin_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = load_current_user()
        if not user:
            return jsonify({"msg": "Compte introuvable"}), 401
        if not user.is_admin:
            return jsonify({"msg": "Accès réservé aux administrateurs"}), 403
        return fn(*args, **kwargs)
    return wrapper


def permission_required(permission_key):
    """Autorise si l'utilisateur est admin OU si la clé est activée dans son
    JSON `permissions` — même logique que ton UserTypeRoute côté React."""
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            user = load_current_user()
            if not user:
                return jsonify({"msg": "Compte introuvable"}), 401
            if user.is_admin or (user.permissions or {}).get(permission_key):
                return fn(*args, **kwargs)
            return jsonify({
                "msg": f"Le module « {permission_key} » n'est pas activé sur votre compte"
            }), 403
        return wrapper
    return decorator