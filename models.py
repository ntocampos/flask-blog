from flask_sqlalchemy import SQLAlchemy
from main import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40)) # SHA1 encryption
    sessions = db.relationship('Session', backref='user', lazy='dynamic')

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password

    def __repr__(self):
        return '<User {id}: {username}>'.format(id = self.id, username = self.username)

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    key = db.Column(db.String(40))

    def __init__(self, user_id, key):
        self.key = key
