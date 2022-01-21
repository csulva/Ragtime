import pytest
from app import db, create_app
from app.models import User
from flask import current_app

@pytest.fixture(scope='module')
def new_app():
    """Tests that test database works when creating an app in 'testing' configuration
    """
    app = create_app('testing')
    assert 'data-test.sqlite' in app.config['SQLALCHEMY_DATABASE_URI']
    test_client = app.test_client()
    context = app.app_context()
    context.push()
    db.create_all()

    yield test_client

    db.session.remove()
    db.drop_all()
    context.pop()

