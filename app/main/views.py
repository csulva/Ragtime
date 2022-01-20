from flask import render_template, url_for, flash, redirect, request, current_app, make_response
from flask_login import login_required, current_user
from . import main
from .forms import EditProfileForm, AdminLevelEditProfileForm, CompositionForm
from .. import db
from ..models import Role, User, Permission, Composition
from ..decorators import admin_required, permission_required


@main.route('/', methods=["GET", "POST"])
def index():
    """Index or home page.

    Returns:
        html file: Returns index.html from the templates directory
    """
    # Renders the composition form on the home page to submit compositions
    form = CompositionForm()
    # Create compositions
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
    # Will not allow compositions to be created if user is anonymous and the form is submitted
    elif current_user.is_anonymous and form.validate_on_submit():
        flash('You must be logged in to do that.')
    # Defines which compositions to show on home page
    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_compositions
    else:
        query = Composition.query
    # Paginate the query from above to show 20 per 1 page
    pagination = query.order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
            error_out=False)
    # Convert to list
    compositions = pagination.items
    return render_template('index.html', form=form, compositions=compositions, pagination=pagination, show_followed=show_followed)

@main.route('/all')
@login_required
def show_all():
    """On the home/index page, enables users to view all compositions
    created in a paginated list. Must be logged in.

    Returns:
        Response: Response is the home page or index.html file which renders the compositions
    """
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60) # 30 days
    return resp

@main.route('/followed')
@login_required
def show_followed():
    """On the home/index page, enables users to view all compositions
    of those who the user follows. Must be logged in.

    Returns:
        Response: Response is the home page or index.html file which renders the compositions
    """
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60) # 30 days
    return resp

@main.route('/admin')
@login_required
@admin_required
def for_admins_only():
    """For administrators only. If you are an administrator, you can see this page

    Returns:
        String: On the page, will return "Welcome, administrator!"
    """
    return "Welcome, administrator!"

@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    """""For moderators only. If you are an moderator, you can see this page

    Returns:
        String: On the page, will return "Greetings, moderator!"
    """
    return "Greetings, moderator!"

@main.route('/user/<username>')
def user(username):
    """The profile page of the given user is shown

    Args:
        username (string): The user's username is provided in the function to view the user's profile

    Returns:
        user.html file: Shows the page that is the user's profile
    """
    # Search for user based on the one provided in the URL, otherwise 404 error rendered
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    # Pagination of the compositions for the particular user
    pagination = Composition.query.filter_by(artist=user).order_by(Composition.timestamp.desc()).paginate(
            page,
            per_page=current_app.config['RAGTIME_COMPS_PER_PAGE'],
            error_out=False)
    # Convert to list
    compositions = pagination.items
    return render_template('user.html', user=user, compositions=compositions, pagination=pagination)

@main.route('/edit-profile', methods=["GET", "POST"])
@login_required
def edit_profile():
    """The edit profile function renders the page where the user can edit their profile--only
    their own profile

    Returns:
        edit_profile.html file: The page where one can edit their profile
    """
    # Renders EditProfileForm on the page
    form = EditProfileForm()
    # If form is validated, it will be updated and saved in the database
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
    """Edit the profile of any user as an administrator

    Args:
        id (int): The ID of the user whose profile is being edited

    Returns:
        editprofile.html file: Which renders the edit profile page to be able to edit any user's profile
    """
    form = AdminLevelEditProfileForm()
    # Search user based on their ID or 404 error if None
    user = User.query.filter_by(id=id).first_or_404()
    # Activates the POST request to change the user's profile
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
    # Shows the current information as a GET request
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.bio.data = user.bio
    return render_template('editprofile.html', form=form)

@main.route('/composition/<slug>')
def composition(slug):
    """Function to be able to view the composition

    Args:
        slug (string): Each composition has a unique slug, and it's used to yield that particular
        composition, in this case in html format

    Returns:
        composition.html file: Shows the particular composition in an html format
    """
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    slug = composition.slug
    return render_template('composition.html', compositions=[composition], slug=slug)

@main.route('/edit/<slug>', methods=["GET", "POST"])
@login_required
def edit_composition(slug):
    """Edit the information of the composition in a form. This is the page to do that.

    Args:
        slug (string): Each composition has a unique slug, and it's used to yield that particular
        composition, in this case in html format

    Returns:
        edit-composition.html file: Renders the composition form to be able to edit it.
    """
    form = CompositionForm()
    # Searches the database for the particular composition based on the slug, otherwise returns 404
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    # Activates the POST request to change the composition information
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
        # Redirects to that composition's page
        return redirect(url_for('.composition', slug=composition.slug))
    # Shows the current information as a GET request
    form.release_type.data=composition.release_type
    form.title.data=composition.title
    form.description.data=composition.description
    return render_template('edit-composition.html', form=form)

@main.route('/delete/<slug>', methods=["GET", "POST"])
@login_required
def delete_composition(slug):
    """Function will delete the composition if the user has authorization (if it's their own)

    Args:
        slug (string): Each composition has a unique slug, and it's used to yield that particular
        composition, in this case in html format

    Returns:
        index.html file: Brings the user back to the home page once the function has been called (the composition is deleted)
    """
    # Search the composition based on slug to input into the function, else 404 error
    composition = Composition.query.filter_by(slug=slug).first_or_404()
    db.session.delete(composition)
    db.session.commit()
    flash('You have successfully deleted the composition.')
    return redirect(url_for('.index', composition=composition))

@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    """This function allows you (the user) to follow another user

    Args:
        username (string): The given username of the user you would like to follow

    Returns:
        user.html: Redirects back to the user's profile of the user you follow
    """
    # Search the database for the user based on username
    user = User.query.filter_by(username=username).first()
    # If not a user
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    # If already following that user
    if current_user.is_following(user):
        flash("Looks like you are already following that user.")
        return redirect(url_for('.user', username=username))
    # Follow user
    current_user.follow(user)
    db.session.commit()
    flash(f"You are now following {username}")
    # Redirects to the user's profile
    return redirect(url_for('.user', username=username))

@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    """This function allows you (the user) to unfollow another user

    Args:
        username (string): The given username of the user you would like to unfollow

    Returns:
        user.html: Redirects back to the user's profile of the user you unfollow
    """
    # Search the database for the user based on username
    user = User.query.filter_by(username=username).first()
    # If not a user
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    # If NOT already following that user
    if not current_user.is_following(user):
        flash("Looks like you aren't already following that user.")
        return redirect(url_for('.user', username=username))
    # Unfollow the user
    current_user.unfollow(user)
    db.session.commit()
    flash(f"You have successfully unfollowed {username}.")
    # Redirects to the user's profile
    return redirect(url_for('.user', username=username))

@main.route('/followers/<username>')
def followers(username):
    """Function returns all the followers of the user provided by the username

    Args:
        username (string): The given username of the user who has the followers

    Returns:
        followers.html file: Renders a page displaying followers of the user based on the
        username given in the function
    """
    # Search the database for the user based on the username
    user = User.query.filter_by(username=username).first()
    # If user does not exist
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    # Display followers in paginated list
    pagination = user.followers.paginate(
        page,
        per_page=current_app.config['RAGTIME_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # Convert to only follower and timestamp
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html',
                           user=user,
                           title_text="Followers of",
                           endpoint='.followers',
                           pagination=pagination,
                           follows=follows)

@main.route('/following/<username>')
def following(username):
    """Function returns all users who are followed by the user provided by the username

    Args:
        username (string): The given username of the user is following others

    Returns:
        following.html file: Renders a page displaying users who the given user is following
    """
    # Search for user in the database with the username given in the function
    user = User.query.filter_by(username=username).first()
    # If user does not exist
    if user is None:
        flash("That is not a valid user.")
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    # Display paginated list of users who the given user is following
    pagination = user.following.paginate(
        page,
        per_page=current_app.config['RAGTIME_FOLLOWERS_PER_PAGE'],
        error_out=False)
    # Convert to only follower and timestamp
    follows = [{'user': item.following, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('following.html',
                           user=user,
                           title_text="Following",
                           endpoint='.following',
                           pagination=pagination,
                           follows=follows)