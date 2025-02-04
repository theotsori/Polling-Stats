import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import (
    LoginManager, UserMixin, login_user, login_required,
    logout_user, current_user
)
from datetime import datetime
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import check_password_hash, generate_password_hash

# -------------------------
# Application Configuration
# -------------------------
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
with open('my_secret_key.txt', 'r') as f:
    app.secret_key = f.read().strip()

db = SQLAlchemy(app)

# -------------------------
# Flask-Login Setup
# -------------------------
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = "Please log in to access this page."

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# -------------------------
# Models
# -------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    votes = db.Column(db.Integer, default=0)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category', backref='issues')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class UserVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)

# -------------------------
# Flask-Admin Setup
# -------------------------
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

admin = Admin(app, name='Admin Panel', template_mode='bootstrap3')
admin.add_view(AdminModelView(User, db.session))
admin.add_view(AdminModelView(Issue, db.session))
admin.add_view(AdminModelView(Category, db.session))

# -------------------------
# Authentication Routes
# -------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        # Allow login with username or email
        user = User.query.filter((User.username == username_or_email) | (User.email == username_or_email)).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form values
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form.get('confirm_password')

        # Basic validations
        if password != confirm_password:
            flash('Passwords do not match.', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Username or email already exists.', 'error')
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

# -------------------------
# Main Application Routes
# -------------------------
@app.route('/')
def index():
    sort_by = request.args.get('sort', 'date')
    category_filter = request.args.get('category')

    query = Issue.query
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    if sort_by == 'votes':
        query = query.order_by(Issue.votes.desc())
    else:  # Default sort by date
        query = query.order_by(Issue.created_at.desc())
    
    issues = query.all()
    categories = Category.query.all()
    return render_template(
        'index.html',
        issues=issues,
        categories=categories,
        current_sort=sort_by,
        current_category=category_filter
    )

@app.route('/add', methods=['GET', 'POST'])
def add_issue():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        # Optionally, add a category if provided
        category_id = request.form.get('category_id')
        new_issue = Issue(title=title, description=description, category_id=category_id)
        db.session.add(new_issue)
        db.session.commit()
        flash('New issue added!', 'success')
        return redirect(url_for('index'))
    categories = Category.query.all()
    return render_template('add_issue.html', categories=categories)

@app.route('/vote/<int:issue_id>', methods=['POST'])
@login_required
def vote(issue_id):
    issue = Issue.query.get_or_404(issue_id)
    existing_vote = UserVote.query.filter_by(user_id=current_user.id, issue_id=issue_id).first()
    if not existing_vote:
        issue.votes += 1
        new_vote = UserVote(user_id=current_user.id, issue_id=issue_id)
        db.session.add(new_vote)
        db.session.commit()
        flash('Your vote has been recorded!', 'success')
    else:
        flash('You have already voted on this issue.', 'warning')
    return redirect(url_for('index'))

@app.route('/results')
def results():
    issues = Issue.query.order_by(Issue.votes.desc()).all()
    return render_template('results.html', issues=issues)

# -------------------------
# Run the Application
# -------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create tables if they don't exist
    app.run(debug=True)
