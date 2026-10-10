# AcuMeds Doctor Portal Configuration
import os

DEBUG = True
SECRET_KEY = 'doctor-portal-secret-key-change-in-production-doc999'

# Database Configuration - shared across all portals
_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db'))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{_DB_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Session Configuration
PERMANENT_SESSION_LIFETIME = 3600
SESSION_REFRESH_EACH_REQUEST = True

# Application Info
APP_NAME = 'AcuMeds Doctor Portal'
APP_VERSION = '1.0.0'
APP_AUTHOR = 'AcuMeds Development Team'

# Consultation Settings
DEFAULT_CONSULTATION_FEE = 300.0
CURRENCY = 'INR'
CURRENCY_SYMBOL = '₹'
TIMEZONE = 'Asia/Kolkata'
