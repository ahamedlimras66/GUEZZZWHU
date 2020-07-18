from db import db
from flask_login import UserMixin
from sqlalchemy import ForeignKey


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String)
    phone_no = db.Column(db.String(10))
    email = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.DateTime, nullable=False)
    verification = db.Column(db.Integer, nullable=False, default=0)
    otp = db.Column(db.String(4))
    user = db.relationship('Link', cascade="all,delete",backref="user")
    linkcommand = db.relationship('LinkCommand', cascade="all,delete",backref="user")

class Link(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, ForeignKey('user.id'))
    link = db.relationship('LinkCommand', cascade="all,delete",backref="link")

class LinkCommand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    link_id = db.Column(db.Integer, ForeignKey('link.id'))
    commander_id = db.Column(db.Integer, ForeignKey('user.id'))
    date_time = db.Column(db.DateTime,)
    command =  db.Column(db.String(255))