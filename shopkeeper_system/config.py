# AcuMeds Shopkeeper App Configuration

import os

## Application Settings
DEBUG = True
SECRET_KEY = 'shopkeeper-secret-key-change-in-production-xyz789'

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

## Application Info
APP_NAME = 'AcuMeds Shopkeeper'
APP_VERSION = '1.0.0'
APP_AUTHOR = 'AcuMeds Development Team'

## Feature Flags
ENABLE_PRESCRIPTIONS = True
ENABLE_MEDICINE_MANAGEMENT = True

## Logging Configuration
LOG_FILE = 'logs/app.log'
LOG_LEVEL = 'INFO'

## General
CURRENCY = 'INR'
CURRENCY_SYMBOL = '₹'
TIMEZONE = 'Asia/Kolkata'

# Link to main pharmacy app
PHARMACY_APP_URL = 'http://localhost:5000'
SHOPKEEPER_APP_URL = 'http://localhost:5001'
