from flask import render_template, request, redirect, url_for, session, flash
from main import app
from models import db, User

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        _user = User.query.filter_by(username = username).first()

        if _user:
            if _user.password == password:
                # Do session stuff
                session['username'] = username
                return redirect('')
            else:
                flash("Wrong username or password!")
                return render_template('login.html')
        else:
            flash("User doesn't exist!")
            return render_template('login.html')
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # It has a user logged in
    session.clear()
    return redirect('')
