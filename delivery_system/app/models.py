"""
Database models for Delivery system
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """User model - admin and delivery users"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    role = db.Column(db.String(20), default='delivery')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)

    delivery_agent = db.relationship('DeliveryAgent', backref='user', uselist=False, cascade='all, delete-orphan')

    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)

    def is_admin(self):
        return self.role == 'admin'

    def is_delivery(self):
        return self.role == 'delivery'

    def __repr__(self):
        return f'<User {self.username}>'


class Shopkeeper(db.Model):
    """Shopkeeper profile for order context"""
    __tablename__ = 'shopkeepers'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    shop_name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(80))
    contact_number = db.Column(db.String(20))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Shopkeeper {self.shop_name}>'


class DeliveryAgent(db.Model):
    """Delivery agent profile"""
    __tablename__ = 'delivery_agents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    vehicle_number = db.Column(db.String(40))
    city = db.Column(db.String(80))
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    deliveries = db.relationship('Delivery', backref='delivery_agent', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DeliveryAgent {self.user_id}>'


class Order(db.Model):
    """Order model for delivery assignments"""
    __tablename__ = 'orders'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('shopkeepers.id'), nullable=True)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    estimated_delivery_date = db.Column(db.Date)
    assigned_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    delivery_address = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    delivery_proof = db.Column(db.String(255))
    payment_method = db.Column(db.String(80), default='Cash on Delivery')
    payment_status = db.Column(db.String(50), default='Pending')
    payment_reference = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    delivery = db.relationship('Delivery', backref='order', uselist=False, cascade='all, delete-orphan')
    user = db.relationship('User', backref='orders')
    shopkeeper = db.relationship('Shopkeeper', backref='assigned_orders')

    def __repr__(self):
        return f'<Order {self.id}>'


class Delivery(db.Model):
    """Delivery assignment for an order"""
    __tablename__ = 'deliveries'

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False, unique=True)
    delivery_agent_id = db.Column(db.Integer, db.ForeignKey('delivery_agents.id'), nullable=False)
    status = db.Column(db.String(30), default='Assigned')
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
    picked_up_at = db.Column(db.DateTime)
    out_for_delivery_at = db.Column(db.DateTime)
    delivered_at = db.Column(db.DateTime)
    otp_code = db.Column(db.String(8))
    otp_verified_at = db.Column(db.DateTime)
    delivery_fee = db.Column(db.Float, default=0.0)
    cash_to_collect = db.Column(db.Float, default=0.0)
    last_lat = db.Column(db.Float)
    last_lng = db.Column(db.Float)
    last_location_at = db.Column(db.DateTime)
    notes = db.Column(db.Text)

    status_updates = db.relationship('DeliveryStatusUpdate', backref='delivery', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Delivery order={self.order_id} agent={self.delivery_agent_id}>'


class DeliveryStatusUpdate(db.Model):
    """Delivery status timeline entry"""
    __tablename__ = 'delivery_status_updates'

    id = db.Column(db.Integer, primary_key=True)
    delivery_id = db.Column(db.Integer, db.ForeignKey('deliveries.id'), nullable=False)
    status = db.Column(db.String(30), nullable=False)
    note = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<DeliveryStatusUpdate {self.delivery_id} {self.status}>'
