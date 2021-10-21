from app import db
from app.models import User

def test_database_insert(new_app):
    u = User(username='john')
    db.session.add(u)
    db.session.commit()