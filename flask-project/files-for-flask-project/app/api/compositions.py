from flask import jsonify, request, url_for, g, current_app
from . import api
from .decorators import permission_required
from .. import db
from ..models import Composition, Permission
from .errors import forbidden

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
    composition = Composition.query.get_or_404(id)
    return jsonify(composition.to_json())

@api.route('/compositions/<int:id>', methods=['PUT'])
@permission_required(Permission.PUBLISH)
def edit_composition(id):
    composition = Composition.query.get_or_404(id)
    if g.current_user != composition.artist and \
            not g.current_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    import json
    put_json = json.loads(request.json)
    composition.release_type = put_json.get('release_type', composition.release_type)
    composition.title = put_json.get('release_type', composition.title)
    composition.description = put_json.get('description', composition.description)
    db.session.add(composition)
    db.session.commit()
    return jsonify(composition.to_json())

@api.route('/compositions/')
def get_compositions():
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False)
    compositions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_compositions', page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_compositions', page=page+1)
    return jsonify({
        'compositions': [composition.to_json() for composition in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })