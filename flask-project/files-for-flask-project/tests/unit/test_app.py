from app import db
from app.models import User
import pytest

def test_database_insert(new_app):
    u = User(username='john')
    db.session.add(u)
    db.session.commit()

def test_password_functionality(new_app):
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
