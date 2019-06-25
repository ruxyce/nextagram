from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from werkzeug.utils import secure_filename

from flask_login import login_required, current_user

from models.post import Post, ImageKey, Like
from models.user import User

import random
import string
import math

from helpers import Config, s3

posts_blueprint = Blueprint('posts',
                            __name__,
                            template_folder='templates')

def allowed_file(file):
    return 'image' in file.content_type

# @posts_blueprint.route('/all', methods=['GET'])
# @login_required
# def index():
#     posts = Post.select().order_by(Post.created_at.desc()).limit(10).prefetch(Like)
#     return render_template('posts/index.html', posts=posts)

@posts_blueprint.route('/feed', methods=['GET'])
@login_required
def index():
    page = request.args.get('page')
    posts = (Post
            .select()
            .where((Post.user.in_(current_user.following())) | (Post.user_id == current_user.id))
            .order_by(Post.created_at.desc()))

    # add handler for 0 post
    total_posts = len(posts)
    posts_per_page = 2
    pages = math.ceil(total_posts/posts_per_page)

    if not page or not page.isnumeric():
        page = 1

    page = int(page)

    if page > pages:
        page = pages

    posts = posts.paginate(page, posts_per_page).prefetch(Like)
    return render_template('posts/index.html', posts=posts, pages=pages, page=page)

@posts_blueprint.route('/new', methods=['GET','POST'])
@login_required
def new():
    return render_template('posts/new.html')

@posts_blueprint.route('/<post_id>', methods=['GET'])
def show(post_id):
    post = Post.get_or_none(Post.image == post_id)
    if post:
        user = User.get(User.id == post.user_id)
        return render_template('posts/show.html', post=post, user=user)
    return "Post not found"

@posts_blueprint.route('/like/<post>', methods=['POST'])
@login_required
def like(post):
    find = Like.get_or_none(Like.post == post, Like.user == current_user.id)
    if not find:
        Like.create(post = post, user = current_user.id)

    if 'next' in request.form:
        return redirect(request.form['next'])

    return redirect(url_for('posts.index'))

@posts_blueprint.route('/unlike/<post>', methods=['POST'])
@login_required
def unlike(post):
    find = Like.get_or_none(Like.post == post, Like.user == current_user.id)
    if find:
        find.delete_instance()

    if 'next' in request.form:
        return redirect(request.form['next'])

    return redirect(url_for('posts.index'))

@posts_blueprint.route("/create", methods=["POST"])
@login_required
def create():
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
            retrieve = ImageKey.get_or_none(ImageKey.filename == filename)
            if retrieve:
                continue
            else:
                ImageKey.create(filename = filename)
                dupe = False
        prepend = 'images/'

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
        
        caption = request.form['caption']

        Post.create(user=current_user.id, image=filename, caption=caption)

        return redirect(url_for('home'))

    else:
        return redirect("/")