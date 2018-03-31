import flask

authen = flask.Blueprint('authen', __name__)

from . import views, errors
