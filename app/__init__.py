import flask_httpauth
import pymongo
import flask
import config


db = pymongo.MongoClient().LMS
auth = flask_httpauth.HTTPBasicAuth()


def create_app(config_name):
    app = flask.Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)

    db.init_app(app)

    from . import main as main_blueprint
    from . import authen as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)
    return app
