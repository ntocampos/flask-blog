from flask import Flask
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.secret_key = 'f97a5a8134e5df4ad0707be5f4bcb7e308e77debb097d9bd'
# os.urandom(24).encode('hex')

from views import *

if __name__ == '__main__':
    app.run(debug = True)
