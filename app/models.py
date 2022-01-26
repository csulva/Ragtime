import re
from flask.helpers import url_for
from flask_login.mixins import AnonymousUserMixin
from sqlalchemy.orm import backref
from . import db
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer, exc
from flask import current_app
from datetime import datetime
import hashlib
import bleach
from app.exceptions import ValidationError

# Quantifying Role Permissions
class Permission:
    FOLLOW = 1
    REVIEW = 2
    PUBLISH = 4
    MODERATE = 8
    ADMIN = 16

# Database table "roles"
class Role(db.Model):
    __tablename__ = 'roles'
    # Table columns
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)

    # This relationship enables users to access roles
    users = db.relationship('User', backref='role', lazy='dynamic')
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)

    # Role set to permission 0 unless otherwise specified (such as in the insert_roles() static method below)
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    def __repr__(self):
        """Returns name of the role.

        Returns:
            String: "Role: name of the role"
        """
        return f'<Role: {self.name}>'

    def add_permission(self, perm):
        """Adds specified permission to a provided user.

        Args:
            perm (int): The integer related to specific permissions (see above Permissions class)
        """
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        """Removes a given permission from the provided user. User must already have that role.

        Args:
            perm (int): The integer related to specific permissions (see above Permissions class)
        """
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        """Resets the user's permissions to 0, or no permissions.
        """
        self.permissions = 0

    def has_permission(self, perm):
        """Returns True or False if user has given perm, or not.

        Args:
            perm (int): The integer related to specific permissions (see above Permissions class)
        """
        return self.permissions & perm == perm

    @staticmethod
    def insert_roles():
        """Creates roles below and adds them to the database.
        """
        roles = {
            'User':             [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH],
            'Moderator':        [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE],
            'Administrator':    [Permission.FOLLOW,
                                 Permission.REVIEW,
                                 Permission.PUBLISH,
                                 Permission.MODERATE,
                                 Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            # see if role is already in table
            role = Role.query.filter_by(name=r).first()
            if role is None:
                # it's not so make a new one
                role = Role(name=r)
            role.reset_permissions()
        # add whichever permissions the role needs
            for perm in roles[r]:
                role.add_permission(perm)
            # if role is the default one, default is True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

# Relationship table "follows" -- one-to-many -- connects User to Users through follower and following
class Follow(db.Model):
    __tablename__ = 'follows'

    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    following_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Database table "users"
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Required for registration
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(128))

    # Foreign key to "roles" table
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    # After registering, must confirm email
    confirmed = db.Column(db.Boolean, default=False)

    # Editable in user profile page
    name = db.Column(db.String(64))
    location = db.Column(db.String(64))
    bio = db.Column(db.Text())

    last_seen = db.Column(db.DateTime(), default=datetime.utcnow) # Automatically updates
    avatar_hash = db.Column(db.String(32)) # Profile image - randomized based on email

    # Relationship to compositions table
    compositions = db.relationship('Composition', backref='artist', lazy='dynamic')

    # Who the user is following
    following = db.relationship('Follow',
                foreign_keys=[Follow.follower_id],
                backref=db.backref('follower', lazy='joined'),
                lazy='dynamic',
                cascade='all, delete-orphan')

    # Who is following the user
    followers = db.relationship('Follow',
                foreign_keys=[Follow.following_id],
                backref=db.backref('following', lazy='joined'),
                lazy='dynamic',
                cascade='all, delete-orphan')

    def __init__(self, **kwargs):
        """Creates user role automatically upon registration of new user. Users set to follow themselves
        upon registration as well.
        """
        super().__init__(**kwargs)
        if self.role is None:
            if self.username == current_app.config['RAGTIME_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        if self.email is not None and self.avatar_hash is None:
            self.avatar_hash = self.email_hash()
        self.follow(self)

    # Ensures unable to read password once created -- must use "verify_password" function
    @property
    def password(self):
        raise AttributeError('Password is not a readable attribute')

    # Shows compositions of those the user follows
    @property
    def followed_compositions(self):
        return Composition.query.join(Follow, Follow.following_id == Composition.artist_id) \
            .filter(Follow.follower_id == self.id)

    # Ensures password is secured with password hash
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        """Returns True if password entered matches the user's password.
        Returns False if password entered does not match the user's password.

        Args:
            password (string): Check if the argument entered is indeed the correct password.
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Returns User: username
        """
        return f'<User: {self.username}>'

    def generate_confirmation_token(self, expiration_sec=15000):
        """Generates confirmation token so that when a new user registers on the site,
        an email will be sent with the token, to confirm the user.

        Args:
            expiration_sec (int, optional): Token expires in 250 minutes. Defaults to 15000 seconds.

        Returns:
            string: Unique token string
        """
        s = Serializer(current_app.secret_key, expiration_sec)
        x = s.dumps({'confirm_id': self.id}).decode('utf-8')
        return x

    def confirm(self, token):
        """Confirms user in the database, user table. Returns True if user is confirmed
        based on the token generated for their account.

        Args:
            token (string): Unique token string to confirm account.
        """
        s = Serializer(current_app.secret_key)
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm_id') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def can(self, perm):
        """Returns True if user can perform a permission (perm) provided, False if not.

        Args:
            perm (int): permission defined by an integer in the Permissions table
        """
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        """Returns True if the user has the Administrator role, False if not.
        """
        return self.can(Permission.ADMIN)

    @staticmethod
    def make_new_users_user_role():
        """If users have no current roles, this function ensures they are created as a User role.
        """
        for u in User.query.all():
            if u.role == None:
                u.role = Role.query.filter_by(default=True).first()
                db.session.commit()

    @staticmethod
    def add_self_follows():
        """All users follow themselves, therefore can view their own compositions.
        """
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def ping(self):
        """When the user is active, their last_seen column updates to now.
        """
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        db.session.commit()

    def email_hash(self):
        """Returns random string/hash based on user's email, where the user's avatar/profile image can be created.
        """
        return hashlib.md5(self.email.lower().encode('utf-8')).hexdigest()

    def unicornify(self, size=128):
        """Generates user profile image/avatar based on email/email hash.

        Args:
            size (int, optional): Size of the image. Defaults to 128px.

        Returns:
            string: Image URL from Unicornify API
        """
        url = 'https://unicornify.pictures/avatar'
        hash = self.avatar_hash or self.email_hash()
        return f'{url}/{hash}?s={size}'

    def follow(self, user):
        """Lets user follow another user.

        Args:
            user (class): A user in the database
        """
        if not self.is_following(user):
            f = Follow(follower=self, following=user)
            db.session.add(f)

    def unfollow(self, user):
        """Lets user unfollow another user

        Args:
            user (class): A user in the database
        """
        f = self.following.filter_by(following_id=user.id).first()
        if f:
            db.session.delete(f)

    def is_following(self, user):
        """Checks if current user is following the user provided in calling the function

        Args:
            user (class): A user in the database
        """
        if user.id is None:
            return False
        return self.following.filter_by(following_id=user.id).first() is not None

    def is_a_follower(self, user):
        """Checks if the user provided in the function is a follower of the current user

        Args:
            user (class): A user in the database
        """
        if user.id is None:
            return False
        return self.followers.filter_by(follower_id=user.id).first() is not None

    def generate_auth_token(self, expiration_sec):
        s = Serializer(current_app.config['SECRET_KEY'], expires_in=expiration_sec)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return None
        return User.query.get(data['id'])

    def to_json(self):
        """Returns json data as a dictionary for user information
        """
        json_user = {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'last seen': self.last_seen,
            'compositions_url': url_for('api.get_user_compositions', id=self.id),
            'followed_compositions_url': url_for('api.get_user_followed', id=self.id),
            'composition count': self.compositions.count(),
        }
        return json_user

# Database table "compositions"
class Composition(db.Model):
    __tablename__ = 'compositions'
    # Primary key
    id = db.Column(db.Integer, primary_key=True)

    # Info for compositions
    release_type = db.Column(db.Integer)
    title = db.Column(db.String(64))
    description = db.Column(db.Text)

    timestamp = db.Column(db.DateTime,
        index=True, default=datetime.utcnow)

    # Foreign key to see which user the composition belongs to
    artist_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    description_html = db.Column(db.Text)
    slug = db.Column(db.String(128), unique=True) # Used in the URL of the composition

    @staticmethod
    def on_changed_description(target, value, oldvalue, initiator):
        """Updates description when it is changed, and cleans old description information
        """
        allowed_tags = ['a']
        html = bleach.linkify(bleach.clean(value,
                                           tags=allowed_tags,
                                           strip=True))
        target.description_html = html

    def generate_slug(self):
        """Creates random string slug associated with the composition, used in URL of the composition
        """
        self.slug = f"{self.id}-" + re.sub(r'[^\w]+', '-', self.title.lower())
        db.session.add(self)
        db.session.commit()

    def to_json(self):
        """Returns json data as a dictionary for the composition information
        """
        json_composition = {
            'url': url_for('api.get_composition', id=self.id),
            'release_type': self.release_type,
            'title': self.title,
            'description': self.description,
            'description_html': self.description_html,
            'timestamp': self.timestamp,
            'artist_url': url_for('api.get_user', id=self.artist.id),
        }
        return json_composition

    @staticmethod
    def from_json(json_composition):
        """Returns information and creates composition from json data provided if composition is created with APIs

        Args:
            json_composition (dict): json dict of composition information

        Raises:
            ValidationError: If the data returns None, it will raise a Validation Error
        """
        release_type = json_composition.get('release_type')
        title = json_composition.get('title')
        description = json_composition.get('description')
        if release_type is None:
            raise ValidationError('Composition must have a release type.')
        if title is None:
            raise ValidationError('Composition must have a title.')
        if description is None:
            raise ValidationError('Composition must have a description.')

        # Creates composition in the database
        try:
            return Composition(release_type=release_type, title=title, description=description)
        except TypeError as e:
            # Needs all information above to complete the creation of composition
            raise ValidationError(str(e))


db.event.listen(Composition.description,
                'set',
                Composition.on_changed_description)

# Anonymous user class
class AnonymousUser(AnonymousUserMixin):
    def can(self, perm):
        """Anonymous user has no permissions, so it returns False

        Args:
            perm (int): permission defined by an integer in the Permissions table

        """
        return False

    def is_administrator(self):
        """Anonymous user is not an administrator, so it returns False
        """
        return False

# Quantifying composition release type
class ReleaseType:
    SINGLE = 1
    EXTENDED_PLAY = 2
    ALBUM = 3

# Manages anonymous user class
login_manager.anonymous_user = AnonymousUser

# Loads user based on id
@login_manager.user_loader
def load_user(user_id):
    """Returns user based on their id provided

    Args:
        user_id (int): the id of the user
    """
    return User.query.get(int(user_id))