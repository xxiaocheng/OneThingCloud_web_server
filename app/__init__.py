from flask import Flask
from flask_bootstrap import Bootstrap
from config import config


bootstrap=Bootstrap()


def create_app(config_name):
    app=Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)


    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint,url_prefix='/auth')

    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint,url_prefix='/')

    from .wkb import wkb as wkb_blueprint
    app.register_blueprint(wkb_blueprint,url_prefix='/wkb')

    from .cloud import cloud as cloud_blueprint
    app.register_blueprint(cloud_blueprint,url_prefix='/cloud')


    return app
    