from flask import render_template, request, redirect, url_for, session, flash, g
from main import app
from models import db, User, Session, Post
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
    if session.get('is_authenticated', False):
        print 'autenticated: ' + str(session.get('is_authenticated'))
        _s = Session.query.filter_by(key = session.get('session_id')).first()
        g.current_user = _s.user

# Views

@app.route('/')
def index():
    _posts = Post.query.order_by('created_at DESC').all()
    return render_template('index.html', posts = _posts)

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        _user = User.query.filter_by(username = username).first()

        if _user and _user.password == password:
            hash_key = username + app.secret_key + str(int(mktime(datetime.now().timetuple())))
            session_id = sha1(hash_key.encode()).hexdigest()

            s = Session(session_id)
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

@app.route('/post', methods = ['GET', 'POST'])
@app.route('/post/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if title and body:
            _user = g.current_user
            _post = Post(title, body)
            _user.posts.append(_post)

            db.session.add(_user)
            db.session.add(_post)
            db.session.commit()

            return redirect(url_for('index'))
    else:
        return render_template('new_post.html')

@app.route('/post/<int:id>')
def view_post(id):
    _post = Post.query.get(id)
    if _post:
        return render_template('post.html', post = _post)

@app.route('/post/<int:id>/edit', methods = ['GET', 'POST'])
@login_required
def edit_post(id):
    _post = Post.query.get(id)
    if request.method == 'POST':
        new_title = request.form['title']
        new_body = request.form['body']

        if new_title and new_body:
            _post.title = new_title
            _post.body = new_body
            db.session.commit()

        return redirect(url_for('view_post', id = id))
    else:
        print 'Is ownwe? ' + str(g.current_user == _post.user)
        if g.current_user == _post.user:
            return render_template('new_post.html', post = _post)
        else:
            return redirect(url_for('view_post', id = id))

@app.route('/post/<int:id>/delete')
@login_required
def delete_post(id):
    _post = Post.query.get(id)
    if g.current_user == _post.user:
        db.session.delete(_post)
        db.session.commit()

    return redirect(url_for('index'))
