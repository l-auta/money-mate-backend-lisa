from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_session import Session  # Import Flask-Session
from config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
session = Session()  # Initialize Flask-Session

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app, supports_credentials=True)  # Allow credentials (cookies)

    # Configure Flask-Session
    app.config['SESSION_TYPE'] = 'filesystem'  # Store sessions on the filesystem
    app.config['SECRET_KEY'] = '8l@ck890101'  # Required for session security
    session.init_app(app)

    db.init_app(app)
    bcrypt.init_app(app)

    with app.app_context():
        from . import routes
        app.register_blueprint(routes.main_routes)
        db.create_all()  # Create database tables

    return app