from flask import render_template, request, redirect, url_for, session
from main import app

@app.route('/')
def index():
    return "<h1>Hello, views!</h1>"
