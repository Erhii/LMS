from . import authen
from .. import auth
from flask import jsonify, g, request, abort
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
    phone = request.json.get("phone")
    name = request.json.get('name')
    password = request.json.get("password")
    if phone is None or password is None or name is None:
        abort(400)
    if db.users.find_one({"phone": phone}):
        abort(400)
    user = Users(phone, name)
    user.hash_password(password)
    user_json = {
        "phone": phone,
        "name": name,
        "password": user.password
    }
    db.users.insert_one(user_json)
    user.setId(db.users.find_one({'phone': phone})['_id'])
    return jsonify({"phone": user.phone}), 201


@authen.route("/api/v1.0/password", methods=["PUT"])
@auth.login_required
def modify_password():
    old_password = request.json.get("old_password")
    new_password = request.json.get("new_password")
    if verify_password(g.user.phone, old_password):
        g.user.hash_password(new_password)
        new_password = g.user.password
        db.users.update({'phone': g.user.phone}, {"$set": {"password": new_password}})
    return jsonify({"phone": g.user.phone}), 201
