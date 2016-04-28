"""
Initializes the Flask application
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')
app.config.from_object('stacktracker.config')
db = SQLAlchemy(app)

import stacktracker.views
