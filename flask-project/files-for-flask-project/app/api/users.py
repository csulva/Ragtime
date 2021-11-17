from flask import jsonify
from . import api
from ..models import User

@api.route('/users/<int:id>')
def get_user(id):
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/compositions/', methods=["GET"])
def get_user_compositions(id):
    return jsonify({})

@api.route('/users/<int:id>/followed/', methods=["GET"])
def get_user_followed(id):
    return jsonify({})