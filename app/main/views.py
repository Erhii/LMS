from . import main
from .. import auth
from flask import request, abort, jsonify, g
from .. import db
from bson import ObjectId
from datetime import datetime


@main.route("/api/v1.0/book", methods=["POST"])
@auth.login_required
def add_book():
    book_json = {
        "book_name": request.json.get("book_name"),
        "author_name": request.json.get("author_name"),
        "publish_name": request.json.get("publish_name"),
        "isbn_num": request.json.get("isbn_num"),
        "price": request.json.get("price"),
        "explanation": request.json.get("explanation")
    }
    db.books.insert_one(book_json)


@main.route("/api/v1.0/book/<string:book_id>", method=['DELETE'])
@auth.login_required
def delete_book(book_id):
    book = db.books.find_one({"_id": ObjectId(book_id)})
    if not book:
        abort(400)
    db.books.delete_one({"_id": ObjectId(book_id)})


@main.route("/api/v1.0/book/<string:book_id>", methods=["PUT"])
@auth.login_required
def modify_book(book_id):
    book_json = {
        "book_name": request.json.get("book_name"),
        "author_name": request.json.get("author_name"),
        "publish_name": request.json.get("publish_name"),
        "isbn_num": request.json.get("isbn_num"),
        "price": request.json.get("price"),
        "explanation": request.json.get("explanation")
    }
    db.books.update({"_id": ObjectId(book_id)}, {"$set": book_json}, upsert=True)


@main.route("/api/v1.0/book/<string:book_id>", method=['GET'])
def display_book(book_id):
    book = db.books.find_one({"_id": ObjectId(book_id)})
    book['_id'] = str(book['_id'])
    return jsonify(book)


@main.route("/api/v1.0/preorder_book/<string:book_id>", method=['POST'])
@auth.login_required
def preoder_book(book_id):
    book = db.books.find_one({"_id": ObjectId(book_id)})
    order = {

    }
    db.preorder.insert({"phone": g.user.phone})


@main.route("/api/v1.0/borrow_book/<string:book_id>", method=['POST'])
@auth.login_required
def borrow_book(book_id):
    book = db.books.find_one({"book_id": book_id})


@main.route("/api/v1.0/history/<string:user_id>", method=["GET"])
def query_history(user_id):
    record = db.records.find({"user_id": user_id})
    return jsonify(record)
