from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login = LoginManager()
login.login_view = 'auth.login'

from flask_moment import Moment
moment = Moment()
num_collector = []  # For run-time field assortment

# ================================================================
#   Name:           Create App
#   Description:    Congifures and runs program
#   Last Changed:   10/26/21
#   Changed By:     Reagan Kelley
#   Change Details: Basic Implementation of create app
# ================================================================
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    app.static_folder = config_class.STATIC_FOLDER 
    app.template_folder = config_class.TEMPLATE_FOLDER
    num_collector.clear()

    db.init_app(app)
    login.init_app(app)
    moment.init_app(app)
    from app.Controller.errors import bp_errors as errors
    app.register_blueprint(errors)
    from app.Controller.auth_routes import bp_auth as auth
    app.register_blueprint(auth)
    from app.Controller.routes import bp_routes as routes
    app.register_blueprint(routes)

    if not app.debug and not app.testing:
        pass

    return app