from datetime import datetime
from . import db

class UserVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    issue_id = db.Column(db.Integer, db.ForeignKey('issue.id'))
    voted_at = db.Column(db.DateTime, default=datetime.utcnow)