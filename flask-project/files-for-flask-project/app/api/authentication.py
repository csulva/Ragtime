from flask_httpauth import HTTPBasicAuth
from flask import jsonify, g
from app.models import User
from .errors import unauthorized, forbidden
from . import api


auth = HTTPBasicAuth()

@auth.verify_password
def verify_password(email_or_token, password):
    if email_or_token == '':
        return False
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    return user.verify_password(password)

@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials.')

@api.route('/')
@auth.login_required
def test():
    return jsonify({})