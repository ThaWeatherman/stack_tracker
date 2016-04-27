"""
Contains all of the routing views
"""
from flask_restful import Api
from flask_restful import Resource
from flask_restful import reqparse

from stacktracker import app
from stacktracker.models import Coin, Item


api = Api(app)


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

