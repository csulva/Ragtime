from app import create_app, db
from app.models import Composition, Role, User, Follow
import os
from flask_migrate import Migrate
from flask_migrate import upgrade

# Create app from FLASK_CONFIG environment variable config or default config
app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db, render_as_batch=True)

# Allows to not need to import database tables every time you call a Flask Shell session
@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User, Composition=Composition, Follow=Follow)

# Creates tables, adds Roles, and ensures Users follow themselves. Deployed before production
@app.cli.command()
def deploy():
    """ Run deployment tasks """
    # migrate database
    upgrade()

    Role.insert_roles()

    User.add_self_follows()
