from flask import render_template, flash, redirect, request
from flask.helpers import url_for
from flask_login.utils import logout_user
from . import auth
from app import login_manager
from flask_login import login_required, login_user, current_user
from .forms import LoginForm, RegistrationForm, ChangeEmail, ChangePassword
from app.models import User
from app.email import send_email
from .. import db

@auth.route('/login', methods=["GET", "POST"])
def login():
    """Function to enable users to login

    Returns:
        auth/login.html file: Loads the login.html page displaying the login form.
    """
    form = LoginForm()
    # Activates the POST request to log the user in
    if form.validate_on_submit():
        name_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(email=name_entered).first()
        # Verify email exists User is None or not
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
    """Function to log the user out of the session.

    Returns:
        Redirects to index/home page
    """
    logout_user()
    flash('You have been logged out successfully.')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=["GET", "POST"])
def register():
    """Function to let a user register their account to be added to database, login, post.

    Returns:
        auth/register.html file: Renders the registration form and template
    """
    form = RegistrationForm()
    # Activates the POST request to register account
    if form.validate_on_submit():
        username_entered = form.username.data
        email_entered = form.email.data
        password_entered = form.password.data
        user = User.query.filter_by(username=username_entered).first()
        # Check to make sure username is not already taken
        if user is None:
            user = User(username=username_entered, email=email_entered, password=password_entered)
            db.session.add(user)
            db.session.commit()
            token = user.generate_confirmation_token()
            confirmation_link = url_for('auth.confirm', token=token, _external=True)
            # Send email upon registering
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
    """Function to confirm the user's email address.

    Args:
        token (string): Token generated after registering email, or upon request.
        Token is placed in a confirmaiton link that is sent to the user's email address in the database.

    Returns:
        Redirect to index/home page.
    """
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
    """Decorates functions that redirects user to the unconfirmed page
    if the user's account is unconfirmed.

    Returns:
        Redirects to unconfirmed html page if user is unconfirmed.
    """
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
            return redirect(url_for('auth.unconfirmed'))

@auth.route('/unconfirmed')
def unconfirmed():
    """Landing page for users who are signed in but uncofirmed.

    Returns:
        auth/unconfirmed.html file: Renders unconfirmed page.
    """
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    return render_template('auth/unconfirmed.html', user=current_user)

@auth.route('/resend_confirmation')
def resend_confirmation():
    """Function to resend confirmation link to the user's email

    Returns:
        Redirects to auth/unconfirmed html page
    """
    user = current_user
    token = user.generate_confirmation_token()
    confirmation_link = url_for('auth.confirm', token=token, _external=True)
    send_email(user.email, 'Confirm your account with Ragtime', 'auth/confirm', user=user, confirmation_link=confirmation_link)
    flash('Message sent! Check your email for the new confirmation link.')
    return redirect(url_for('auth.unconfirmed'))

@auth.route('/change-email', methods=["GET", "POST"])
@login_required
def change_email():
    """Function to allow users to change their email address.

    Returns:
        Renders change email form unless POST request--redirects to login page
    """
    form = ChangeEmail()
    # Activates the POST request to change the user's email address
    if form.validate_on_submit():
        old_email = form.old_email.data
        email = form.email.data
        # Checks if old email matches in order to change
        if current_user.email == old_email:
            current_user.email = email
            db.session.add(current_user)
            db.session.commit()
            flash('You have successfully changed your email address.')
            return redirect(url_for('auth.login'))
        else:
            flash('Your old email does not match our records. Please try again.')
    return render_template('auth/change-email.html', form=form)

@auth.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """Function to allow users to change their password

    Returns:
        Renders change password form, unless POST request--redirects to login page
    """
    form = ChangePassword()
    # Activates the POST request to change the user's password
    if form.validate_on_submit():
        password = form.password.data
        new_password = form.new_password.data
        # Checks if old password matches in order to change
        if current_user.verify_password(password) == True:
            current_user.password = new_password
            db.session.add(current_user)
            db.session.commit()
            flash('Your password has been changed successfully.')
            return redirect(url_for('auth.login'))
        else:
            flash('Old password does not match records. Try again.')
    return render_template('auth/change-password.html', form=form)