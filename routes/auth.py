from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from ..models import user
from ..services import auth_service

auth = Blueprint('auth', __name__)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username_or_email = request.form['username']
        password = request.form['password']
        user_instance = auth_service.authenticate_user(username_or_email, password)
        if user_instance:
            login_user(user_instance)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.index'))
        flash('Invalid credentials. Please try again.', 'error')
    return render_template('login.html')

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('main.index'))

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        result = auth_service.register_user(
            request.form['username'], 
            request.form['email'], 
            request.form['password'], 
            request.form.get('confirm_password')
        )
        if result['success']:
            flash(result['message'], 'success')
            return redirect(url_for('auth.login'))
        flash(result['message'], 'error')
    return render_template('register.html')