from flask import g
from functools import wraps
from .errors import forbidden

def permission_required(permission):
    """Decorator function used for functions where a certain permisson (given) is required

    Args:
        permission (int): Permission int described in models.py
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not g.current_user.can(permission):
                return forbidden("Insufficient permissions")
            return f(*args, **kwargs)
        return decorated_function
    return decorator