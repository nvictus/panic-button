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


class Room(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(64), unique=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    admin = db.relationship('User', uselist=False)
    guests = db.relationship('Guest', cascade="save-update, merge, delete")
    created_on = db.Column(db.DateTime)
    ended_on = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean)

    def __init__(self, name, user):
        self.name = name
        self.admin = user
        self.guests.append(Guest(room_id=self.id, user_id=user.id))
        self.is_active = True
        self.created_on = datetime.utcnow()

    def add_guest(self, user):
        self.guests.append(Guest(room_id=self.id, user_id=user.id))
        db.session.commit()

    def end_session(self):
        self.is_active = False
        self.ended_on = datetime.utcnow()        

class Guest(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_active = db.Column(db.Boolean)
    joined_on = db.Column(db.DateTime)
    left_on = db.Column(db.DateTime)

    def __init__(self, room_id, user_id):
        self.room_id = room_id
        self.user_id = user_id
        self.is_active = True
        self.joined_on = datetime.utcnow()

    def leave_room(self):
        self.is_active = False
        self.left_on = datetime.utcnow()


class Panic(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.user_id'))
    guest = db.relationship('Guest', uselist=False)
    time_stamp = db.Column(db.DateTime)

    def __init__(self, user, room, time_stamp):
        guest = Guest.query.filter_by(user_id=user.id, room_id=room.id).first()
        if guest is None:
            raise KeyError("Could not find guest.")
        if guest is room.admin:
            raise ValueError("Admin cannot submit a panic.")
        if not guest.is_active:
            raise ValueError("Guest has left the room.")
        self.time_stamp = time_stamp            


@loginmanager.user_loader
def load_user(userid):
    return User.query.filter(User.id == userid).first()


def init_db():
    """ Run once to create tables """
    with app.app_context():
        db.create_all()
        default_user = User('default', 'default')
        db.session.add(default_user)
        db.session.add(Room('default', default_user))
        db.session.commit()
