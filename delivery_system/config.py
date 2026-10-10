# AcuMeds Delivery App Configuration

import os

# Application Settings
DEBUG = True
SECRET_KEY = 'delivery-secret-key-change-in-production-xyz789'

# Database Configuration - shared across all portals
_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db'))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{_DB_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024

# Session Configuration
PERMANENT_SESSION_LIFETIME = 3600
SESSION_REFRESH_EACH_REQUEST = True

# Application Info
APP_NAME = 'AcuMeds Delivery'
APP_VERSION = '1.0.0'
APP_AUTHOR = 'AcuMeds Development Team'

# Delivery Settings
DELIVERY_FEE_DEFAULT = 30.0

# General
CURRENCY = 'INR'
CURRENCY_SYMBOL = 'Rs'
TIMEZONE = 'Asia/Kolkata'
