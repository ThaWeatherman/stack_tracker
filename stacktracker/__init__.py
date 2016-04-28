"""
Initializes the Flask application
"""
import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy


path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(path, 'app.db')
app = Flask(__name__)
# TODO: move config stuff to config.py and load it
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + path
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # TODO: what is this?
app.config['HASHING_ROUNDS'] = 5
app.config['SALT_LENGTH'] = 10
app.config['SECRET_KEY'] = 'poochootrain'
app.config['SECURITY_PASSWORD_SALT'] = 'dootdoot'
app.config['MAILGUN_KEY'] = ''
app.config['MAILGUN_DOMAIN'] = ''
app.secret_key = 'poopoocachoo'
db = SQLAlchemy(app)

import stacktracker.views
