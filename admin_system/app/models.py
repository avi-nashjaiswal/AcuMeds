"""
Database models for the pharmacy application
"""
from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    """User model - represents customers, shopkeepers, and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))  # Location/city of user
    # Optional profile fields
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    # User role: 'customer', 'shopkeeper', 'admin'
    role = db.Column(db.String(20), default='customer')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    orders = db.relationship('Order', backref='user', lazy=True, cascade='all, delete-orphan')
    cart_items = db.relationship('CartItem', backref='user', lazy=True, cascade='all, delete-orphan')
    prescriptions = db.relationship('Prescription', backref='user', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy=True, cascade='all, delete-orphan')
    shopkeeper = db.relationship('Shopkeeper', backref='user', uselist=False, cascade='all, delete-orphan')
    delivery_agent = db.relationship('DeliveryAgent', backref='user', uselist=False, cascade='all, delete-orphan')
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient_appointments = db.relationship('DoctorAppointment', backref='patient', lazy=True, foreign_keys='DoctorAppointment.patient_id', cascade='all, delete-orphan')
    patient_prescriptions = db.relationship('DoctorPrescription', backref='patient', lazy=True, foreign_keys='DoctorPrescription.patient_id', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    ratings = db.relationship('MedicineRating', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def is_shopkeeper(self):
        """Check if user is a shopkeeper"""
        return self.role == 'shopkeeper'

    def is_delivery_agent(self):
        """Check if user is a delivery agent"""
        return self.role == 'delivery'

    def is_doctor(self):
        """Check if user is a doctor"""
        return self.role == 'doctor'
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Check if password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class Shopkeeper(db.Model):
    """Shopkeeper profile - stores business information for medicine sellers"""
    __tablename__ = 'shopkeepers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    shop_name = db.Column(db.String(120), nullable=False)
    license_number = db.Column(db.String(80))
    license_document = db.Column(db.String(255))  # File path to uploaded license
    city = db.Column(db.String(80))
    contact_number = db.Column(db.String(20))
    verified = db.Column(db.Boolean, default=False)  # Admin verification
    verified_at = db.Column(db.DateTime, nullable=True)  # When admin verified
    verification_notes = db.Column(db.Text)  # Admin verification notes/rejection reason
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Shopkeeper {self.shop_name}>'


class Medicine(db.Model):
    """Medicine model - represents available medicines"""
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
    # Shopkeeper foreign key - NULL means admin/platform default
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('shopkeepers.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    cart_items = db.relationship('CartItem', backref='medicine', lazy=True, cascade='all, delete-orphan')
    order_items = db.relationship('OrderItem', backref='medicine', lazy=True, cascade='all, delete-orphan')
    shopkeeper = db.relationship('Shopkeeper', backref='medicines')
    ratings = db.relationship('MedicineRating', backref='medicine', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Medicine {self.name}>'


class CartItem(db.Model):
    """Shopping cart item"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    added_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_total(self):
        """Calculate total for this cart item"""
        return self.medicine.price * self.quantity
    
    def __repr__(self):
        return f'<CartItem {self.medicine.name} x {self.quantity}>'


class Order(db.Model):
    """Order model - represents customer orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    order_date = db.Column(db.DateTime, default=datetime.utcnow)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Confirmed, Processing, Ready, Delivered
    estimated_delivery_date = db.Column(db.Date)
    # Shopkeeper assignment
    shopkeeper_id = db.Column(db.Integer, db.ForeignKey('shopkeepers.id'), nullable=True)
    assigned_date = db.Column(db.DateTime)
    delivery_date = db.Column(db.DateTime)
    delivery_address = db.Column(db.Text)
    delivery_notes = db.Column(db.Text)
    delivery_proof = db.Column(db.String(255))
    # Payment fields
    payment_method = db.Column(db.String(80))
    payment_status = db.Column(db.String(50), default='Pending')
    payment_reference = db.Column(db.String(120))
    refund_request_status = db.Column(db.String(50), default='None')
    refund_request_amount = db.Column(db.Float)
    refund_request_reason = db.Column(db.Text)
    refund_requested_at = db.Column(db.DateTime)
    refund_requested_by = db.Column(db.String(120))
    refund_status = db.Column(db.String(50), default='Not Refunded')
    refund_amount = db.Column(db.Float)
    refund_reason = db.Column(db.Text)
    refund_processed_at = db.Column(db.DateTime)
    refund_processed_by = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    order_items = db.relationship('OrderItem', backref='order', lazy=True, cascade='all, delete-orphan')
    shopkeeper = db.relationship('Shopkeeper', backref='assigned_orders')
    delivery = db.relationship('Delivery', backref='order', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Order {self.id} - {self.status}>'


class OrderItem(db.Model):
    """Individual item in an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_at_purchase = db.Column(db.Float, nullable=False)

    rating = db.relationship('MedicineRating', backref='order_item', uselist=False, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<OrderItem {self.medicine.name}>'


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


class Prescription(db.Model):
    """User prescription uploads"""
    __tablename__ = 'prescriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    file_path = db.Column(db.String(255))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<Prescription {self.id}>'


class Address(db.Model):
    """User saved addresses"""
    __tablename__ = 'addresses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(80), default='Home')
    recipient = db.Column(db.String(120))
    phone = db.Column(db.String(30))
    address_line = db.Column(db.Text)
    city = db.Column(db.String(80))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(80), default='India')

    user = db.relationship('User', backref='addresses')

    def __repr__(self):
        return f'<Address {self.id} {self.title}>'


class Subscription(db.Model):
    """Auto-refill subscription for a medicine"""
    __tablename__ = 'subscriptions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1)
    interval_days = db.Column(db.Integer, default=30)
    next_run = db.Column(db.Date)
    active = db.Column(db.Boolean, default=True)

    user = db.relationship('User', backref='subscriptions')
    medicine = db.relationship('Medicine')

    def __repr__(self):
        return f'<Subscription {self.id} user={self.user_id} med={self.medicine_id}>'


class Recommendation(db.Model):
    """AI-generated recommendations based on symptoms"""
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    symptoms = db.Column(db.String(500))
    # Optional short title for the symptom case
    symptom_title = db.Column(db.String(200))
    recommended_medicines = db.Column(db.Text)  # JSON format
    symptoms_matched = db.Column(db.Text)  # JSON list of matched symptoms
    # Optional patient details captured at time of recommendation
    patient_name = db.Column(db.String(120))
    patient_age = db.Column(db.Integer)
    patient_gender = db.Column(db.String(20))
    confidence = db.Column(db.Integer, default=0)  # Confidence percent (0-100)
    recommendation_date = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Recommendation {self.id}>'


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


class Doctor(db.Model):
    """Doctor profile model"""
    __tablename__ = 'doctors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)
    specialization = db.Column(db.String(120), nullable=False)
    qualification = db.Column(db.String(120), nullable=False)
    experience_years = db.Column(db.Integer, default=1)
    license_number = db.Column(db.String(80), nullable=False)
    clinic_name = db.Column(db.String(150))
    clinic_address = db.Column(db.Text)
    city = db.Column(db.String(80))
    consultation_fee = db.Column(db.Float, default=300.0)
    bio = db.Column(db.Text)
    rating = db.Column(db.Float, default=4.9)
    total_reviews = db.Column(db.Integer, default=0)
    is_verified = db.Column(db.Boolean, default=False)
    is_available = db.Column(db.Boolean, default=False)
    available_days = db.Column(db.String(100), default='Mon,Tue,Wed,Thu,Fri,Sat')
    available_time_start = db.Column(db.String(20), default='09:00 AM')
    available_time_end = db.Column(db.String(20), default='08:00 PM')
    avatar = db.Column(db.String(255), default='images/doctor-default.png')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    verified_at = db.Column(db.DateTime, nullable=True)
    verification_notes = db.Column(db.Text, nullable=True)
    registration_ref = db.Column(db.String(100), nullable=True)
    approval_letter_ref = db.Column(db.String(100), nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)

    # Relationships
    appointments = db.relationship('DoctorAppointment', backref='doctor', lazy=True, foreign_keys='DoctorAppointment.doctor_id', cascade='all, delete-orphan')
    prescriptions = db.relationship('DoctorPrescription', backref='doctor', lazy=True, foreign_keys='DoctorPrescription.doctor_id', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Doctor {self.user_id} - {self.specialization}>'


class DoctorAppointment(db.Model):
    """Doctor appointment booking model"""
    __tablename__ = 'doctor_appointments'

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    appointment_date = db.Column(db.String(30), nullable=False)
    appointment_time = db.Column(db.String(30), nullable=False)
    consultation_type = db.Column(db.String(30), default='Online Video')  # Online Video, Audio Call, In-Clinic
    patient_name = db.Column(db.String(120))
    patient_age = db.Column(db.Integer)
    patient_gender = db.Column(db.String(20))
    patient_phone = db.Column(db.String(30))
    symptoms = db.Column(db.Text)
    status = db.Column(db.String(30), default='Pending')  # Pending, Confirmed, In Consultation, Completed, Cancelled
    consultation_fee = db.Column(db.Float, default=300.0)
    payment_status = db.Column(db.String(30), default='Paid')  # Paid, Pending, Refunded
    meeting_link = db.Column(db.String(255))
    doctor_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    prescription = db.relationship('DoctorPrescription', backref='appointment', uselist=False, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DoctorAppointment {self.id} Patient={self.patient_id} Doctor={self.doctor_id} Status={self.status}>'


class DoctorPrescription(db.Model):
    """Digital prescription issued by a doctor"""
    __tablename__ = 'doctor_prescriptions'

    id = db.Column(db.Integer, primary_key=True)
    appointment_id = db.Column(db.Integer, db.ForeignKey('doctor_appointments.id'), nullable=True)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctors.id'), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    prescription_code = db.Column(db.String(40), unique=True)
    patient_name = db.Column(db.String(120))
    patient_age = db.Column(db.Integer)
    patient_gender = db.Column(db.String(20))
    vitals_bp = db.Column(db.String(30))
    vitals_pulse = db.Column(db.String(30))
    vitals_temp = db.Column(db.String(30))
    vitals_weight = db.Column(db.String(30))
    diagnosis = db.Column(db.Text, nullable=False)
    general_advice = db.Column(db.Text)
    tests_recommended = db.Column(db.Text)
    follow_up_date = db.Column(db.String(40))
    is_ordered = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    items = db.relationship('DoctorPrescriptionItem', backref='prescription', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<DoctorPrescription {self.prescription_code or self.id}>'


class DoctorPrescriptionItem(db.Model):
    """Medicines listed within a doctor prescription"""
    __tablename__ = 'doctor_prescription_items'

    id = db.Column(db.Integer, primary_key=True)
    prescription_id = db.Column(db.Integer, db.ForeignKey('doctor_prescriptions.id'), nullable=False)
    medicine_id = db.Column(db.Integer, db.ForeignKey('medicines.id'), nullable=True)
    medicine_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(80))      # e.g., "500 mg", "1 tablet"
    frequency = db.Column(db.String(80))   # e.g., "1-0-1 (Twice daily)", "Once daily at night"
    timing = db.Column(db.String(80))      # e.g., "After food", "Before food"
    duration = db.Column(db.String(80))    # e.g., "5 days", "2 weeks"
    instructions = db.Column(db.Text)      # e.g., "Take with warm water"
    quantity = db.Column(db.Integer, default=1)

    medicine = db.relationship('Medicine')

    def __repr__(self):
        return f'<DoctorPrescriptionItem {self.medicine_name}>'

