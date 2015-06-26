from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.extensions import db


class Brand(db.Model):
    __tablename__ = 'brands'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True)
    ca_id = db.Column(db.String(5), unique=True)


class Auction(db.Model):
    __tablename__ = 'auctions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    type = db.Column(db.String(32))
    price = db.Column(db.Numeric(precision=7,scale=2))
    timestamp = db.Column(db.DateTime)
    aid = db.Column(db.String(16))
    site = db.Column(db.String(32))
    link = db.Column(db.Text)
    close = db.Column(db.DateTime)
    quantity = db.Column(db.Integer, default=1)
    finished = db.Column(db.Boolean, default=False)
    _brand_id = db.Column(db.Integer, db.ForeignKey('brands.id'))
    brand = db.relationship('Brand', backref='auctions')

    @hybrid_property
    def price_per_stick(self):
        if self.price and self.quantity:
            return self.price / self.quantity
        else:
            return None

    @hybrid_property
    def time_left(self):
        if not self.finished:
            delta = self.close - datetime.now()
            days = delta.days
            hours = delta.seconds / 3600
            minutes = (delta.seconds % 3600) / 60
            if days < 0 or hours < 0 or minutes < 0:
                days = 0
                hours = 0
                minutes = 0
            return days, hours, minutes
        else:
            return 0, 0, 0
