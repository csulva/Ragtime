from flask import jsonify, request, url_for, g
from . import api
from .decorators import permission_required
from .. import db
from ..models import Composition, Permission

@api.route('/compositions/', methods=["POST"])
@permission_required(Permission.PUBLISH)
def new_composition():
    composition = Composition.from_json(request.json)
    composition.artist = g.current_user
    db.session.add(composition)
    db.session.commit()
    composition.generate_slug()
    return jsonify(composition.to_json()), 201, \
        {'Location': url_for('api.get_composition', id=composition.id)}

@api.route('/compositions/<int:id>', methods=["GET"])
def get_composition(id):
    return jsonify({})

# @api.route('/compositions/')
# def get_compositions():
#     compositions = Composition.query.all()
#     return jsonify({ 'compositions': [composition.to_json()
#                                       for composition in compositions]})