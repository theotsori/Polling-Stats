from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///votes.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Issue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    votes = db.Column(db.Integer, default=0)

@app.route('/')
def index():
    issues = Issue.query.all()
    return render_template('index.html', issues=issues)

@app.route('/add', methods=['GET', 'POST'])
def add_issue():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        new_issue = Issue(title=title, description=description)
        db.session.add(new_issue)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_issue.html')

@app.route('/vote/<int:issue_id>', methods=['POST'])
def vote(issue_id):
    issue = Issue.query.get(issue_id)
    issue.votes += 1
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/results')
def results():
    issues = Issue.query.order_by(Issue.votes.desc()).all()
    return render_template('results.html', issues=issues)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        app.run(debug=True)
