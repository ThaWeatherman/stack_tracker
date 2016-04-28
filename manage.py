import os

from flask.ext.script import Manager, Command
from flask.ext.hashing import Hashing

from stacktracker import app


try:
    input = raw_input
except NameError:
    pass
manager = Manager(app)
hashing = Hashing(app)


@manager.command
def initdb():
    """Initializes an empty application database"""
    from stacktracker import db
    db.create_all()


@manager.command
def dumpconfig():
    """Dumps the application's current config"""
    from pprint import pprint
    pprint(app.config)


@manager.command
def admin(email):
    """Make the specified user an administrator. manage.py admin <email>"""
    from stacktracker import db
    from stacktracker.models import User
    user = User.query.get(email)
    if user:
        user.is_admin = True
        db.session.add(user)
        db.session.commit()
        print('User {} is now an admin'.format(email))
    else:
        print('That is not a valid user')


@manager.command
def unadmin(email):
    """Remove admin rights from the specified user. manage.py unadmin <email>"""
    from stacktracker import db
    from stacktracker.models import User
    user = User.query.get(email)
    if  user:
        user.is_admin = False
        db.session.add(user)
        db.session.commit()
        print('User {} is no longer an admin'.format(email))
    else:
        print('That is not a valid user')


@manager.command
def adduser(email, password):
    """Add a user to the database. manage.py adduser <email> <password>"""
    from stacktracker import db
    from stacktracker.models import User
    user = User.query.get(email)
    if user:
        print('User already exists')
    else:
        salt = os.urandom(app.config['SALT_LENGTH'])
        pswd = hashing.hash_value(password, salt=salt)
        user = User(email, pswd, salt)
        db.session.add(user)
        db.session.commit()
        print('User added')


@manager.command
def removeuser(email):
    from stacktracker import db
    from stacktracker.models import User
    user = User.query.get(email)
    if user:
        db.session.delete(user)
        db.session.commit()
        print('Deleted user')
    else:
        print('No such user')


if __name__ == '__main__':
    manager.run()

