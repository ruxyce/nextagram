from flask import Blueprint, render_template, request, redirect, url_for, flash

from werkzeug.security import generate_password_hash

from flask_login import login_required, current_user, login_user

from models.user import User
from models.post import Post, Like

import re

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route('/', methods=['POST'])
def create():
    username = request.form['username'].lower()
    email = request.form['email'].lower()

    dupe_username = User.get_or_none(User.username == username)
    dupe_email = User.get_or_none(User.email == email)

    if not dupe_username and not dupe_email:

        pattern = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        # validate_email = re.match(pattern, email)

        characters = "abcdefghijklmnopqrstuvwxyz0123456789_."
        # validate_username = all(char in characters for char in username)

        # if not validate_email:
        if not re.match(pattern, email):
            flash("Please enter a valid email address.")
            return redirect(url_for('sessions.signup'))

        # if not validate_username:
        if not all(char in characters for char in username):
            flash("Username criteria not met.")
            return redirect(url_for('sessions.signup'))

        password = request.form['password']
        pw_pattern = "^[A-Za-z0-9._@-]{8,32}$"
        ym_pattern = ".*your.*mom.*|.*mom.*your.*"
        if not re.match(pw_pattern, password) or not re.match(ym_pattern, password.lower()):
            flash("Password criteria not met.")
            return redirect(url_for('sessions.signup'))

        password = generate_password_hash(password)
        user = User.create(username=username, email=email, password=password)
        login_user(user)

        return redirect(url_for('home'))
    
    elif dupe_email:
        flash('That email address is already registered.')
        return redirect(url_for('sessions.signup'))

    elif dupe_username:
        flash('That username is already taken.')
        return redirect(url_for('sessions.signup'))


@users_blueprint.route('/<username>', methods=["GET","POST"])
def userpage(username):
    user = User.get_or_none(User.username == username)
    if user:
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('user_posts.html', user=user, following=following)
    else:
        return render_template('error.html',
            error_header='User Not Found',
            error_text="Who you're looking for does not exist! :("
        )

@users_blueprint.route('/all', methods=["GET","POST"])
def all_users():
    users = User.select().order_by(User.id).prefetch(Post, Like)
    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('all_users.html', users=users, following=following)

@users_blueprint.route('/search')
def search():
    term = request.args.get('q').lower()
    users = User.select().where(User.username.contains(term))
    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('all_users.html', users=users, following=following, term=term)

@users_blueprint.route('/<username>/following', methods=["GET"])
def following(username):
    user = User.get_or_none(User.username == username)

    if user:
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('following.html', user=user, following=following)
    
    return render_template('error.html',
        error_header='User Not Found',
        error_text="Who you're looking for does not exist! :("
    )

@users_blueprint.route('/<username>/followers', methods=["GET"])
def followers(username):
    user = User.get_or_none(User.username == username)

    if user:
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('followers.html', user=user, following=following)

    return render_template('error.html',
        error_header='User Not Found',
        error_text="Who you're looking for does not exist! :("
    )

@users_blueprint.route('/follow/<id>', methods=["POST"])
@login_required
def follow(id):
    current_user.follow(id)

    if 'next' in request.form:
        return redirect(request.form['next'])

    return redirect(url_for('home'))

@users_blueprint.route('/unfollow/<id>', methods=["POST"])
@login_required
def unfollow(id):
    current_user.unfollow(id)

    if 'next' in request.form:
        return redirect(request.form['next'])

    return redirect(url_for('home'))

@users_blueprint.route('/newww', methods=["GET"])
def newww():
    return render_template('users/newww.html')