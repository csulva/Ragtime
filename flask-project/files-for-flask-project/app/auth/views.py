from flask import render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login.utils import logout_user
from . import auth
from app import login_manager
from flask_login import login_required, login_user, current_user
from .forms import LoginForm, RegistrationForm
from app.models import User
from .. import db

@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(email=name_entered).first()
        if user.verify_password(password_entered) == True:
            login_user(user, form.remember_me.data)
            next = request.args.get('next')
            if next is None or not next.startswith('/'):
                next = url_for('main.index')
            return redirect(next)
    else:
        flash('Username or password is invalid')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        #Do I need this?
        username_entered = form.username.data
        email_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(username=username_entered).first()
        if user is None:
            user = User(username=username_entered, email=email_entered, password=password_entered)
            db.session.add(user)
            db.session.commit()
            flash('Thanks for registering!')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)