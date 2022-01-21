from flask import jsonify
from ..exceptions import ValidationError
from . import api

@api.errorhandler(ValidationError)
def validation_error(e):
    """Given Validation Error, returns bad request message
    """
    return bad_request(e.args[0])

def forbidden(message):
    """Returns json with 403 forbidden error message, forbidden
    """
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response

def bad_request(message):
    """Returns json with 400 error message, bad request
    """
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response

def unauthorized(message):
    """Returns json with 401 error message, unauthorized
    """
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response