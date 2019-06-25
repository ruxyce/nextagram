from flask import Blueprint, jsonify, request, make_response

from werkzeug.security import check_password_hash

from models.user import User, Relationship

from instagram_api.helpers import jsonify_failed, jsonify_success

import jwt

from flask_jwt_extended import jwt_required, create_access_token, get_jwt_identity

sessions_api_blueprint = Blueprint('sessions_api',
                             __name__,
                             template_folder='templates')

@sessions_api_blueprint.route('/login', methods=['POST'])
def login():
    if not request.is_json:
        return jsonify({"message": "Error - Missing JSON in request"}), 400

    if not 'username' in request.json or not 'password' in request.json:
        return jsonify({"message": "Error - Missing login parameters"}), 400

    user = User.get_or_none(User.username == request.json['username'])

    if not user:
        return jsonify({"message": "Error - User does not exist"}), 401

    if not check_password_hash(user.password, request.json['password']):
        return jsonify({"message": "Error - Bad password"}), 401

    access_token = create_access_token(identity=user.id)

    output = {
        "auth_token": access_token,
        "message": "Successfully signed in.",
        "status": "success",
        "user": {
            "id": user.id,
            "profileImage": user.avatar_url,
            "username": user.username,
            "isPrivate": user.is_private
        }
    }

    return jsonify(output)

@sessions_api_blueprint.route('/protected', methods=['GET'])
@jwt_required
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@sessions_api_blueprint.route('/test', methods=['GET'])
def test():

    users = User.select()
    
    output = []

    for user in users:

        user_data = {
            "id" : user.id,
            "profileImage": user.avatar_url,
            "username": user.username
        }

        output.append(user_data)

    return jsonify(output)

@sessions_api_blueprint.route('/token', methods=['GET'])
@jwt_required
def validate_token():
    user = User.get_by_id(get_jwt_identity())

    output = {
        "message": "Signed in with previous token.",
        "status": "success",
        "user": {
            "id": user.id,
            "profileImage": user.avatar_url,
            "username": user.username,
            "isPrivate": user.is_private
        }
    }

    return jsonify(output)