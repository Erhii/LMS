import flask_httpauth
import pymongo
import flask
import config


db = pymongo.MongoClient("mongodb://root:Tzaq224930@www.erhii.com:27017/LMS")
auth = flask_httpauth.HTTPBasicAuth()


def create_app(config_name):
    app = flask.Flask(__name__)
    app.config.from_object(config.config[config_name])
    config.config[config_name].init_app(app)

    db.init_app(app)

    from .main import main as main_blueprint
    from .authen import authen as auth_blueprint

    app.register_blueprint(main_blueprint)
    app.register_blueprint(auth_blueprint)

    return app
