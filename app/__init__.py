from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from app.config import Config

db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(name='Admin Panel', template_mode='bootstrap3')

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)
    
    # Configure login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = "Please log in to access this page."
    
    # Register blueprints
    from app.routes.auth import auth
    from app.routes.main import main
    
    app.register_blueprint(auth)
    app.register_blueprint(main)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app