from app import app
from flask import render_template, session, escape, redirect, url_for

import os
from instagram_web.helpers.google_oauth import oauth
import config

from flask_login import current_user

from instagram_web.blueprints.users.views import users_blueprint
from instagram_web.blueprints.sessions.views import sessions_blueprint
from instagram_web.blueprints.posts.views import posts_blueprint
from instagram_web.blueprints.donate.views import donate_blueprint

from flask_assets import Environment, Bundle
from .util.assets import bundles

assets = Environment(app)
assets.register(bundles)

oauth.init_app(app)

app.register_blueprint(users_blueprint, url_prefix="/")
app.register_blueprint(sessions_blueprint, url_prefix="/")
app.register_blueprint(posts_blueprint, url_prefix="/p")
app.register_blueprint(donate_blueprint, url_prefix="/donate")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route("/")
def home():
    if current_user.is_authenticated:
        return redirect(url_for('posts.index'))
    return redirect(url_for('users.index'))