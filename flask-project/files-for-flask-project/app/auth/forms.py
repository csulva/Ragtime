from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, Email

class LoginForm(FlaskForm):
    email = StringField('Email:', validators=[DataRequired(), Length(64), Email()])
    password = PasswordField('Password:', validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField('Log In')