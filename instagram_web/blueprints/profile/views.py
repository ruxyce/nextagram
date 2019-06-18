from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from werkzeug.utils import secure_filename

from models.post import AvatarKey
from models.user import User

from helpers import Config, s3

from flask_login import login_required, current_user

import random
import string

profile_blueprint = Blueprint('profile',
                            __name__,
                            template_folder='templates')

def allowed_file(file):
    return 'image' in file.content_type

@profile_blueprint.route('/', methods=['GET'])
def profile():
    return render_template('profile.html')
 
@profile_blueprint.route('/avatar')
@login_required
def update_avatar():
    return render_template('update_avatar.html')

@profile_blueprint.route("/upload_avatar", methods=["POST"])
@login_required
def upload_avatar():
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

        return redirect(url_for('users.userpage', username=current_user.username))

    else:
        return redirect("/")