from flask import Flask
from flask import request
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # TODO: what is this?
db = SQLAlchemy(app)
api = Api(app)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer)
    purchase_price = db.Column(db.Float, nullable=False)
    purchase_date = db.Column(db.DateTime, nullable=False)
    purchased_from = db.Column(db.String(60), nullable=False)
    purchase_spot = db.Column(db.Float, nullable=False)
    sold = db.Column(db.Boolean)
    sold_price = db.Column(db.Float)
    sold_date = db.Column(db.DateTime)
    sold_to = db.Column(db.String(60))
    sold_spot = db.Column(db.Float)
    shipping_charged = db.Column(db.Float)
    shipping_cost = db.Column(db.Float)
    coin_id = db.Column(db.Integer, db.ForeignKey('coin.id'), nullable=False)

    def __init__(self, coin_id, purchase_price, purchase_date, purchased_from, purchase_spot,
                 sold=False, sold_price=None, sold_date=None, sold_to=None, sold_spot=None,
                 shipping_charged=None, shipping_cost=None):
        self.coin_id = coin_id
        self.purchase_price = purchase_price
        self.purchase_date = purchase_date
        self.purchased_from = purchased_from
        self.purchase_spot = purchase_spot
        self.sold = sold
        if sold_price:
            self.sold_price = sold_price
        if sold_date:
            self.sold_date = sold_date
        if sold_to:
            self.sold_to = sold_to
        if sold_spot:
            self.sold_spot = sold_spot
        if shipping_charged:
            self.shipping_charged = shipping_charged
        if shipping_cost:
            self.shipping_cost = shipping_cost

    def __repr__(self):
        return '<Item %d>' % self.id
    

class Coin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(60), nullable=False, unique=True)
    weight = db.Column(db.Float, nullable=False)
    actual_weight = db.Column(db.Float, nullable=False)
    metal = db.Column(db.String(15), nullable=False)
    country = db.Column(db.String(30), nullable=False)
    items = db.relationship('Item', backref='coin', lazy='dynamic')
    ngc_url = db.Column(db.String(200))
    pcgs_url = db.Column(db.String(200))
    jm_url = db.Column(db.String(200))
    apmex_url = db.Column(db.String(200))
    shinybars_url = db.Column(db.String(200))
    provident_url = db.Column(db.String(200))
    current_apmex = db.Column(db.Float)
    current_jm = db.Column(db.Float)
    current_provident = db.Column(db.Float)
    current_shinybars = db.Column(db.Float)
    current_pcgs = db.Column(db.Float)
    current_ngc = db.Column(db.Float)

    def __init__(self, name, weight, actual_weight, metal, country, ngc_url='', pcgs_url='',
                 jm_url='', apmex_url='', shinybars_url='', provident_url=''):
        self.name = name
        self.weight = weight
        self.actual_weight = actual_weight
        self.metal = metal
        self.country = country
        if ngc_url:
            self.ngc_url = ngc_url
        if pcgs_url:
            self.pcgs_url = pcgs_url
        if jm_url:
            self.jm_url = jm_url
        if apmex_url:
            self.apmex_url = apmex_url
        if shinybars_url:
            self.shinybars_url = shinybars_url
        if provident_url:
            self.provident_url = provident_url

    def __repr__(self):
        return '<Coin %r>' % self.name


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


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)

