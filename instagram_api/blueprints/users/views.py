from flask import Blueprint, jsonify, request

from werkzeug.security import generate_password_hash

from models.user import User, Relationship

import re

from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

users_api_blueprint = Blueprint('users_api',
                             __name__,
                             template_folder='templates')

@users_api_blueprint.route('/', methods=['GET'])
def index():
    return jsonify(
            [{ "id": user.id, 
                "username": user.username,
                "profileImage": user.avatar_url,
                "isPrivate": user.is_private }
            for user in User.select().order_by(User.id)] 
    )

@users_api_blueprint.route('/<user_id>', methods=['GET'])
def show(user_id):
    user = User.get_or_none(User.id == user_id)

    if user:
        return jsonify(
            { "id": user.id,
                "username": user.username,
                "avatar": user.avatar_url,
                "followers": [follower.id for follower in user.followers],
                "following": [following.id for following in user.following] }
        )

    return jsonify({
        "message": "User does not exist",
        "status": "failed"
    })

@users_api_blueprint.route('/', methods=['POST'])
def create():
    if not request.is_json:
        return jsonify({"message": "Error - Missing JSON in request"})

    if not 'username' in request.json or not 'password' in request.json or not 'email' in request.json:
        return jsonify({"message": "Error - Missing parameters"})

    username = request.json['username']
    email = request.json['email']
    password = request.json['password']

    if User.get_or_none(User.username == username):
        return jsonify({"message": "Error - Username already taken"})
    
    if User.get_or_none(User.email == email):
        return jsonify({"message": "Error - Email already registered"})

    # Validate
    pattern = "^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
    if not re.match(pattern, email):
        return jsonify({"message": "Error - Invalid email address"})

    characters = "abcdefghijklmnopqrstuvwxyz0123456789_."
    if not all(char in characters for char in username) or len(username) < 5 or len(username) > 20:
        return jsonify({"message": "Error - Username must be between 5 to 20 characters long"})

    pw_pattern = "^[A-Za-z0-9._@-]{8,32}$"
    if not re.match(pw_pattern, password):
        return jsonify({"message": "Error - Password criteria not met"})

    password = generate_password_hash(password)
    user = User.create(username=username, email=email, password=password)

    access_token = create_access_token(identity=user.id)

    output = {
        "auth_token": access_token,
        "message": "New user successfully created.",
        "status": "success",
        "user": {
            "id": user.id,
            "profileImage": user.avatar_url,
            "username": user.username,
            "isPrivate": user.is_private
        }
    }

    return jsonify(output)

@users_api_blueprint.route('/following/me', methods=['GET'])
@jwt_required
def my_following():
    user = User.get_or_none(User.id == get_jwt_identity())
    if not user:
        return jsonify({"status": "failed"}), 401
    approved = [guy.id for guy in user.following]
    pending = [guy.id for guy in user.following_requests]
    return jsonify(
        { "my_following": { "approved": approved, "pending": pending } }
    )

@users_api_blueprint.route('/followers/me', methods=['GET'])
@jwt_required
def my_followers():
    user = User.get_or_none(User.id == get_jwt_identity())
    if not user:
        return jsonify({"status": "failed"}), 401
    my_followers = [follower.id for follower in user.followers]
    return jsonify(my_followers)

@users_api_blueprint.route('/follow/<user_id>', methods=['POST'])
@jwt_required
def follow(user_id):
    user = User.get_or_none(User.id == get_jwt_identity())
    user.follow(user_id)

    approved = [guy.id for guy in user.following]
    pending = [guy.id for guy in user.following_requests]
    return jsonify(
        { "my_following": { "approved": approved, "pending": pending } }
    )

@users_api_blueprint.route('/unfollow/<user_id>', methods=['POST'])
@jwt_required
def unfollow(user_id):
    user = User.get_or_none(User.id == get_jwt_identity())
    user.unfollow(user_id)

    approved = [guy.id for guy in user.following]
    pending = [guy.id for guy in user.following_requests]
    return jsonify(
        { "my_following": { "approved": approved, "pending": pending } }
    )  