from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from app.models import User, Issue, Category
from app import admin, db

class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

# Add admin views
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Issue, db.session))
admin.add_view(AdminModelView(Category, db.session))