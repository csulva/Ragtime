# Import FlaskForm as child class
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, ValidationError
from wtforms.fields.core import BooleanField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from app.models import User

# Login form asks for email, password, remember_me button
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Length(1, 64), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField()
    submit = SubmitField('Log In')

# Registration form to register an account. Passwords must match
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
        """Checks to see if email has/has not already been registered and saved in the database.

        Args:
            field (string): The field is what is entered in the form, in this case, the email address
            to check if it exists already or not.

        Raises:
            ValidationError: Returns "Email already exists" if True
        """
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered.')

    def validate_username(self, field):
        """Checks to see if username has/has not already been registered and saved in the database.

        Args:
            field (string): The field is what is entered in the form, in this case, a username
            to check if it exists already or not.

        Raises:
            ValidationError: Returns "Username already exists" if True
        """
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('Username already exists.')

# Change email form, requires old email
class ChangeEmail(FlaskForm):
    old_email = StringField("Old Email", validators=[DataRequired(), Email()])
    email = StringField("New Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Submit")

    def validate_email(self, field):
        """Checks to see if the new email given exists or not, in order to change it

        Args:
            field (string): The field is what is entered in the form, in this case, an email
            to check if it exists already or not.

        Raises:
            ValidationError: Returns "Email already registered by another user." if True
        """
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('Email already registered by another user.')

# Change password form, requires old password to match
class ChangePassword(FlaskForm):
    password = PasswordField("Old Password", validators=[DataRequired()])
    new_password = PasswordField('Password', validators=[DataRequired(), EqualTo('new_password_confirm', message='Passwords do not match.'
        )])
    new_password_confirm = PasswordField('Confirm Password:', validators=[DataRequired()])
    submit = SubmitField("Submit")
