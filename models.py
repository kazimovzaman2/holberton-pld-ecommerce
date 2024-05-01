from flask_sqlalchemy import SQLAlchemy
from enum import IntEnum
import secrets

db = SQLAlchemy()


class Role(IntEnum):
    ADMIN = 3
    USER = 2
    COMPANY = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    surname = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    role = db.Column(db.Enum(Role), default=Role.USER)
    token = db.Column(db.String(120), unique=True, nullable=True)

    def __repr__(self):
        return "<User %r>" % self.name

    def generate_token(self):
        self.token = secrets.token_hex(16)
        db.session.commit()

    @staticmethod
    def verify_token(token):
        return User.query.filter_by(token=token).first()

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(80))
    company_address = db.Column(db.String(80))
    is_active = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    user = db.relationship("User", backref="company")
