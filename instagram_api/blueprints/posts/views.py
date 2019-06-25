from flask import Blueprint, jsonify, request

from models.post import Post, Like
from models.user import User

from flask_jwt_extended import jwt_required, get_jwt_identity

posts_api_blueprint = Blueprint('posts_api',
                             __name__,
                             template_folder='templates')

@posts_api_blueprint.route('/', methods=['GET'])
def show():
    if 'userId' not in request.args:
        posts = Post.select().order_by(Post.created_at)
        image_urls = [post.image_url for post in posts]
        return jsonify(image_urls)

    user_id = request.args.get('userId')
    posts = Post.select().where(Post.user_id == user_id).order_by(Post.created_at).prefetch(Like)
    image_urls = [post.image_url for post in posts]
    return jsonify(image_urls)

    # output = [{
    #     "created_at": post.created_at,
    #     "image_url": post.image_url,
    #     "caption": post.caption,
    #     "user": int(post.user_id),
    #     "like_count": len(post.likes)
    # } for post in posts]

    # return jsonify(output)

@posts_api_blueprint.route('/me', methods=['GET'])
@jwt_required
def my_posts():
    user = User.get_or_none(User.id == get_jwt_identity())
    if not user:
        return "Fix later"
    # breakpoint()
    posts = Post.select().where(Post.user_id == user.id).order_by(Post.created_at).prefetch(Like)
    image_urls = [post.image_url for post in posts]
    return jsonify(image_urls)