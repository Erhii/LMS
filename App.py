from flask import Flask, request, abort, jsonify, url_for, g
from pymongo import MongoClient
from flask.ext.httpauth import HTTPBasicAuth
from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from bson.objectid import ObjectId


app = Flask(__name__)
auth = HTTPBasicAuth()
db = MongoClient().LMS
app.config = {
    "SECRET_KEY": "ohfouwehfonewoifnksdnnjfj"
}


class Users(object):
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


class Books(object):
    def __init__(self, book_name, author_name, publish_name, isbn_num, price, explanation):
        self.id = ""
        self.book_name = book_name
        self.author_name = author_name
        self.publish_name = publish_name
        self.ISBN_num = isbn_num
        self.price = price
        self.explanation = explanation
        self.count = ""

    def setId(self, book_id):
        self.id = book_id


@app.route("/api/v1.0/token")
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({"token": token.decode("ascii")})


@auth.verify_password
def verify_password(account_or_token, password):
    user = Users.generate_auth_token(account_or_token)
    if not user:
        user_json = db.users.find_one({"account": account_or_token})
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
                                                                         user_id=str(user.id),
                                                                         _external=True)}


@app.route("/api/v1.0/users/<string:user_id>")
def sign_in(user_id):
    user = db.users.find_one({'_id': ObjectId(user_id)})
    if not user:
        abort(400)
    return jsonify({'account': user.account})


@app.route("/api/v1.0/modify_password", methods=["POST"])
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


@app.route("/api/v1.0/add_book", methods=["POST"])
@auth.login_required
def add_book():
    book_name = request.json.get("book_name")
    author_name = request.json.get("author_name")
    publish_name = request.json.get("publish_name")
    isbn_num = request.json.get("isbn_num")
    price = request.json.get("price")
    explanation = request.json.get("explanation")
    book = Books(book_name, author_name, publish_name, isbn_num, price, explanation)
    book_json = {
        "book_name": book_name,
        "author_name": author_name,
        "publish_name": publish_name,
        "isbn_num": isbn_num,
        "price": price,
        "explanation": explanation
    }
    db.books.insert_one(book_json)
    book.setId(db.books.find_one({"book_name": book_name})['_id'])


@app.route("/api/v1.0/delete_book/<string:book_id>")
@auth.login_required
def delete_book(book_id):
    book = db.books.find_one({"book_id": ObjectId(book_id)})
    if not book:
        abort(400)
    db.books.delete_one({"book_id": ObjectId(book_id)})


@app.route("/api/v1.0/add_book", methods=["POST"])
@auth.login_required
def modify_book():
    book_id = request.json.get("book_id")
    book_name = request.json.get("book_name")
    author_name = request.json.get("author_name")
    publish_name = request.json.get("publish_name")
    isbn_num = request.json.get("isbn_num")
    price = request.json.get("price")
    explanation = request.json.get("explanation")
    book = db.books.find_one({"book_id": book_id})
    if not book:
        abort(400)
    book_json = {
        "book_name": book_name,
        "author_name": author_name,
        "publish_name": publish_name,
        "isbn_num": isbn_num,
        "price": price,
        "explanation": explanation
    }
    db.books.update(
        {"book_id": book_id},
        {
            "$set": book_json
        }
    )


@app.route("/api/v1.0/display_book/<string:book_id>")
def display_book(book_id):
    book = db.books.find_one({"book_id": ObjectId(book_id)})
    return jsonify(book)


@app.route("/api/v1.0/preorder_book/<string:book_id>")
@auth.login_required
def preoder_book(book_id):
    book = db.books.find_one({"book_id": ObjectId(book_id)})


@app.route("/api/v1.0/query_book/", methods=["POST"])
def query_book():
    book_name = request.json.get("book_name")
    isbn_num = request.json.get("isbn_num")
    if not book_name and isbn_num:
        abort(400)
    book = db.books.find_one({"book_name": book_name, "isbn_num": isbn_num})
    return jsonify(book)


@app.route("/api/v1.0/borrow_book/<string:book_id>")
def borrow_book(book_id):
    book = db.books.find_one({"book_id": book_id})


@app.route("/api/v1.0/query_history/<string:user_id>")
def query_history(user_id):
    record = db.records.find({"user_id": user_id})
    return jsonify(record)


