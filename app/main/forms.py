# Import FlaskForm as the child form
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, TextAreaField
from wtforms import validators
from wtforms.fields.core import BooleanField, SelectField
from wtforms.validators import DataRequired, Length
from app.models import ReleaseType

# Edit profile form, asks user name, location, bio, with submit button
class EditProfileForm(FlaskForm):
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

# Edit profile form allowing administrator to edit a user's profile.
class AdminLevelEditProfileForm(FlaskForm):
    username = StringField("Username", validators=[Length(0, 64)]) # Admin can change username
    confirmed = BooleanField("Confirmed") # Admin can confirm
    role = SelectField(u'Role', choices=[(1, 'User'), (2, 'Moderator'), (3, 'Administrator')], coerce=int)
    name = StringField("Name", validators=[Length(0, 64)])
    location = StringField("Location", validators=[Length(0, 64)])
    bio = TextAreaField("Bio")
    submit = SubmitField("Submit")

# To post a composition: needs release_type, title, and description
class CompositionForm(FlaskForm):
    release_type = SelectField("Release Type", coerce=int, default=ReleaseType.SINGLE, validators=[DataRequired()])
    title = StringField("Title", validators=[DataRequired()])
    description = TextAreaField("Tell us about your composition")
    submit = SubmitField("Submit")

    def __init__(self, *args, **kwargs):
        """Allows dropdown choices for release type column: Single, EP, or Album
        """
        super().__init__(*args, **kwargs)
        self.release_type.choices = [
            (ReleaseType.SINGLE, 'Single'),
            (ReleaseType.EXTENDED_PLAY, 'EP'),
            (ReleaseType.ALBUM, 'Album')]



