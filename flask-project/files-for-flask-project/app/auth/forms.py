from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField('Log In')

class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    username = StringField('Username:', validators=[DataRequired(), Length(1, 64), Regexp('^[A-Za-z][A-Za-z0-9_.]*$', 0,
                   'Usernames must have only letters, numbers, dots, or underscores',
        )])
    password = PasswordField('Password', validators=[DataRequired(), EqualTo('password_confirm', message='Passwords do not match.'
        )])
    password_confirm = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField('Register')

    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists.')

class ChangeEmail(FlaskForm):
    email = StringField("Old Email", validators=[DataRequired(), Email()])
    new_email = StringField("New Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def validate_email(self, field):
        if User.query.filter_by(new_email=field.data).first():
            raise ValidationError('Email already registered.')

class ChangePassword(FlaskForm):
    password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired(), EqualTo('new_password_confirm', message='Passwords do not match.'
        )])
    new_password_confirm = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")
