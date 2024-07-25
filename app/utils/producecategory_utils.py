from datetime import datetime
from flask_login import current_user
from app import db
from app.models import ProduceCategory


def create_pc(name, grade):
    pc = ProduceCategory(
        name=name,
        grade=grade,
        created_by=current_user.id,
        modified_by=current_user.id,
        date_created=datetime.utcnow(),
        date_updated=datetime.utcnow()
    )
    db.session.add(pc)
    db.session.commit()
    return pc


def update_pc(pc_id, name, grade):
    pc = ProduceCategory.query.get(pc_id)
    if not pc:
        raise ValueError(f"ProduceCategory ID {pc_id} does not exist.")
    
    pc.name = name
    pc.grade = grade
    pc.modified_by = current_user.id
    pc.date_updated = datetime.utcnow()
    db.session.commit()
    return pc


def delete_pc(pc_id):
    pc = ProduceCategory.query.get(pc_id)
    if pc:
        db.session.delete(pc)
        db.session.commit()
    else:
        raise ValueError(f"ProduceCategory ID {pc_id} does not exist.")
