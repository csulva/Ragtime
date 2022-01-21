from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g
from app.models import User
from .errors import unauthorized, forbidden
from . import api

auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    """Verifies user in order to access API

    Args:
        email_or_token (string): Email or token from the user
        password (string): Password from the user
    """
    if email_or_token == '':
        return False
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)

@api.before_request
@auth.login_required
def before_request():
    """Function returns forbidden if account unconfirmed or anonymous user
    """
    if not g.current_user.is_anonymous and \
        not g.current_user.confirmed:
        return forbidden('Unconfirmed account')

@auth.error_handler
def auth_error():
    """Returns invalid credentials if unauthorized to access
    """
    return unauthorized('Invalid credentials.')

@api.route('/')
@auth.login_required
def test():
    """Returns empty dictionary for index page of API url
    """
    return jsonify({})

@api.route('/tokens/', methods=['POST'])
def get_token():
    """Posts auth token for the user in json format
    """
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials.')
    return jsonify({'token': g.current_user.generate_auth_token(expiration_sec=3600), 'expiration': 3600})

