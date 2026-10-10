# AcuMeds Application Configuration

import os

## Application Settings

# Set to True for development, False for production
DEBUG = True

# Secret key for session management - CHANGE IN PRODUCTION!
SECRET_KEY = 'your-secret-key-change-in-production-1234567890'

# Database Configuration
_DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db'))
SQLALCHEMY_DATABASE_URI = f'sqlite:///{_DB_PATH}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Upload Configuration
UPLOAD_FOLDER = 'static/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size

# Session Configuration
PERMANENT_SESSION_LIFETIME = 3600  # 1 hour in seconds
SESSION_REFRESH_EACH_REQUEST = True

## Email Configuration (for future use)
# MAIL_SERVER = 'smtp.gmail.com'
# MAIL_PORT = 587
# MAIL_USE_TLS = True
# MAIL_USERNAME = 'your-email@gmail.com'
# MAIL_PASSWORD = 'your-password'

## Payment Gateway (Paytm)
PAYTM_ENV = os.getenv('PAYTM_ENV', 'prod')  # prod | staging
PAYTM_MID = os.getenv('PAYTM_MID', '')
PAYTM_MERCHANT_KEY = os.getenv('PAYTM_MERCHANT_KEY', '')
PAYTM_WEBSITE = os.getenv('PAYTM_WEBSITE', 'DEFAULT')
PAYTM_CALLBACK_URL = os.getenv('PAYTM_CALLBACK_URL', '')
PAYTM_CHANNEL_ID = os.getenv('PAYTM_CHANNEL_ID', 'WEB')
PAYTM_INDUSTRY_TYPE = os.getenv('PAYTM_INDUSTRY_TYPE', 'Retail')

## Manual UPI (no automatic verification)
MANUAL_UPI_ID = os.getenv('MANUAL_UPI_ID', 'avinashbarai722@okhdfcbank')
MANUAL_UPI_NAME = os.getenv('MANUAL_UPI_NAME', 'Avinash Barai')

## Application Info
APP_NAME = 'AcuMeds'
APP_VERSION = '1.0.0'
APP_AUTHOR = 'AcuMeds Development Team'

## Feature Flags
ENABLE_PRESCRIPTIONS = True
ENABLE_AI_RECOMMENDATIONS = True
ENABLE_USER_REVIEWS = False  # Future feature
ENABLE_PAYMENT_GATEWAY = bool(PAYTM_MID and PAYTM_MERCHANT_KEY)

## Logging Configuration
LOG_FILE = 'logs/app.log'
LOG_LEVEL = 'INFO'

## AI Recommendation Settings
AI_CONFIDENCE_THRESHOLD = 10  # Minimum confidence percentage
AI_RECOMMENDATION_LIMIT = 3  # Max recommendations to show

## Pagination
ITEMS_PER_PAGE = 20

## Security
PASSWORD_MIN_LENGTH = 6
SESSION_TIMEOUT = 3600

## General
CURRENCY = 'INR'
CURRENCY_SYMBOL = '₹'
TIMEZONE = 'Asia/Kolkata'
