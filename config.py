# Config classes differentiated based on stage of application

from logging import DEBUG
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# Parent config class
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or "anyrandomstringofevents#123"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Email configurations
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    RAGTIME_ADMIN = os.environ.get('RAGTIME_ADMIN')
    RAGTIME_MAIL_SUBJECT_PREFIX = 'Ragtime - '
    RAGTIME_MAIL_SENDER = f'Ragtime Admin <{RAGTIME_ADMIN}>'

    # Pagination information
    RAGTIME_COMPS_PER_PAGE = 20
    RAGTIME_FOLLOWERS_PER_PAGE = 20

    HTTPS_REDIRECT = False

    @staticmethod
    def init_app(app):
        pass

# Development Configuration
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_DEV_URL') or \
        f'sqlite:///{os.path.join(basedir, "data-dev.sqlite")}'

# Testing Configuration
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL') or \
        f'sqlite:///{os.path.join(basedir, "data-test.sqlite")}'

# Production Configuration
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(basedir, "data.sqlite")}'

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # Log handler for sending emails
        import logging
        from logging.handlers import SMTPHandler
        creds = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            creds = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                # logging: to use TLS, must pass tuple (can be empty)
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.RAGTIME_MAIL_SENDER,
            toaddrs=[cls.RAGTIME_ADMIN],
            subject=cls.RAGTIME_MAIL_SUBJECT_PREFIX + " Application Error",
            credentials=creds,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

# Heroku Configuration for deploying to Heroku in production. FLASK_CONFIG should be 'heroku'.
class HerokuConfig(ProductionConfig):
    HTTPS_REDIRECT = True if os.environ.get('DYNO') else False

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        # log to stderr
        import logging
        from logging import StreamHandler
        file_handler = StreamHandler
        file_handler.setLevel(file_handler, level=logging.INFO)
        app.logger.addHandler(file_handler)

        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)


# Names of config classes
config = {'development': DevelopmentConfig,
'testing': TestingConfig,
'production': ProductionConfig,
'default': DevelopmentConfig,
'heroku': HerokuConfig,
}