from flask import session, render_template, url_for, flash, redirect
from flask_login import login_required
from . import main
from .forms import NameForm
from .. import db
from ..models import Role, User, Permission
from ..decorators import admin_required, permission_required


@main.route('/', methods=["GET", "POST"])
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
        return redirect(url_for('.index'))
    return f""" {render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))}
    <p><a href="http://127.0.0.1:5000/songs">Song List</a></p>
    <p><a href="http://127.0.0.1:5000/about">About Me</a></p>
    """

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    return "Welcome, administrator!"

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "Greetings, moderator!"
