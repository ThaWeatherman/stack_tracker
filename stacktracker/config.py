import os


path = os.path.abspath(os.path.dirname(__file__))
path = os.path.join(path, 'app.db')

DEBUG = None  # for runserver
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + path
SQLALCHEMY_TRACK_MODIFICATIONS = False  # TODO: what is this?
HASHING_ROUNDS = 5
SALT_LENGTH = 10
try:
    SECRET_KEY = os.environ['SECRET_KEY']
except KeyError:
    SECRET_KEY = 'poochoo'
try:
    SECURITY_PASSWORD_SALT = os.environ['SECURITY_SALT']
except KeyError:
    SECURITY_PASSWORD_SALT = 'dootdoot'
try:
    MAILGUN_KEY = os.environ['MAILGUN_API_KEY']
except KeyError:
    MAILGUN_KEY = ''
MAILGUN_DOMAIN = 'seanmckaybeck.com'
