"""
Independent Database Models for Shopkeeper System
No admin system dependency - Shopkeeper only models
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json


class User(UserMixin, db.Model):
    """User model - Shopkeeper only"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    shopkeeper = db.relationship('Shopkeeper', backref='user', uselist=False, cascade='all, delete-orphan')
    ratings = db.relationship('MedicineRating', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Shopkeeper(db.Model):
    """Shopkeeper profile - Shop information"""
    __tablename__ = 'shopkeepers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    shop_name = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(80), nullable=False)
    license_document = db.Column(db.String(255))
    contact_number = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(80))
    verified = db.Column(db.Boolean, default=False)  # Admin verification status
    verified_at = db.Column(db.DateTime, nullable=True)
    verification_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    medicines = db.relationship('Medicine', backref='shopkeeper', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Shopkeeper {self.shop_name}>'


class Medicine(db.Model):
    """Medicine model - Shopkeeper's inventory"""
    __tablename__ = 'medicines'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text)
    strength_value = db.Column(db.Float)
    strength_unit = db.Column(db.String(20))
    price = db.Column(db.Float, nullable=False)
    stock_quantity = db.Column(db.Integer, default=0)
    requires_prescription = db.Column(db.Boolean, default=False)
    side_effects = db.Column(db.Text)
    usage_instructions = db.Column(db.Text)
    image = db.Column(db.String(255), default='images/medicine-default.png')
    gallery_images = db.Column(db.Text, default='[]')
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('shopkeepers.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='medicine', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('MedicineRating', backref='medicine', lazy=True, cascade='all, delete-orphan')

    def get_gallery_images(self):
        """Return gallery image paths as a deduplicated list."""
        images = []

        if self.gallery_images:
            try:
                parsed = json.loads(self.gallery_images)
                if isinstance(parsed, list):
                    images.extend(parsed)
            except (TypeError, ValueError, json.JSONDecodeError):
                pass

        if self.image and self.image != 'images/medicine-default.png' and self.image not in images:
            images.insert(0, self.image)

        clean = []
        for image in images:
            if image and image not in clean:
                clean.append(image)

        return clean

    def set_gallery_images(self, images):
        """Persist gallery images JSON and keep primary image synced."""
        clean = []
        for image in images or []:
            if image and image not in clean:
                clean.append(image)

        self.gallery_images = json.dumps(clean)
        if clean:
            self.image = clean[0]
    
    def __repr__(self):
        return f'<Medicine {self.name}>'


class Order(db.Model):
    """Customer Order"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('shopkeepers.id'), nullable=True)
    customer_name = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    customer_email = db.Column(db.String(120))
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    delivery_address = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    delivery_proof = db.Column(db.String(255))
    estimated_delivery_date = db.Column(db.Date)
    delivery_date = db.Column(db.DateTime)
    payment_method = db.Column(db.String(80))
    payment_status = db.Column(db.String(50), default='Pending')
    payment_reference = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='orders')
    shopkeeper = db.relationship('Shopkeeper', backref='orders')
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id}>'


class OrderItem(db.Model):
    """Individual items in an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    rating = db.relationship('MedicineRating', backref='order_item', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'


class MedicineRating(db.Model):
    """User rating for a purchased medicine"""
    __tablename__ = 'medicine_ratings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    order_item_id = db.Column(db.Integer, db.ForeignKey('order_items.id'), nullable=False, unique=True)
    rating = db.Column(db.Integer, nullable=False)
    review_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<MedicineRating {self.medicine_id} {self.rating}>'


class Notification(db.Model):
    """Order notifications and updates"""
    __tablename__ = 'notifications'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))  # order_placed, assigned, ready, delivered, etc.
    related_order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    order = db.relationship('Order', backref='notifications')
    
    def __repr__(self):
        return f'<Notification {self.id} for user {self.user_id}>'
