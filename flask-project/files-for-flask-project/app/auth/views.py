from flask import render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login.utils import logout_user
from . import auth
from app import login_manager
from flask_login import login_required, login_user, current_user
from .forms import LoginForm
from app.models import User

@auth.route('/register')
def register():
    return render_template('register.html')

@auth.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    username = request.form.get('username')
    password = request.form.get('password')
    form = LoginForm()
    if form.validate_on_submit():
        name_entered = form.name.data
        user = User.query.filter_by(username=name_entered).first()
        login_user(user)
        flash(f'Welcome {form.username.data}!')
        return redirect(url_for('.index'))
    else:
        flash('Try again')
    return render_template('auth/login.html', form=form)

@auth.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('main.index'))