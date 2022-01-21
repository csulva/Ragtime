from flask import jsonify, url_for, current_app, request
from . import api
from ..models import Composition, User

@api.route('/users/<int:id>')
def get_user(id):
    """Function creates API json data of the user with the provided ID

    Args:
        id (int): ID of the user

    Returns:
        .json: data of the user
    """
    # Get the user from the ID provided
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())

@api.route('/users/<int:id>/compositions/', methods=["GET"])
def get_user_compositions(id):
    """Function creates API json data of each composition created by the user with the provided ID

    Args:
        id (int): ID of the user

    Returns:
        .json: json data of each composition
    """
    # Get the user from the ID provided
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    # Get the user's compositions
    query = user.compositions
    # Paginate all compositions
    pagination = query.order_by(Composition.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False)
    # Convert to list
    compositions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_compositions', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_compositions', id=id, page=page+1)
    return jsonify({
        'compositions': [composition.to_json() for composition in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })

@api.route('/users/<int:id>/followed/', methods=["GET"])
def get_user_followed(id):
    """Function creates API json data of compositions of users who are followed by the given user

    Args:
        id (int): ID of the user

    Returns:
        .json: json data of each composition
    """
    # Get the user from the ID provided
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    # Get all followed
    query = user.followed_compositions
    # Paginate all compositions
    pagination = query.order_by(Composition.timestamp.desc()).paginate(
        page,
        per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
        error_out=False)
    # Convert to list
    compositions = pagination.items
    prev = None
    if pagination.has_prev:
        prev = url_for('api.get_user_compositions', id=id, page=page-1)
    next = None
    if pagination.has_next:
        next = url_for('api.get_user_compositions', id=id, page=page+1)
    return jsonify({
        'compositions': [composition.to_json() for composition in compositions],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })