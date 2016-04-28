"""
Initializes the Flask application
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config.from_object('stacktracker.config')
db = SQLAlchemy(app)

import stacktracker.views
