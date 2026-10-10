"""
Database models for the Doctor Portal application
Uses shared SQLite database with all AcuMeds portals
"""
try:
    from . import db
except ImportError:
    from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json


class User(UserMixin, db.Model):
    """User model representing doctors, patients, shopkeepers, delivery agents, and admins"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(80))
    age = db.Column(db.Integer)
    gender = db.Column(db.String(20))
    role = db.Column(db.String(20), default='doctor')  # customer, shopkeeper, delivery, doctor, admin
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)

    # Doctor Profile Relationship
    doctor = db.relationship('Doctor', backref='user', uselist=False, cascade='all, delete-orphan')
    patient_appointments = db.relationship('DoctorAppointment', backref='patient', lazy=True, foreign_keys='DoctorAppointment.patient_id', cascade='all, delete-orphan')
    patient_prescriptions = db.relationship('DoctorPrescription', backref='patient', lazy=True, foreign_keys='DoctorPrescription.patient_id', cascade='all, delete-orphan')

    def is_doctor(self):
        return self.role == 'doctor'

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'


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
        return f'<Doctor {self.id} - {self.specialization}>'


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
        return f'<DoctorAppointment {self.id} Status={self.status}>'


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


class Medicine(db.Model):
    """Medicine inventory model"""
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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

    medicine = db.relationship('Medicine')

    def __repr__(self):
        return f'<CartItem {self.medicine_id} x {self.quantity}>'


class Notification(db.Model):
    """Notification model"""
    __tablename__ = 'notifications'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(50))
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Notification {self.id}>'

