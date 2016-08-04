from flask import render_template, request, redirect, url_for, session, flash, g
from main import app
from models import db, User, Session, Post
from hashlib import sha1
from datetime import datetime
from time import mktime
from functools import wraps
import re
import simplejson as json

### Wrappers ###

# This decorator will prevent that users don't access certain pages that need
# authentication
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('session_id'):
            # If the session is active, verify if the session key exists in the db
            # to prevent fake session keys
            user_id = session.get('user_id')
            session_id = session.get('session_id')
            _session = Session.query.filter_by(user_id = user_id, key = session_id)

            if _session:
                return f(*args, **kwargs)

        return redirect(url_for('login'))

    return decorated_function

# Puts the session_id corresponding user object in the g variable, to be accessible
# through the entire request
@app.before_request
def before():
    if session.get('is_authenticated', False):
        print 'autenticated: ' + str(session.get('is_authenticated'))
        _s = Session.query.filter_by(key = session.get('session_id')).first()
        g.current_user = _s.user


### Auxiliar functions ###

def authenticate(username, password, remember = False):
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
        session.permanent = remember

        return True
    else:
        return False


### Views ###
# Above each view, a comment about what the page does

# Lists all the posts
@app.route('/')
def index():
    _posts = Post.query.order_by('created_at DESC').all()
    return render_template('index.html', posts = _posts)


# GET: displays the login form; POST: authenticate
@app.route('/login', methods = ['GET', 'POST'])
def login():
    if session.get('is_authenticated'):
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if request.form.get('remember_me'):
            remember_me = True
        else:
            remember_me = False

        if authenticate(username, password, remember_me):
            return redirect('')
        else:
            flash("Wrong username or password.")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/check_user', methods = ['POST'])
def check_username():
    username = request.form.get('username')
    if username:
        _user = User.query.filter_by(username=username).first()
        print(_user)
        if not _user:
            return json.dumps({ 'user_exists': False })
        else:
            return json.dumps({ 'user_exists': True })

    return json.dumps({})

@app.route('/check_email', methods = ['POST'])
def check_email():
    email = request.form.get('email')

    prog = re.compile(r'([a-z A-Z 0-9 . _ + -])+\@([a-z A-Z 0-9 - .])+\.([a-z])+')

    if email:
        _user = User.query.filter_by(email=email).first()
        print(_user)

        if _user or not prog.match(email):
            return json.dumps({ 'email_exists': True })
        else:
            return json.dumps({ 'email_exists': False })

    return json.dumps({})


# Clear the session values
@app.route('/logout')
@login_required
def logout():
    session.clear()
    return redirect(url_for('index'))

# GET: displays the new post form; POST: creates a new post
@app.route('/post', methods = ['GET', 'POST'])
@app.route('/post/new', methods = ['GET', 'POST'])
@login_required
def new_post():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        title = title if len(title) <= 50 else title[:50]
        body = body if len(body) <= 1000 else body[:1000]

        print('#######' + title + '#######')
        print('#######' + title[:50] + '#######')

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

# View a specific post
@app.route('/post/<int:id>')
def view_post(id):
    _post = Post.query.get(id)
    if _post:
        return render_template('post.html', post = _post)
    else:
        return '404'

# GET: display the form pre filled to edit a post; POST: edit the post
@app.route('/post/<int:id>/edit', methods = ['GET', 'POST'])
@login_required
def edit_post(id):
    _post = Post.query.get(id)
    if g.current_user == _post.user:
        if request.method == 'POST':
            title = request.form['title']
            body = request.form['body']

            title = title if len(title) <= 50 else title[:50]
            body = body if len(body) <= 1000 else body[:1000]

            print('#######' + title + '#######')
            print('#######' + title[:50] + '#######')

            if title and body:
                _post.title = title
                _post.body = body
                db.session.commit()

            return redirect(url_for('view_post', id = id))
        else:
            return render_template('new_post.html', post = _post)
    else:
        return redirect(url_for('view_post', id = id))

# Delete a specific post if the requestor is the owner
@app.route('/post/<int:id>/delete')
@login_required
def delete_post(id):
    _post = Post.query.get(id)
    if g.current_user == _post.user:
        db.session.delete(_post)
        db.session.commit()

    return redirect(url_for('index'))

# GET: displays the register form; POST: creates a new user in the db
@app.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        valid = True

        prog = re.compile(r'([a-z A-Z 0-9 . _ + -])+\@([a-z A-Z 0-9 - .])+\.([a-z])+')
        if not prog.match(email):
            valid = False
            print 'email error'

        if len(username) < 4:
            valid = False
            print 'username error'

        if len(password) < 4:
            valid = False
            print 'password error'

        if valid:
            hashed_pass = sha1(password).hexdigest()

            _user = User(email, username, hashed_pass)
            db.session.add(_user)
            db.session.commit()
            authenticate(username, password, True)

            return redirect(url_for('index'))
        else:
            return redirect(url_for('register'))
    else:
        return render_template('register.html')

@app.route('/user/<int:userid>')
def userListing(userid):
    _user = User.query.filter_by(id = userid).first()
    if not _user:
        return 404

    print(_user.posts)

    return render_template('user.html', user=_user)
