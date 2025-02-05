from ..models import issue, category, vote

def get_issues(sort_by, category_filter):
    query = issue.Issue.query
    if category_filter:
        query = query.filter_by(category_id=category_filter)
    if sort_by == 'votes':
        query = query.order_by(issue.Issue.votes.desc())
    else:  # Default sort by date
        query = query.order_by(issue.Issue.created_at.desc())
    return query.all()

def create_issue(title, description, category_id):
    new_issue = issue.Issue(title=title, description=description, category_id=category_id)
    issue.db.session.add(new_issue)
    issue.db.session.commit()

def vote(user_id, issue_id):
    the_issue = issue.Issue.query.get_or_404(issue_id)
    existing_vote = vote.UserVote.query.filter_by(user_id=user_id, issue_id=issue_id).first()
    if not existing_vote:
        the_issue.votes += 1
        new_vote = vote.UserVote(user_id=user_id, issue_id=issue_id)
        vote.db.session.add(new_vote)
        vote.db.session.commit()
        return {'message': 'Your vote has been recorded!', 'category': 'success'}
    return {'message': 'You have already voted on this issue.', 'category': 'warning'}