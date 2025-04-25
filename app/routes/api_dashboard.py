from flask import Blueprint, jsonify, request
from flask_login import current_user, login_required
from app.models import User, Farm, Forest, Tree, FarmData, Store, Product, District
from app import db

dashboard_api_bp = Blueprint('dashboard_api', __name__, url_prefix='/api/dashboard')

# 1. Nombre de users par type
@dashboard_api_bp.route('/users/by-type', methods=['GET'])
@login_required
def users_by_type():
    result = db.session.query(User.user_type, db.func.count(User.id)).group_by(User.user_type).all()
    return jsonify({user_type: count for user_type, count in result})

# 2. Activité d’un utilisateur
@dashboard_api_bp.route('/user/<int:user_id>/activity', methods=['GET'])
@login_required
def user_activity(user_id):
    models = [FarmData, Farm, Forest, Tree, District, Store, Product]
    activity = {}
    for model in models:
        created = db.session.query(model).filter_by(created_by=user_id).count()
        updated = db.session.query(model).filter_by(modified_by=user_id).count()
        activity[model.__tablename__] = {"created": created, "updated": updated}
    return jsonify(activity)

# 3. Statistiques globales
@dashboard_api_bp.route('/entities/count', methods=['GET'])
@login_required
def count_all():
    stats = {
        "farms": Farm.query.count(),
        "forests": Forest.query.count(),
        "trees": Tree.query.count(),
        "farmdata": FarmData.query.count(),
        "stores": Store.query.count(),
        "products": Product.query.count()
    }
    return jsonify(stats)

# 4. Dernières mises à jour par modèle
@dashboard_api_bp.route('/latest-updates/<string:model_name>', methods=['GET'])
@login_required
def latest_updates(model_name):
    limit = int(request.args.get('limit', 10))
    models = {
        'farm': Farm,
        'forest': Forest,
        'tree': Tree,
        'farmdata': FarmData,
        'store': Store,
        'product': Product,
        'district': District
    }
    model = models.get(model_name.lower())
    if not model:
        return jsonify({'error': f'Model {model_name} not found'}), 404
    records = model.query.order_by(model.date_updated.desc()).limit(limit).all()
    return jsonify([{col.name: getattr(record, col.name) for col in model.__table__.columns} for record in records])
