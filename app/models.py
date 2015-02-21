from datetime import datetime
from sqlalchemy.ext.hybrid import hybrid_property

from . import app
from . import db, bcrypt, loginmanager


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(64), unique=True)
    _password = db.Column(db.String(128))
    registered_on = db.Column(db.DateTime)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def _set_password(self, plaintext):
        self._password = bcrypt.generate_password_hash(plaintext)

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.registered_on = datetime.utcnow()

    def check_password(self, plaintext):
        if bcrypt.check_password_hash(self._password, plaintext):
            return True
        else:
            return False
 
    def is_authenticated(self):
        return True
 
    def is_active(self):
        return True
 
    def is_anonymous(self):
        return False
 
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.username)


class ButtonPress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time_stamp = db.Column(db.DateTime)
    trackperson_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    trackperson = db.relationship('User', uselist=False)

    def __init__(self, user, time_stamp):
        self.trackperson = user
        self.time_stamp = time_stamp


@loginmanager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()


def init_db():
    """ Run once to create tables """
    with app.app_context():
        db.create_all()

