"""
All web forms for the application
"""
from flask.ext.wtf import Form
from wtforms import StringField, FloatField, SelectField, BooleanField, PasswordField
from wtforms.fields.html5 import DateField, EmailField
from wtforms.validators import DataRequired, Email, EqualTo


class CoinForm(Form):
    name = StringField('Coin/bar name')
    weight = FloatField('Weight of main precious metal (ozt)')
    actual_weight = FloatField('The actual weight of the coin (ozt)')
    metal = SelectField('The main precious metal', choices=[('gold', 'Gold'), ('silver', 'Silver'),
                                                            ('platinum', 'Platinum'), ('palladium', 'Palladium')])
    country = StringField('The country of origin')
    ngc_url = StringField('The URL to a comparable NGC listing')
    pcgs_url = StringField('The URL to a comparable PCGS listing')
    jm_url = StringField('The URL to this item at JMBullion')
    apmex_url = StringField('The URL to this item at APMEX')
    shinybars_url = StringField('The URL to this item at ShinyBars')
    provident_url = StringField('The URL to this item at Provident Metals')


class ItemForm(Form):
    name = SelectField('The name of the coin/bar', choices=[])  # fill in choices dynamically later
    purchase_price = FloatField('The purchase price of the item')
    purchase_date = DateField('The purchase date of the item', format='%m-%d-%Y')
    purchased_from = StringField('Who or where you bought the item from')
    purchase_spot = FloatField('Spot price at the tiem of purchase')
    sold = BooleanField('Sold')
    sold_price = FloatField('The price you sold the item for')
    sold_date = DateField('The date of the sale', format='%m-%d-%Y')
    sold_to = StringField('Who the item was sold to')
    sold_spot = FloatField('Spot price at the time of sale')
    shipping_charged = FloatField('The amount of shipping cost charged')
    shipping_cost = FloatField('The actual cost of shipping')


class LoginForm(Form):
    email = EmailField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])


class RegistrationForm(Form):
    email = EmailField('Email address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(),
                                                     EqualTo('confirm', message='Passwords must match.')])
    confirm = PasswordField('Repeat password', validators=[DataRequired()])

