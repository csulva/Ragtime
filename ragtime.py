from app import create_app, db
from app.models import Composition, Role, User, Follow
import os
from flask_migrate import Migrate
from flask_migrate import upgrade

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User, Composition=Composition, Follow=Follow)

@app.cli.command()
def deploy():
    """ Run deployment tasks """
    db.drop_all()
    db.create_all()
    # migrate database
    upgrade()

    Role.insert_roles()

    User.add_self_follows()
