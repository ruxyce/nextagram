from app import app, csrf
from flask_cors import CORS

cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

## Import API Routes ##
from instagram_api.blueprints.users.views import users_api_blueprint
from instagram_api.blueprints.sessions.views import sessions_api_blueprint
from instagram_api.blueprints.posts.views import posts_api_blueprint

## Register API Routes ##
app.register_blueprint(users_api_blueprint, url_prefix='/api/v1/users')
app.register_blueprint(sessions_api_blueprint, url_prefix='/api/v1')
app.register_blueprint(posts_api_blueprint, url_prefix="/api/v1/posts")

csrf.exempt(sessions_api_blueprint)
csrf.exempt(users_api_blueprint)
csrf.exempt(posts_api_blueprint)

from models.user import User
from werkzeug.security import check_password_hash
