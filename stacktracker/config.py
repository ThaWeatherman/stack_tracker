import os


path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(path, 'app.db')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path
SQLALCHEMY_TRACK_MODIFICATIONS = False  # TODO: what is this?
HASHING_ROUNDS = 5
SALT_LENGTH = 10
SECRET_KEY = 'poochootrain'
SECURITY_PASSWORD_SALT = 'dootdoot'
MAILGUN_KEY = ''
MAILGUN_DOMAIN = ''
