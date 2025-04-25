from app.models import User
from app import db

def count_users_by_type():
    result = db.session.query(User.user_type, db.func.count(User.id)).group_by(User.user_type).all()
    return {user_type: count for user_type, count in result}


from app.models import FarmData, Farm, Forest, Tree, District, Store, Product
from flask_login import current_user

def get_user_activity(user_id=None):
    user_id = user_id or current_user.id
    activity = {}

    models = [FarmData, Farm, Forest, Tree, District, Store, Product]
    for model in models:
        created_count = db.session.query(model).filter_by(created_by=user_id).count()
        updated_count = db.session.query(model).filter_by(modified_by=user_id).count()
        activity[model.__tablename__] = {
            "created": created_count,
            "updated": updated_count
        }

    return activity


def get_latest_updates(model, limit=10):
    return model.query.order_by(model.date_updated.desc()).limit(limit).all()

def count_all_entities():
    from app.models import Farm, Forest, Tree, FarmData, Store, Product
    return {
        "farms": Farm.query.count(),
        "forests": Forest.query.count(),
        "trees": Tree.query.count(),
        "farmdata": FarmData.query.count(),
        "stores": Store.query.count(),
        "products": Product.query.count()
    }
