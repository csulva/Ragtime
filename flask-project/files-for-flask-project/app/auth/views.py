from flask import render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login.utils import logout_user
from . import auth
from app import login_manager
from flask_login import login_required, login_user, current_user
from .forms import LoginForm, RegistrationForm
from app.models import User
from app.email import send_email
from .. import db

@auth.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        name_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(email=name_entered).first()
        #verify email exists User is None or not
        if user is not None:
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
        username_entered = form.username.data
        email_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(username=username_entered).first()
        if user is None:
            user = User(username=username_entered, email=email_entered, password=password_entered)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            confirmation_link = url_for('auth.confirm', token=token, _external=True)
            send_email(user.email, 'Welcome to Ragtime!', 'mail/welcome', user=user)
            send_email(user.email, 'Confirm your account with Ragtime', 'auth/confirm',  confirmation_link=confirmation_link)
            send_email('chrservices15@gmail.com', 'A new user has been created!', 'mail/new_user', user=user)
            flash('Thanks for registering!')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('auth.register'))
    return render_template('auth/register.html', form=form)

@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        flash('You are already confirmed.')
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        db.session.commit()
        flash('You have confirmed your account! Thank you.')
        return redirect(url_for('main.index'))
    else:
        flash('Whoops, that confirmation link either expired or isn\'t valid.')
        return redirect(url_for('main.index'))

@auth.before_app_request
def before_request():
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request != 'static' \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/resend_confirmation')
def resend_confirmation():
    user = current_user
    token = user.generate_confirmation_token()
    confirmation_link = url_for('auth.confirm', token=token, _external=True)
    send_email(user.email, 'Confirm your account with Ragtime', 'auth/confirm', user=user, confirmation_link=confirmation_link)
    flash('Message sent! Check your email for the new confirmation link.')
    return redirect(url_for('auth.unconfirmed'))
