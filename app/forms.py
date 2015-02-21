from wtforms import TextField, PasswordField, validators
from flask.ext.wtf import Form


class SigninForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])


class RegistrationForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
    password2 = PasswordField('Password2', [validators.required()])
    
