from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from ..models import issue, category, vote
from ..services import vote_service

main = Blueprint('main', __name__)

@main.route('/')
def index():
    sort_by = request.args.get('sort', 'date')
    category_filter = request.args.get('category')
    issues = vote_service.get_issues(sort_by, category_filter)
    categories = category.Category.query.all()
    return render_template('index.html', issues=issues, categories=categories, 
                           current_sort=sort_by, current_category=category_filter)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_issue():
    if request.method == 'POST':
        title, description, category_id = request.form['title'], request.form['description'], request.form.get('category_id')
        vote_service.create_issue(title, description, category_id)
        flash('New issue added!', 'success')
        return redirect(url_for('main.index'))
    return render_template('add_issue.html', categories=category.Category.query.all())

@main.route('/vote/<int:issue_id>', methods=['POST'])
@login_required
def vote(issue_id):
    result = vote_service.vote(current_user.id, issue_id)
    flash(result['message'], result['category'])
    return redirect(url_for('main.index'))

@main.route('/results')
def results():
    issues = issue.Issue.query.order_by(issue.Issue.votes.desc()).all()
    return render_template('results.html', issues=issues)