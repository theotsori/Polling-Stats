from flask import Blueprint
from .config import *
from .extensions.flask_setup import db, login_manager, admin, init_extensions

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

    init_extensions(app)

    from .routes import main, auth
    app.register_blueprint(main)
    app.register_blueprint(auth)

    from .models import user, category, issue, vote
    from .models.user import User
    from .services import auth_service

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    class AdminModelView(ModelView):
        def is_accessible(self):
            return auth_service.is_admin(current_user)

    admin.add_view(AdminModelView(User, db.session))
    admin.add_view(AdminModelView(issue.Issue, db.session))
    admin.add_view(AdminModelView(category.Category, db.session))

    return app