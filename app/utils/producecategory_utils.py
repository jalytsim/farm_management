from app.models import ProduceCategory
from app import db

def create_pc(name, grade, created_by=None, modified_by=None):
    pc = ProduceCategory(name=name, grade=grade, created_by=created_by, modified_by=modified_by)
    db.session.add(pc)
    db.session.commit()
    return pc
def update_pc(pc, name, grade, modified_by=None):
    pc.name = name
    pc.grade = grade
    if modified_by is not None:
        pc.modified_by = modified_by
    db.session.commit()
    
def delete_pc(pc):
    db.session.delete(pc)
    db.session.commit()
