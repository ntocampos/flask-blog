from flask import render_template, request, redirect, url_for, session, flash, g
from main import app
from models import db, User, Session
from hashlib import sha1
from datetime import datetime
from time import mktime
from functools import wraps

# Wrappers

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('session_id'):
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            _session = Session.query.filter_by(user_id = user_id, key = session_id)

            if _session:
                return f(*args, **kwargs)

        return redirect(url_for('login'))

    return decorated_function

@app.before_request
def before():
    if session.get('is_authenticated'):
        _s = Session.query.filter_by(key = session.get('session_id')).first()
        g.current_user = _s.user

# Views

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        _user = User.query.filter_by(username = username).first()

        if _user and _user.password == password:
            hash_key = username + app.secret_key + str(int(mktime(datetime.now().timetuple())))
            session_id = sha1(hash_key.encode()).hexdigest()

            s = Session(_user.id, session_id)
            _user.sessions.append(s)
            db.session.add(s)
            db.session.commit()

            session['session_id'] = session_id
            session['is_authenticated'] = True

            return redirect('')
        else:
            flash("Wrong username or password.")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect('')

@app.route('/post/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'GET':
        return render_template('new_post.html')
