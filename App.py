from flask import Flask, request, abort, jsonify, url_for, g
from bson.objectid import ObjectId




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


