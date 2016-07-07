from flask_sqlalchemy import SQLAlchemy
from main import app

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column('id', db.Integer, primary_key=True)
    email = db.Column('email', db.String(100))
    username = db.Column('username', db.String(20))
    password = db.Column('password', db.String(40)) # SHA1 encryption

    def __init__(self, email, username, password):
        self.email = email
        self.username = username
        self.password = password
