from flask import Blueprint, render_template, request, redirect, url_for, flash

from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename

from flask_login import login_required, current_user, login_user

from models.user import User, Relationship
from models.post import Post, Like, AvatarKey

from helpers import Config, s3

import re
import random
import string

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route('/new', methods=['GET','POST'])
def new():
    return redirect(url_for('sessions.signup_bypass_url'))

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
            return redirect(url_for('users.new'))

        # if not validate_username:
        if not all(char in characters for char in username):
            flash("Username criteria not met.")
            return redirect(url_for('users.new'))

        password = request.form['password']
        pw_pattern = "^[A-Za-z0-9._@-]{8,32}$"
        ym_pattern = ".*your.*mom.*|.*mom.*your.*"
        if not re.match(pw_pattern, password) or not re.match(ym_pattern, password.lower()):
            flash("Password criteria not met.")
            return redirect(url_for('users.new'))

        password = generate_password_hash(password)
        user = User.create(username=username, email=email, password=password)
        login_user(user)

        return redirect(url_for('home'))
    
    elif dupe_email:
        flash('That email address is already registered.')
        return redirect(url_for('users.new'))

    elif dupe_username:
        flash('That username is already taken.')
        return redirect(url_for('users.new'))

@users_blueprint.route('/edit')
@login_required
def edit():
    return render_template('users/edit.html')

def allowed_file(file):
    return 'image' in file.content_type

@users_blueprint.route("/update", methods=["POST"])
@login_required
def update():
    if "user_file" not in request.files:
        return "No user_file key in request.files"
    file = request.files["user_file"]
    if file.filename == "":
        return "Please select a file"
    if not allowed_file(file):
        return "Invalid file extension"
    if file:
        file.filename = secure_filename(file.filename)

        dupe = True
        while dupe == True:
            filename = ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))
            retrieve = AvatarKey.get_or_none(AvatarKey.filename == filename)
            if retrieve:
                continue
            else:
                AvatarKey.create(filename = filename)
                dupe = False
        prepend = 'avatars/'

        try:
            s3.upload_fileobj(
                file,
                Config.S3_BUCKET,
                prepend+filename,
                ExtraArgs={
                    "ACL": "public-read",
                    "ContentType": file.content_type
                }
            )
        
        except Exception as e:
            print("Something Happened: ", e)
            return e
        
        query = User.update(avatar=filename).where(User.id == current_user.id)
        query.execute()

        return redirect(url_for('users.show', username=current_user.username))

    else:
        return redirect("/")

@users_blueprint.route('/<username>', methods=["GET","POST"])
def show(username):
    user = User.get_or_none(User.username == username)
    if user:
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('users/show.html', user=user, following=following)
    else:
        return render_template('error.html',
            error_header='User Not Found',
            error_text="Who you're looking for does not exist! :("
        )

@users_blueprint.route('/all', methods=["GET","POST"])
def index():
    users = User.select().order_by(User.id).prefetch(Post, Like)
    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('users/index.html', users=users, following=following)

@users_blueprint.route('/search')
def search():
    term = request.args.get('q').lower()
    users = User.select().where(User.username.contains(term))
    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('users/index.html', users=users, following=following, term=term)

@users_blueprint.route('/<username>/following', methods=["GET"])
def show_following(username):
    user = User.get_or_none(User.username == username)

    if user:
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('users/show_following.html', user=user, following=following)
    
    return render_template('error.html',
        error_header='User Not Found',
        error_text="Who you're looking for does not exist! :("
    )

@users_blueprint.route('/<username>/followers', methods=["GET"])
def show_followers(username):
    user = User.get_or_none(User.username == username)

    if user:
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('users/show_followers.html', user=user, following=following)

    return render_template('error.html',
        error_header='User Not Found',
        error_text="Who you're looking for does not exist! :("
    )

@users_blueprint.route('/follow/<id>', methods=["POST"])
@login_required
def follow(id):
    user = User.get_by_id(id)
    relationship = Relationship.get_or_none(Relationship.from_user == current_user.id, Relationship.to_user == user.id)
    # Dupe validate to be refined

    if not relationship:
        
        if user.is_private:
            flash(f"A follow request has been sent to {user.username} and now awaiting approval.")
    
        else:
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

@users_blueprint.route('requests', methods=["GET"])
@login_required
def requests():
    return "ASF"