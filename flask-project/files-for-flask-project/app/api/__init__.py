from flask import Blueprint
from app.models import Permission

api = Blueprint('api', __name__, url_prefix='/api/v1')

@api.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)

from . import authentication, comments, compositions, errors, users