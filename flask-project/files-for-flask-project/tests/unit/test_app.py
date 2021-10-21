from app import db
from app.models import User

def test_database_insert(new_app):
    u = User(username='john')
    db.session.add(u)
    db.session.commit()

def test_password_functionality(new_app):
    u = User(password='test')
    u1 = User(password='test')
    db.session.add(u)
    db.session.commit()
    u.password_hash = True
    # u.verify_password('test') == True
    # u.verify_password('nottest') = False
    # u.password = AttributeError
    u.password_hash != u1.password_hash
