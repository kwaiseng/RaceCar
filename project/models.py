from flask_login import UserMixin
from . import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))

class Entry(db.Model):
    id = db.Column(db.Integer, primary_key=True) # primary keys are required by SQLAlchemy
    name = db.Column(db.String(100))
    url = db.Column(db.String(256), unique=True)
    origfilename = db.Column(db.String(256))
    car_type = db.Column(db.String(256))
    first_100K = db.Column(db.Integer)
    top_speed =db.Column(db.Integer)
    price = db.Column(db.Integer)
    qty = db.Column(db.Integer)
