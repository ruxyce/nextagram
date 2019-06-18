from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from werkzeug.security import check_password_hash

from models.user import User

from flask_login import login_user, logout_user, login_required, current_user

sessions_blueprint = Blueprint('sessions',
                            __name__,
                            template_folder='templates')

@sessions_blueprint.route('/signup', methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('signup.html')

@sessions_blueprint.route('/login', methods=['GET','POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('home'))
    return render_template('login.html')

@sessions_blueprint.route('/auth', methods=['POST'])
def auth():
    username = request.form['username'].lower()
    password = request.form['password']
    user = User.get_or_none(User.username == username)
    if not user:
        flash('Invalid username.')
        return redirect(url_for('sessions.login'))
    pw_check = check_password_hash(user.password, password)
    if pw_check:
        login_user(user)
        return redirect(url_for('home'))
    else:
        flash('Incorrect password.')
        return redirect(url_for('sessions.login'))

@sessions_blueprint.route('/signout', methods=["GET","POST"])
@login_required
def signout():
    logout_user()
    flash('Successfully logged out.')
    return redirect(url_for('sessions.login'))

