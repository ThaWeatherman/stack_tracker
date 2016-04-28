"""
Contains all of the routing views
"""
from functools import wraps
import os
import time

from flask import render_template, abort, request, redirect, url_for, flash
from flask_restful import Api, Resource, reqparse
from flask_login import LoginManager, login_user, logout_user, current_user, login_required
from flask.ext.hashing import Hashing
from itsdangerous import URLSafeTimedSerializer

from .mailgun import mailgun_notify
from stacktracker import app, db
from stacktracker.models import Coin, Item, User
from stacktracker.forms import CoinForm, ItemForm, LoginForm, RegistrationForm


api = Api(app)
login_manager = LoginManager()
login_manager.init_app(app)
hashing = Hashing(app)


# ----------------
# helper functions
# ----------------
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        email = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
        return email
    except:
        return False


def check_confirmed(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.confirmed is False:
            flash('Please confirm your account!', 'warning')
            return redirect(url_for('unconfirmed'))
        return func(*args, **kwargs)
    return decorated_function


def check_admin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if current_user.is_admin is False:
            return abort(404)
        return func(*args, **kwargs)
    return decorated_function


def send_email(user, html):
    conf = {
            'api_key': app.config['MAILGUN_KEY'],
            'domain': app.config['MAILGUN_DOMAIN'],
            'from': 'Admin <register@{}>'.format(app.config['MAILGUN_DOMAIN']),
            'to': user.email,
            'subject': 'Please confirm your account',
            'html': html
            }
    while True:
        try:
            mailgun_notify(**conf)
            break
        except:
            # TODO: add logging
            time.sleep(1)
            continue


# -------------
# API functions
# -------------
class CoinResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('name', type=str, help='The name of the coin type')
    parser.add_argument('weight', type=float, help='The weight of the main precious metal in the coin/bar')
    parser.add_argument('actual_weight', type=float, help='The actual weight of the coin')
    parser.add_argument('metal', type=str, help='The main precious metal in the coin/bar')
    parser.add_argument('country', type=str, help='The origin country of the coin/bar')
    parser.add_argument('ngc_url', type=str, default = '', help='The URL to a comparable coin in the NGC registry')
    parser.add_argument('pcgs_url', type=str, default = '', help='The URL to a comparable coin in the PCGS registry')
    parser.add_argument('jm_url', type=str, default = '', help='The URL to the product on JMB\'s website')
    parser.add_argument('apmex_url', type=str, default = '', help='The URL to the product on Apmex\'s website')
    parser.add_argument('shinybars_url', type=str, default = '', help='The URL to the product on ShinyBars')
    parser.add_argument('provident_url', type=str, default = '', help='The URL to the product on Provident\'s website')

    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', action='append', help='The name of the coin being grabbed. '
                                                          'Specify the argument multiple times '
                                                          'to get multiple coin types.')
        args = parser.parse_args()
        if args['name']:
            coins = Coin.query.filter(Coin.name.in_(args['name'])).all()
        else:
            coins = Coin.query.all()
        ret = {'coins': [{'name': coin.name, 'weight': coin.weight, 'metal': coin.metal,
                          'actual_weight': coin.actual_weight, 'ngc': coin.ngc_url, 
                          'pcgs': coin.pcgs_url, 'jmb': coin.jm_url, 'apmex': coin.apmex_url,
                          'shinybars': coin.shinybars_url, 'provident': coin.provident_url} for
                          coin in coins]}
        return ret, 200
                           

    def post(self):
        required_args = ['name', 'weight', 'actual_weight', 'metal', 'country']
        for arg in self.parser.args:
            if arg.name in required_args:
                arg.required = True
        args = self.parser.parse_args()
        stripped = {arg: args[arg] for arg in args if arg not in required_args}
        coin = Coin(args['name'], args['weight'], args['actual_weight'], args['metal'],
                    args['country'], **stripped)
        db.session.add(coin)
        db.session.commit()
        return {'message': 'Success'}, 200

    def put(self):
        for arg in self.parser.args:
            if arg.name == 'name':
                arg.required = True
        args = self.parser.parse_args()
        coin = Coin.query.filter_by(name=args['name']).first()
        if not coin:
            return {'message': 'ERROR: That coin does not exist'}, 400
        for arg in args:
            if arg == 'name' or not args[arg]:
                continue
            if hasattr(coin, arg):
                setattr(coin, arg, args[arg])
        db.session.commit()
        return {'message': 'Success'}, 200

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', type=str, required=True,
                            help='The name of the coin to be deleted')
        args = parser.parse_args()
        coin = Coin.query.filter_by(name=args['name']).first()
        if not coin:
            return {'message': 'ERROR: Coin does not exist'}, 400
        db.session.delete(coin)
        db.session.commit()
        return {'message': 'Success'}, 200


class ItemResource(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('id', type=int, help='The item\'s ID number')
    parser.add_argument('coin_name', type=str, help='Used to look up the type of coin for the item by name')
    parser.add_argument('purchase_price', type=float, help='The purchase price of the item')
    parser.add_argument('purchase_date', type=str, help='A date string representing the purchase date of the item')
    parser.add_argument('purchased_from', type=str, help='Who the item was purchased from')
    parser.add_argument('purchase_spot', type=float, help='Spot price at the time of purchase')
    parser.add_argument('sold', type=bool, default=False, help='Boolean for whether or not the item has been sold')
    parser.add_argument('sold_price', type=float, help='The price the item was sold for')
    parser.add_argument('sold_date', type=str, help='A date string representing the sold date of the item')
    parser.add_argument('sold_to', type=str, help='Who the item was sold to')
    parser.add_argument('sold_spot', type=float, help='Spot price at the time of sale')
    parser.add_argument('shipping_charged', type=float, help='The amount of shipping charged to the buyer')
    parser.add_argument('shipping_cost', type=float, help='The actual cost of shipping the item')

    def get(self):
         parser = reqparse.RequestParser()
         parser.add_argument('id', action='append', help='The id of the item being grabbed. '
                                                           'Specify the argument multiple times '
                                                           'to get multiple items.')
         args = parser.parse_args()
         if args['id']:
             items = Item.query.filter(Item.id.in_(args['id'])).all()
         else:
             items = Item.query.all()
         ret = {'items': [{} for item in items]}
         return ret, 200

    def post(self):
        required_args = ['coin_name', 'purchase_price', 'purchase_date', 'purchased_from',
                         'purchase_spot', 'sold']
        for arg in self.parser.args:
            if arg.name in required_args:
                arg.required = True
        args = self.parser.parse_args()
        stripped = {arg: args[arg] for arg in args if arg not in required_args}
        coin_id = Coin.query.filter_by(name=args['coin_name']).first().id
        item = Item(coin_id, args['purchase_price'], args['purchase_date'], args['purchased_from'],
                    args['purchase_spot'], args['sold'], **stripped)
        db.session.add(item)
        db.session.commit()
        return {'message': 'Success'}, 200

    def put(self):
        for arg in self.parser.args:
            if arg.name == 'id':
                arg.required = True
        args = self.parser.parse_args()
        item = Item.query.filter_by(id=args['id']).first()
        if not item:
            return {'message': 'ERROR: That item does not exist'}, 400
        for arg in args:
            if arg == 'id' or not args[arg]:
                continue
            if hasattr(item, arg):
                setattr(item, arg, args[arg])
        db.session.commit()
        return {'message': 'Success'}, 200

    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='The ID of the item being deleted')
        args = parser.parse_args()
        item = Item.query.filter_by(id=args['id']).first()
        if not item:
            return {'message': 'ERROR: Coin does not exist'}, 400
        db.session.delete(item)
        db.session.commit()
        return {'message': 'Success'}, 200


api.add_resource(CoinResource, '/api/coin')
api.add_resource(ItemResource, '/api/item')


# ------
# routes
# ------
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('index.html')


@app.route('/inventory')
@login_required
@check_confirmed
def inventory():
    form = ItemForm()
    return render_template('inventory.html', form=form)


@app.route('/administrator')
@login_required
@check_confirmed
@check_admin
def admin():
    form = CoinForm()
    return render_template('admin.html', form=form)


@app.route('/home')
@login_required
@check_confirmed
def home():
    return render_template('home.html')


# --------------
# error handlers
# --------------
@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


# -------------------------------------
# user login/logout/registration routes
# -------------------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            if hashing.check_value(user.password, form.password.data, salt=user.salt):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                flash('Successfully logged in!', 'success')
                return redirect(url_for('home'))
            else:
                flash('Incorrect username or password.', 'error')
        else:
            flash('Incorrect username or password.', 'error')
    if request.method == 'POST' and not form.validate():
        flash_errors(form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if not user:
            salt = os.urandom(app.config['SALT_LENGTH'])
            pswd = hashing.hash_value(form.password.data, salt=salt)
            user = User(form.email.data, pswd, salt)
            db.session.add(user)
            db.session.commit()
            # ------------------
            # registration token
            # ------------------
            token = generate_confirmation_token(user.email)
            confirm_url = url_for('confirm_email', token=token, _external=True)
            html = render_template('activate.html', confirm_url=confirm_url)
            send_email(user, html)
            flash('A confirmation email has been sent via email.', 'success')
            login_user(user)
            return redirect(url_for('unconfirmed'))
        else:
            # user exists
            flash('A user with that email already exists.', 'error')
    if request.method == 'POST' and not form.validate():
        flash_errors(form)
    return render_template('register.html', form=form)


@app.route('/confirm/<token>')
@login_required
def confirm_email(token):
    try:
        email = confirm_token(token)
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
        return redirect(url_for('unconfirmed'))
    user = User.query.get(email)
    if user:
        if user.confirmed:
            flash('Account already confirmed. Please login.', 'success')
            return redirect(url_for('login'))
        else:
            user.confirmed = True
            db.session.add(user)
            db.session.commit()
            flash('You have confirmed your account. Thanks!', 'success')
            return redirect(url_for('index'))
    else:
        flash('Not a valid email address.', 'error')
        return redirect(url_for('unconfirmed'))


@app.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('home')
    flash('Please confirm your account!', 'warning')
    return render_template('unconfirmed.html')


@app.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('confirm_email', token=token, _external=True)
    html = render_template('activate.html', confirm_url=confirm_url)
    send_email(current_user, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('unconfirmed'))

