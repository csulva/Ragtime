from flask import Flask
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment
from flask_wtf.csrf import CSRFProtect


bootstrap = Bootstrap()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
mail = Mail()
moment = Moment()
csrf = CSRFProtect()


def create_app(config_name='default'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    csrf.init_app(app)

    bootstrap.init_app(app)
    db.init_app(app)


    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .api import api as api_blueprint
    app.register_blueprint(api_blueprint)

    if app.config['HTTPS_REDIRECT']:
        from flask_talisman import Talisman
        Talisman(app, content_security_policy={
                'default-src': [
                    "'self'",
                    'cdnjs.cloudflare.com',
                ],
                # allow images from anywhere,
                #   including unicornify.pictures
                'img-src': '*'
            }
        )

    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

    return app


