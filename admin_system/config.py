"""
Configuration for Admin Portal
"""
import os

class Config:
    """Base configuration"""
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # SQLAlchemy
    DB_PATH = os.path.abspath(os.path.join(BASEDIR, 'database', 'pharmacy.db'))
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DB_PATH}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask
    SECRET_KEY = 'admin-portal-secret-key-change-in-production'
    
    # Upload
    UPLOAD_FOLDER = os.path.join(BASEDIR, 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    
    # Flask-Login
    SESSION_COOKIE_SECURE = False  # Set to True in production with HTTPS
    PERMANENT_SESSION_LIFETIME = 86400  # 24 hours
