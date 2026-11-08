"""Merchandise shop models."""
from .extensions import db
from .models import utcnow


class Merchandise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    description = db.Column(db.Text)
    price = db.Column(db.Float)
    stock = db.Column(db.Integer)
    category = db.Column(db.String(50))  # e.g., 'clothing', 'accessories', 'souvenirs'
    image_url = db.Column(db.String(200))
    guide_id = db.Column(db.Integer, db.ForeignKey('guide.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    @property
    def in_stock(self) -> bool:
        return (self.stock or 0) > 0

    guide = db.relationship('Guide', backref=db.backref('merchandise', lazy=True))
    # Add relationship to CartItem
    cart_items = db.relationship('CartItem', backref='merchandise', lazy=True)
    order_items = db.relationship('OrderItem', backref='merchandise', lazy=True)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    merchandise_id = db.Column(db.Integer, db.ForeignKey('merchandise.id'))
    quantity = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=utcnow)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    total_amount = db.Column(db.Float)
    status = db.Column(db.String(20), default='pending')  # pending, processing, shipped, delivered
    shipping_address = db.Column(db.Text)
    payment_status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    payment_method = db.Column(db.String(50))  # UPI, Card, COD
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)

    # Add relationship to OrderItem
    items = db.relationship('OrderItem', backref='order', lazy=True)
    payment = db.relationship('Payment', backref='order', uselist=False, lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    merchandise_id = db.Column(db.Integer, db.ForeignKey('merchandise.id'))
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)  # Price at the time of purchase

class Payment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'))
    amount = db.Column(db.Float)
    payment_method = db.Column(db.String(50))  # UPI, Card, COD
    transaction_id = db.Column(db.String(100))  # For UPI/Card payments
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=utcnow)
    updated_at = db.Column(db.DateTime, default=utcnow, onupdate=utcnow)
