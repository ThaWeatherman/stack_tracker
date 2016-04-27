"""
Contains all of the database models
"""
from flask_sqlalchemy import SQLAlchemy

from stacktracker import app


db = SQLAlchemy(app)
# db.create_all()


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



