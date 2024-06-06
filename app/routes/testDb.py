from flask import Blueprint, jsonify

from app.utils.point_utils import get_all_points, get_pointDetails
from ..models import db, District

test = Blueprint('test', __name__)

@test.route('/test_db')
def test_db():
    data = get_all_points()
    return jsonify(data)
