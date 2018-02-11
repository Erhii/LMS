from flask import Flask, request, abort, jsonify, url_for
from pymongo import MongoClient
from flask.ext.httpauth import HTTPBasicAuth
from passlib import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from bson.objectid import ObjectId


app = Flask(__name__)
auth = HTTPBasicAuth()
db = MongoClient().LMS
app.config = {
    "SECRET_KEY": "ohfouwehfonewoifnksdnnjfj"
}

class Users():
    def __init__(self, account="", password=""):
        self.id = ""
        self.account = account
        self.password = ""
        self.hash_password(password)

    def setId(self, user_id):
        self.id = user_id

    def hash_password(self, password):
        self.password = custom_app_context(password)

    def verify_password(self, password):
        return custom_app_context(password, self.password)

    def generate_auth_token(self, expriation=600):
        s = Serializer(app.config['SECRET_KEY'], expires_in=expriation)
        return s.dumps({'id': self.id})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = db.users.find_one({"_id": data['id']})
        return user


@app.route("/api/v1.0/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({"token": token.decode("ascii")})


@auth.verify_password
def verify_password(account_or_token, password):
    user = Users.generate_auth_token(account_or_token)
    if not user:
        user_json = db.users.find_one({"account": account})
        user = Users(user_json['account'], user_json['password'])
        if not user_json or not user.verify_password(password):
            return False
    g.user = user
    return True


@app.route("/api/v1.0/users", methods=["POST"])
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
                                                                         id=str(user.id),
                                                                         _external=True)}


@app.route("/api/v1.0/users/<string:id>")
def sign_in(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        abort(400)
    return jsonify({'account': user.account})


