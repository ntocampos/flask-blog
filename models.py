from flask_sqlalchemy import SQLAlchemy
from main import app
from datetime import datetime

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40)) # SHA1 encryption

    sessions = db.relationship('Session', backref='user', lazy='dynamic')
    posts = db.relationship('Post', backref='user', lazy='dynamic')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User [{id}]: {username}>'.format(id = self.id, username = self.username)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    key = db.Column(db.String(40))

    def __init__(self, key):
        self.key = key

class Post(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    title = db.Column(db.String(50))
    body = db.Column(db.String(1000))
    created_at = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body):
        self.title = title
        self.body = body
        self.created_at = datetime.now()

    def __repr__(self):
        truncated = (self.title[:10] + '...') if len(self.title) > 10 else self.title
        return 'Post [{id}]: {title}'.format(id = self.id, title = truncated)

def rebuild_database():
    db.drop_all()
    print 'Database droped...'
    db.create_all()
    print 'Database created...'
    u = User('user@example.com', 'user', 'password')
    print 'User created...'

    db.session.add(u)
    db.session.commit()
