from app import db
from app.models import Tree
#tao amn district no nalaina 
def create_tree(name, type, forest_id, point_id, cutting_date, height, diameter, created_by):
    new_tree = Tree(name=name, type=type, forest_id=forest_id, point_id=point_id, cutting_date=cutting_date, height=height, diameter=diameter, created_by=created_by)
    db.session.add(new_tree)
    db.session.commit()
    return new_tree

def get_all_tree():
    return Tree.query.all()

def get_tree_by_id(tree_id):
    return Tree.query.get_or_404(tree_id)

def update_tree(tree_id,name, type, forest_id, point_id, cutting_date, height, diameter, modified_by):
    tree = get_tree_by_id(tree_id)
    tree.name = name
    tree.type = type
    tree.forest_id = forest_id
    tree.point_id = point_id
    tree.cutting_date = cutting_date
    tree.height = height
    tree.diameter = diameter
    tree.modified_by = modified_by
    db.session.commit()
    return tree

def delete_tree(tree_id):
    tree = get_tree_by_id(tree_id)
    db.session.delete(tree)
    db.session.commit()
