from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms import validators
from wtforms.fields.core import BooleanField, SelectField
from wtforms.validators import DataRequired, Length

class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class DateForm(FlaskForm):
    date = DateField('What is your birthday (month, day)', format='%m-%d', validators=[DataRequired()])
    submit = SubmitField("Submit")

class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

class AdminLevelEditProfileForm(FlaskForm):
    username = StringField("Username", validators=[Length(0, 64)])
    confirmed = BooleanField("Confirmed")
    role = SelectField(u'Role', choices=[(1, 'User'), (2, 'Moderator'), (3, 'Administrator')], coerce=int)
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

