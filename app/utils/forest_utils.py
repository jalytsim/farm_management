from app.models import Forest
from ..models import db, FarmData, Farm, District, SoilData
def create_forest(name):
    new_forest = Forest(name=name)
    db.session.add(new_forest)
    db.session.commit()

def update_forest(id, name):
    forest = db.session.query(Forest).get(id)
    if forest:
        forest.name = name
        db.session.commit()

def delete_forest(id):
    forest = db.session.query(Forest).get(id)
    if forest:
        db.session.delete(forest)
        db.session.commit()
        
def get_all_forests():
    return db.session.query(Forest).all()