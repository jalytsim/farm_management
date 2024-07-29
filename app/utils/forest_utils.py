from app.models import Forest
from ..models import db, FarmData, Farm, District, SoilData
from datetime import datetime
from flask_login import current_user

def create_forest(name, tree_type):
    new_forest = Forest(
        name=name,
        tree_type=tree_type,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow(),
        created_by=current_user.id,
        modified_by=current_user.id
    )
    db.session.add(new_forest)
    db.session.commit()

def update_forest(id, name, tree_type):
    forest = db.session.query(Forest).get(id)
    if forest:
        forest.name = name
        forest.tree_type = tree_type
        forest.date_updated = datetime.utcnow()
        forest.modified_by = current_user.id
        db.session.commit()

def delete_forest(id):
    forest = db.session.query(Forest).get(id)
    if forest:
        db.session.delete(forest)
        db.session.commit()
        
def get_all_forests():
    return db.session.query(Forest).all()
