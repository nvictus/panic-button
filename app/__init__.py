import os
from flask import Flask


### CONFIG VARS ###
SECRET_KEY = os.environ.get('SECRET_KEY', 'blah')
HERE = os.path.abspath(__file__)
DB_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(HERE), 
        os.path.pardir, 
        'test.db'
    )
)


### INITIALIZE APP ###
app = Flask(__name__)
app.secret_key = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + DB_PATH


### PLUGINS ###
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager
from flask.ext.bcrypt import Bcrypt

# initialize flask-sqlalchemy
db = SQLAlchemy()
db.init_app(app)

# initialize flask-login
loginmanager = LoginManager()
loginmanager.init_app(app)
loginmanager.login_view = "signin"

# initialize flask-bcrypt
bcrypt = Bcrypt(app)

