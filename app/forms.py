from wtforms import TextField, PasswordField, HiddenField, validators
from flask.ext.wtf import Form


class SigninForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
    next = HiddenField('Next')


class RegistrationForm(Form):
    username = TextField('Username', [validators.required()])
    password = PasswordField('Password', [validators.required()])
    password2 = PasswordField('Password2', [validators.required()])
    
