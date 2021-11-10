from flask import session, render_template, url_for, flash, redirect, request, current_app
from flask_login import login_required, current_user
from . import main
from .forms import NameForm, EditProfileForm, AdminLevelEditProfileForm, CompositionForm
from .. import db
from ..models import Role, User, Permission, load_user, Composition
from ..decorators import admin_required, permission_required


@main.route('/', methods=["GET", "POST"])
def index():
    form = CompositionForm()
    if current_user.can(Permission.PUBLISH) \
            and form.validate_on_submit():
        composition = Composition(
            release_type=form.release_type.data,
            title=form.title.data,
            description=form.description.data,
            artist=current_user._get_current_object())
        db.session.add(composition)
        db.session.commit()
        composition.generate_slug()
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
            error_out=False)
    compositions = pagination.items
    return render_template('index.html', form=form, compositions=compositions, pagination=pagination)

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

@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = Composition.query.order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
            error_out=False)
    compositions = pagination.items
    compositions = user.compositions
    return render_template('user.html', user=user, compositions=compositions)

@main.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.bio = form.bio.data
        db.session.add(current_user._get_current_object())
        db.session.commit()
        flash('You successfully updated your profile! Looks great.')
        return redirect(url_for('.user', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.bio.data = current_user.bio
    return render_template('edit_profile.html', form=form)

@main.route('/editprofile/<int:id>', methods=["GET", "POST"])
@login_required
@admin_required
def admin_edit_profile(id):
    form = AdminLevelEditProfileForm()
    user = User.query.filter_by(id=id).first_or_404()
    if form.validate_on_submit():
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.name = form.name.data
        user.location = form.location.data
        user.bio = form.bio.data
        user.role = Role.query.filter_by(id=form.role.data).first()
        db.session.add(user)
        db.session.commit()
        flash(f'You successfully updated {user.username}\'s profile.')
        return redirect(url_for('.user', username=user.username))
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.bio.data = user.bio
    return render_template('editprofile.html', form=form)

@main.route('/composition/<slug>')
def composition(slug):
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    slug = composition.slug
    return render_template('composition.html', compositions=[composition], slug=slug)

@main.route('/edit/<slug>', methods=["GET", "POST"])
@login_required
def edit_composition(slug):
    form = CompositionForm()
    composition = composition = Composition.query.filter_by(slug=slug).first_or_404()
    if form.validate_on_submit():
        composition.release_type=form.release_type.data
        composition.title=form.title.data
        composition.description=form.description.data
        composition.artist=composition.artist
        composition.slug=None
        db.session.add(composition)
        db.session.commit()
        composition.generate_slug()
        flash(f'You successfully updated your composition.')
        return redirect(url_for('.composition', slug=composition.slug))
    form.release_type.data=composition.release_type
    form.title.data=composition.title
    form.description.data=composition.description
    return render_template('edit-composition.html', form=form)
