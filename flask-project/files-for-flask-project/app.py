from flask import Flask
from flask import render_template, redirect, url_for, session, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import DataRequired
import os
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class NameForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class DateForm(FlaskForm):
    date = DateField('What is your birthday (month, day)', format='%m-%d', validators=[DataRequired()])
    submit = SubmitField("Submit")

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
bootstrap = Bootstrap(app)

app.config['SECRET_KEY'] = "keep it secret, keep it safe"
app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'sqlite:///{os.path.join(basedir, "data-dev.sqlite")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return f'<Role: {self.name}>'

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))

    def __repr__(self):
        return f'<User: {self.username}>'


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Role=Role, User=User)


@app.route('/', methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name_entered = form.name.data
        user = User.query.filter_by(username=name_entered).first()
        if user is None:
            user = User(username=name_entered)
            db.session.add(user)
            db.session.commit()
            session['known'] = False
        else:
            session['known'] = True
        session['name'] = name_entered
        flash('Great! We hope you enjoy the community')
        return redirect(url_for('index'))
    return f""" {render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))}
    <p><a href="http://127.0.0.1:5000/songs">Song List</a></p>
    <p><a href="http://127.0.0.1:5000/about">About Me</a></p>
    """

@app.route('/zodiac', methods=["GET", "POST"])
def zodiac():
    form = DateForm()
    zodiac_signs = ['Aquarius', 'Pisces', 'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn']
    if form.validate_on_submit():
        session['date'] = form.date.data
        flash(f'Your zodiac sign is... ')
        return redirect(url_for('zodiac'))
    return render_template('zodiac.html', form=form, date=session.get('date'), zodiac_signs=zodiac_signs)

@app.route('/about')
def about():
    return '<strong>Hello, my name is Chris, and I enjoy web development and music.</strong>'

@app.route('/songs')
def songs():
    songs = {"You're the Voice": "John Farnham", "Tubular Bells": "Mike Oldfield", "Black Market": "Weather Report", "A Whiter Shade of Pale": "Procol Harum"}
    return render_template('songs.html', favorite_songs=songs)

@app.route('/user/<username>')
def user(username):
    return render_template('user.html', username=username)

@app.route('/number/<number>')
def square(number):
    return f'Your number squared is: {int(number) * int(number)}'

@app.route('/derived')
def derived():
    return render_template('derived.html')

@app.errorhandler(403)
def forbidden(e):
    error_title = 'Forbidden'
    error_msg = 'You shouldn\t be here.'
    return render_template('error.html', error_title=error_title, error_msg=error_msg), 403

@app.errorhandler(404)
def page_not_found(e):
    error_title = 'Not Found'
    error_msg = 'That page doesn\'t exist.'
    return render_template('error.html', error_title=error_title, error_msg=error_msg), 404

@app.errorhandler(500)
def internal_server_error(e):
    error_title = "Internal Server Error"
    error_msg = "Sorry, we seem to be experiencing some technical difficulties"
    return render_template('error.html',
                           error_title=error_title,
                           error_msg=error_msg), 500