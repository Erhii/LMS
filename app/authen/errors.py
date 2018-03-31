from . import authen
from flask import jsonify


@authen.app_errorhandler(404)
def page_not_found(e):
    return jsonify({
        'error': e,
        'code': 404
    })


@authen.app_errorhandler(500)
def internal_server_error(e):
    return jsonify({
        'error': e,
        'code': 500
    })

