from app.models import Forest
from ..models import db
from datetime import datetime
from flask_login import current_user

def create_forest(name, tree_type, user=None):
    print(user.id)
    if user:
        user_id = user.id
    else:
        user_id = current_user.id

    new_forest = Forest(
        name=name,
        tree_type=tree_type,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow(),
        created_by=user_id,
        modified_by=user_id
    )
    db.session.add(new_forest)
    db.session.commit()
    return new_forest  # Retourner l'objet créé

def update_forest(forest_id, name, tree_type, user=None):
    forest = db.session.query(Forest).get(forest_id)
    print(user.id) 
    if user:
        user_id = user.id
    else:
        # Assuming 'current_user' is a global or context-based object that provides the current user's ID
        user_id = current_user.id
    if forest:
        forest.name = name
        forest.tree_type = tree_type
        forest.date_updated = datetime.utcnow()
        forest.modified_by = user_id
        db.session.commit()


def delete_forest(id):
    forest = db.session.query(Forest).get(id)
    if forest:
        db.session.delete(forest)
        db.session.commit()
        
def get_all_forests():
    return db.session.query(Forest).all()
