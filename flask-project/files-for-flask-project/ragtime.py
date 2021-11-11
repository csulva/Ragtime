from app import create_app, db
from app.models import Composition, Role, User, Follow
import os
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db, render_as_batch=True)

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User, Composition=Composition, Follow=Follow)

app.run()