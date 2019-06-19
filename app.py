import os
import config
from flask import Flask, render_template, redirect, url_for, flash
import flask_login as fl

from flask_login import current_user

from flask_wtf.csrf import CSRFProtect

from models.base_model import db
from models.user import User

web_dir = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), 'instagram_web')

app = Flask('NEXTAGRAM', root_path=web_dir)

csrf = CSRFProtect(app)

login_manager = fl.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(id):
    return User.get_or_none(User.id == id)

# only to overwrite, can do without
@login_manager.unauthorized_handler
def unauthorized():
    flash("You must be logged in to do that.")
    return redirect(url_for('sessions.new'))
    # return render_template('401.html')

if os.getenv('FLASK_ENV') == 'production':
    app.config.from_object("config.ProductionConfig")
else:
    app.config.from_object("config.DevelopmentConfig")

@app.before_request
def before_request():
    db.connect()


@app.teardown_request
def _db_close(exc):
    if not db.is_closed():
        print(db)
        print(db.close())
    return exc

@app.context_processor
def count_requests():
    if current_user.is_authenticated:
        hoho = current_user.id
    return dict(hoho=hoho)