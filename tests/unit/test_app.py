from flask.globals import current_app
from app import db
from app.models import User
import pytest
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

def test_database_insert(new_app):
    """Tests to see if Users can be created from the database, added to the database
    and that it can be committed.

    Args:
        new_app (function): creates an app to test this function with database. See: conftest.py
    """
    u = User(username='john')
    db.session.add(u)
    db.session.commit()

def test_password_functionality(new_app):
    """Tests to see if User passwords can be created, added, and committed. Also tests the
    'verify_password()' function to check that the password created returns True when provided
    with the correct password because passwords are hashed for security purposes.

    Args:
        new_app (function): creates an app to test this function with database. See: conftest.py
    """
    u = User(password='test')
    u1 = User(password='test')
    db.session.add(u)
    db.session.commit()
    u.password_hash == True
    u.verify_password('test') == True
    u.verify_password('nottest') == False
    with pytest.raises(AttributeError):
        assert u.password=='Password is not a readable attribute'
    u.password_hash != u1.password_hash



