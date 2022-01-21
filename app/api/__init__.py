from flask import Blueprint
from app.models import Permission

api = Blueprint('api', __name__, url_prefix='/api/v1')

from . import authentication, compositions, errors, users