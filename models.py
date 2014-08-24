from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(30))

    def __init__(self, username, password):
        self.username = username
        self.password = password

class ButtonPress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime)
    trackperson_id = db.Column(db.Integer, db.ForeignKey('person.id'))
    trackperson = db.relationship('Person', uselist=False)

    def __init__(self, user, time_stamp):
        self.trackperson = user
        self.time_stamp = time_stamp

