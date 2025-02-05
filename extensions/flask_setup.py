from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

db = SQLAlchemy()
login_manager = LoginManager()
admin = Admin(template_mode='bootstrap3')

def init_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)
    admin.init_app(app)