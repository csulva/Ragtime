from flask.globals import current_app
from app import db
from app.models import User
import pytest
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

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

# Test token creation and verification:

# def generate_confirmation_token(self, expiration_sec=3600):
#     s = Serializer(current_app.secret_key, expiration_sec)
#     return s.dumps({'confirm_id': self.id}).decode('utf-8')

# def confirm(self, token):
#     s = Serializer(current_app.secret_key)
#     try:
#         data = s.loads(token.encode('utf-8'))
#     except:
#         return False
#     if data.get('confirm_id') != self.id:
#         return False
#     self.confirmed = True
#     db.session.add(self)
#     return True
