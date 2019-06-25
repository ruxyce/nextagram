from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from werkzeug.security import check_password_hash

from models.user import User

from instagram_web.helpers.google_oauth import oauth

from flask_login import login_user, logout_user, login_required, current_user

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

@sessions_blueprint.route('/signup', methods=['GET','POST'])
def signup_bypass_url():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('users/new.html')

@sessions_blueprint.route('/login', methods=['GET','POST'])
def new():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('sessions/new.html')

@sessions_blueprint.route('/oauth_login', methods=['POST'])
def oauth_login():
    target = url_for('sessions.authorize_google', _external=True)
    return oauth.google.authorize_redirect(target)

@sessions_blueprint.route('/authorize/google', methods=['GET','POST'])
def authorize_google():
    token = oauth.google.authorize_access_token()
    email = oauth.google.get('https://www.googleapis.com/oauth2/v2/userinfo').json()['email']
    # this is a pseudo method, you need to implement it yourself

    user = User.get_or_none(User.email == email.lower())
    if not user:
        flash("That email address is not registered here!")
        return redirect(url_for('sessions.new'))

    login_user(user)
    return redirect(url_for('posts.index'))

@sessions_blueprint.route('/auth', methods=['POST'])
def create():
    username = request.form['username'].lower()
    password = request.form['password']
    user = User.get_or_none(User.username == username)
    if not user:
        flash('Invalid username.')
        return redirect(url_for('sessions.new'))
    pw_check = check_password_hash(user.password, password)
    if pw_check:
        login_user(user)
        return redirect(url_for('posts.index'))
    else:
        flash('Incorrect password.')
        return redirect(url_for('sessions.new'))

@sessions_blueprint.route('/signout', methods=["GET","POST"])
@login_required
def delete():
    logout_user()
    flash('Successfully logged out.')
    return redirect(url_for('sessions.new'))

