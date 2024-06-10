from app.models import ProduceCategory
from app import db

def create_pc(name, grade):
    pc = ProduceCategory(name=name, grade=grade)
    db.session.add(pc)
    db.session.commit()
    return pc

def update_pc(pc, name, grade):
    pc.name = name
    pc.grade = grade
    db.session.commit()

def delete_pc(pc):
    db.session.delete(pc)
    db.session.commit()