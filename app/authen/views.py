from . import authen
from .. import auth
from flask import jsonify, g, request, abort, url_for
from ..models import Users
from .. import db
from bson import ObjectId


@authen.route("/api/v1.0/token", method=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({"token": token.decode("ascii")})


@auth.verify_password
def verify_password(phone_or_token, password):
    user = Users.verify_auth_token(phone_or_token)
    if not user:
        user_json = db.users.find_one({"phone": phone_or_token})
        user = Users(user_json['phone'], user_json['name'], user_json['password'])
        if not user_json or not user.verify_password(password):
            return False
    g.user = user
    return True


@authen.route("/api/v1.0/users", methods=["POST"])
def sign_up():
    account = request.json.get("account")
    password = request.json.get("password")
    if account is None or password is None:
        abort(400)
    if not db.users.find_one({"account": account}):
        abort(400)
    user = Users(account, password)
    user_json = {
        "account": account,
        "password": password
    }
    db.users.insert_one(user_json)
    user.setId(db.users.find_one({'account': account})['_id'])
    return jsonify({"account": user.account}), 201, {"Location": url_for('sign_in',
                                                                         user_id=str(user.id),
                                                                         _external=True)}


@authen.route("/api/v1.0/password", methods=["PUT"])
@auth.login_required
def modify_password():
    account = request.json.get("account")
    old_password = request.json.get("oldPassword")
    new_password = request.json.get("newPassword")
    if account is None or old_password is None or new_password is None:
        abort(400)

    user = db.users.find_one({'account': account})
    if not user:
        abort(400)
    if user['password'] != old_password:
        abort(400)
    db.users.update(
        {'account': account},
        {
            "$set": {
                "password": new_password
            }
        })
    return jsonify({"account": user.account}), 201, {"Location": url_for('sign_in',
                                                                         user_id=str(user.id),
                                                                         _external=True)}