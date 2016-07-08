from flask import render_template, request, redirect, url_for, session, flash
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
            _session = Session.query.filter_by(user_id = user_id, session_id = session_id)

            if _session:
                return f(*args, **kwargs)

        return redirect(url_for('login'))

    return decorated_function



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

            session['user_id'] = _user.id
            session['username'] = username
            session['session_id'] = session_id

            return redirect('')
        else:
            flash("Wrong username or password.")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    if 'session_id' in session:
        # User is logged in
        session.clear()
        return redirect('')
    else:
        return redirect(url_for('login'))
