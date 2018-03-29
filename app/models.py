from passlib.apps import custom_app_context
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, SignatureExpired, BadSignature
from flask import current_app
from . import db


class Users(object):
    def __init__(self, phone="", name="", password=""):
        self.id = ""
        self.phone = phone
        self.name = name
        self.password = password

    def setId(self, user_id):
        self.id = user_id

    def hash_password(self, password):
        self.password = custom_app_context.encrypt(password)

    def verify_password(self, password):
        return custom_app_context.verify(password, self.password)

    def generate_auth_token(self, expriation=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expriation)
        return s.dumps({'id': self.phone})

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            return None
        except BadSignature:
            return None
        user = db.users.find_one({"phone": (data['id'])})
        return Users(phone=user['phone'], password=user['password'], name=user['name'])

