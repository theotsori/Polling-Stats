from werkzeug.security import generate_password_hash, check_password_hash
from ..models import user

def authenticate_user(username_or_email, password):
    user_instance = user.User.query.filter((user.User.username == username_or_email) | (user.User.email == username_or_email)).first()
    if user_instance and check_password_hash(user_instance.password, password):
        return user_instance
    return None

def register_user(username, email, password, confirm_password):
    if password != confirm_password:
        return {'success': False, 'message': 'Passwords do not match.'}
    
    if user.User.query.filter((user.User.username == username) | (user.User.email == email)).first():
        return {'success': False, 'message': 'Username or email already exists.'}

    new_user = user.User(username=username, email=email, password=generate_password_hash(password))
    user.db.session.add(new_user)
    user.db.session.commit()
    return {'success': True, 'message': 'Registration successful! Please log in.'}

def is_admin(user):
    return user.is_admin if user else False