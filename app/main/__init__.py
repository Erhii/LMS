import flask

main = flask.Blueprint('main', __name__)

from . import views, errors
