from flask import Blueprint, render_template, request, redirect, url_for, flash

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from flask_login import login_required, current_user, login_user

from models.user import User, Relationship
from models.post import Post, Like, AvatarKey

from helpers import Config, s3

import re
import random
import string

reserved_keywords = ['search', 'avatar', 'update', 'update_avatar', 'edit', 'follow', 'unfollow', 'requests']

users_blueprint = Blueprint('users',
                            __name__,
                            template_folder='templates')

@users_blueprint.route('/u/new', methods=['GET','POST'])
def new():
    return redirect(url_for('sessions.signup_bypass_url'))

@users_blueprint.route('/u/create', methods=['POST'])
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
        if not all(char in characters for char in username) or len(username) < 5 or len(username) > 20:
            flash("Username criteria not met.")
            return redirect(url_for('users.new'))

        if username in reserved_keywords:
            flash("That username is unallowed.")
            return redirect(url_for('users.new'))


        password = request.form['password']
        pw_pattern = "^[A-Za-z0-9._@-]{8,32}$"
        if not re.match(pw_pattern, password):
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

@users_blueprint.route('/edit/details')
@login_required
def edit():
    return render_template('users/edit.html')

@users_blueprint.route('/edit/avatar')
@login_required
def edit_avatar():
    return render_template('users/edit_avatar.html')

def allowed_file(file):
    return 'image' in file.content_type

@users_blueprint.route("/edit/details/update", methods=["POST"])
@login_required
def update():
    
    user = User.get_or_none(User.id == current_user.id)
    if not user:
        return redirect(url_for('home'))

    verify_password = request.form['verify_password']

    if not check_password_hash(user.password, verify_password):
        flash("Password verification failed.")
        return redirect(url_for('users.edit'))

    new_username = request.form['username'].lower()
    do_update_username = False
    if new_username != user.username:
        if User.get_or_none(User.username == new_username):
            flash("That username has already been taken. Changes not saved.")
            return redirect(url_for('users.edit'))

        if len(new_username) < 5 or len(new_username) > 20:
            flash("Username must be between 5 to 20 characters. Changes not saved.")
            return redirect(url_for('users.edit'))

        characters = "abcdefghijklmnopqrstuvwxyz0123456789_."
        if not all(char in characters for char in new_username):
            flash("Invalid characters in username. Changes not saved.")
            return redirect(url_for('users.edit'))

        if new_username in reserved_keywords:
            flash("That username is unallowed.")
            return redirect(url_for('users.edit'))

        do_update_username = True

    new_email = request.form['email'].lower()
    do_update_email = False
    if new_email != user.email:
        if User.get_or_none(User.email == new_email):
            flash("That email has already been registered. Changes not saved.")
            return redirect(url_for('users.edit'))

        pattern = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
        if not re.match(pattern, new_email):
            flash("Invalid email address. Changes not saved.")
            return redirect(url_for('users.edit'))

        do_update_email = True

    new_password = request.form['password']
    do_update_password = False
    if new_password:
        if len(new_password) < 8 or len(new_password) > 20:
            flash("Password must be between 8 to 20 characters. Changes not saved.")
            return redirect(url_for('users.edit'))

        pw_pattern = "^[A-Za-z0-9._@-]{8,32}$"
        if not re.match(pw_pattern, new_password):
            flash("Password criteria not met. Changes not saved.")
            return redirect(url_for('users.edit'))

        do_update_password = True

    if do_update_username:
        user.username = new_username

    if do_update_email:
        user.email = new_email

    if do_update_password:
        user.password = generate_password_hash(new_password)

    user.save()

    if 'set_private' in request.form:
        user.set_private()

    if 'set_public' in request.form:
        user.set_public()    

    flash("Successfully updated.")
    return redirect(url_for('users.edit'))

@users_blueprint.route("/edit/avatar/update", methods=["POST"])
@login_required
def update_avatar():
    if "user_file" not in request.files:
        flash("No file selected.")
        return redirect(url_for('users.edit_avatar'))
    file = request.files["user_file"]
    if file.filename == "":
        flash("No file selected.")
        return redirect(url_for('users.edit_avatar'))
    if not allowed_file(file):
        flash("Invalid file type.")
        return redirect(url_for('users.edit_avatar'))
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

        flash("Successfully updated.")
        return redirect(url_for('users.edit_avatar'))

    else:
        return redirect("/")

@users_blueprint.route('/u/<username>', methods=["GET","POST"])
def show(username):
    user = User.get_or_none(User.username == username)
    if not user:
        return render_template('error.html',
            error_header='User Not Found',
            error_text="Who you're looking for does not exist! :("
        )
    u_followers = user.followers()
    u_followings = user.following()

    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('users/show.html', user=user, u_followers=u_followers, u_followings=u_followings, following=following)

@users_blueprint.route('/u/all', methods=["GET","POST"])
def index():
    users = User.select().order_by(User.id).prefetch(Post, Like)
    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('users/index.html', users=users, following=following)

@users_blueprint.route('/u/search')
def search():
    term = request.args.get('q').lower()
    users = User.select().where(User.username.contains(term))
    following = []
    if current_user.is_authenticated:
        following = current_user.following()
    return render_template('users/index.html', users=users, following=following, term=term)

@users_blueprint.route('/u/<username>/following', methods=["GET"])
def show_following(username):
    user = User.get_or_none(User.username == username)

    if user:
        u_followers = user.followers()
        u_followings = user.following()
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('users/show_following.html', user=user, u_followers=u_followers, u_followings=u_followings, following=following)
    
    return render_template('error.html',
        error_header='User Not Found',
        error_text="Who you're looking for does not exist! :("
    )

@users_blueprint.route('/u/<username>/followers', methods=["GET"])
def show_followers(username):
    user = User.get_or_none(User.username == username)

    if user:
        u_followers = user.followers()
        u_followings = user.following()
        following = []
        if current_user.is_authenticated:
            following = current_user.following()
        return render_template('users/show_followers.html', user=user, u_followers=u_followers, u_followings=u_followings, following=following)

    return render_template('error.html',
        error_header='User Not Found',
        error_text="Who you're looking for does not exist! :("
    )

@users_blueprint.route('/follow/<user_id>', methods=["POST"])
@login_required
def follow(user_id):
    user = User.get_or_none(User.id == user_id)

    if not user:
        return redirect(url_for('home'))

    relationship = Relationship.get_or_none(Relationship.from_user == current_user.id, Relationship.to_user == user.id)
    # Dupe validate to be refined

    if not relationship:
        
        if user.is_private:
            flash(f"A follow request has been sent to {user.username} and now awaiting approval.")
    
        current_user.follow(user_id)

    else:
        if relationship.approved == False:
            flash(f"You have already sent a follow request to {user.username} previously.")

    if 'next' in request.form:
        return redirect(request.form['next'])

    return redirect(url_for('home'))

@users_blueprint.route('/unfollow/<user_id>', methods=["POST"])
@login_required
def unfollow(user_id):
    current_user.unfollow(user_id)

    if 'next' in request.form:
        return redirect(request.form['next'])

    return redirect(url_for('home'))

@users_blueprint.route('/requests', methods=["GET"])
@login_required
def requests():
    return render_template('users/requests.html')

@users_blueprint.route('/approve/<target_user_id>', methods=["POST"])
@login_required
def approve(target_user_id):
    current_user.approve(target_user_id)
    if current_user.follow_requests:
        return redirect(url_for('users.requests'))
    return redirect(url_for('users.show', username=current_user.username))

@users_blueprint.route('/reject/<target_user_id>', methods=["POST"])
@login_required
def reject(target_user_id):
    current_user.reject(target_user_id)
    if current_user.follow_requests:
        return redirect(url_for('users.requests'))
    return redirect(url_for('users.show', username=current_user.username))

@users_blueprint.route('approve_all', methods=["POST"])
@login_required
def approve_all():
    current_user.approve_all()
    return redirect(url_for('users.show', username=current_user.username))

@users_blueprint.route('/destroy_relationship/<user_id>', methods=["POST"])
@login_required
def destroy_relationship(user_id):
    current_user.remove_follower(user_id)
    return redirect(url_for('users.show_followers', username=current_user.username))