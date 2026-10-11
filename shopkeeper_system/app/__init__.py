"""
Flask application initialization
"""
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta
import os
import sqlite3
from app.localization import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    get_current_language,
    get_language_options,
    set_current_language,
    translate,
    translate_message,
)

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()


def _load_env_file(file_path):
    """Load KEY=VALUE entries from an env file into os.environ if missing."""
    if not os.path.exists(file_path):
        return

    try:
        with open(file_path, 'r', encoding='utf-8') as env_file:
            for raw_line in env_file:
                line = raw_line.strip()
                if not line or line.startswith('#') or '=' not in line:
                    continue

                name, value = line.split('=', 1)
                name = name.strip()
                value = value.strip()

                if not name or name in os.environ:
                    continue

                if (
                    (value.startswith('"') and value.endswith('"'))
                    or (value.startswith("'") and value.endswith("'"))
                ):
                    value = value[1:-1]

                os.environ[name] = value
    except OSError:
        return


def _load_runtime_env(project_root):
    """Load local env files when app is started via python run.py."""
    _load_env_file(os.path.join(project_root, '.env.local'))
    _load_env_file(os.path.join(project_root, '.env'))

def create_app():
    """Application factory function"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    project_root = os.path.abspath(os.path.join(basedir, os.pardir, os.pardir))
    _load_runtime_env(project_root)
    
    # Configuration
    # Serve project-level `static/` directory (not `app/static`)
    project_static = os.path.join(os.path.dirname(basedir), 'static')
    app = Flask(
        __name__,
        template_folder=os.path.join(basedir, '..', 'templates'),
        static_folder=project_static,
        static_url_path='/static'
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') or 'acumeds-shopkeeper-prod-secret-key-2026'
    app.config['SESSION_COOKIE_NAME'] = 'acumeds_shopkeeper_session'
    app.config['DEFAULT_LANGUAGE'] = DEFAULT_LANGUAGE
    
    # Database configuration - Use SHARED pharmacy database or DATABASE_URL
    database_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        db_path = os.path.join(project_root, 'admin_system', 'database', 'pharmacy.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload configuration (point to project-level static uploads)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(basedir), 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['OPENAI_API_KEY'] = (os.environ.get('OPENAI_API_KEY') or '').strip()
    app.config['OPENAI_MODEL'] = (os.environ.get('OPENAI_MODEL') or 'gpt-4o-mini').strip() or 'gpt-4o-mini'
    
    # Enable ProxyFix for reverse-proxy production deployments
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    except Exception:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.remember_cookie_duration = timedelta(days=30)  # Remember for 30 days
    login_manager.remember_cookie_secure = False  # Allow non-HTTPS for localhost
    
    # Session configuration
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)  # 7 days
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True
    app.config['SESSION_COOKIE_SECURE'] = False  # Allow non-HTTPS for localhost
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    
    # User loader for flask-login
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import User
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    @app.before_request
    def _load_language_context():
        g.current_language = get_current_language()

    @app.context_processor
    def inject_localization_helpers():
        return {
            'current_language': get_current_language(),
            'supported_languages': SUPPORTED_LANGUAGES,
            'language_options': get_language_options(),
            't': translate,
            '_': translate,
            'translate_message': translate_message,
            'set_current_language': set_current_language,
        }
    
    # Register blueprints - SHOPKEEPER SYSTEM ONLY
    from app.routes import auth_bp, dashboard_bp, api_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    @app.context_processor
    def inject_notification_count():
        """Provide unread notification count for navbar badges."""
        try:
            from flask_login import current_user
            from app.models import Notification

            if current_user.is_authenticated:
                unread = Notification.query.filter_by(
                    user_id=current_user.id,
                    is_read=False
                ).count()
            else:
                unread = 0
        except Exception:
            unread = 0

        return {'notification_count': unread}
    
    # Create database tables
    with app.app_context():
        db.create_all()

        # Ensure shared DB has gallery_images column for multi-photo medicines
        try:
            db_file = db_path
            conn = sqlite3.connect(db_file)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(medicines)")
            med_cols = [r[1] for r in cur.fetchall()]
            if 'gallery_images' not in med_cols:
                try:
                    cur.execute("ALTER TABLE medicines ADD COLUMN gallery_images TEXT DEFAULT '[]'")
                except sqlite3.OperationalError:
                    pass

            cur.execute("PRAGMA table_info(orders)")
            order_cols = [r[1] for r in cur.fetchall()]
            if 'payment_method' not in order_cols:
                try:
                    cur.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT")
                except sqlite3.OperationalError:
                    pass
            if 'payment_status' not in order_cols:
                try:
                    cur.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT DEFAULT 'Pending'")
                except sqlite3.OperationalError:
                    pass
            if 'payment_reference' not in order_cols:
                try:
                    cur.execute("ALTER TABLE orders ADD COLUMN payment_reference TEXT")
                except sqlite3.OperationalError:
                    pass
            conn.commit()
            conn.close()
        except Exception:
            pass
    
    return app
