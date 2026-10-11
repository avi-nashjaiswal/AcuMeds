"""
Flask application initialization
"""
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from config import MANUAL_UPI_ID as DEFAULT_MANUAL_UPI_ID, MANUAL_UPI_NAME as DEFAULT_MANUAL_UPI_NAME
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
    """Load KEY=VALUE entries from env files when launching via python run.py."""
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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') or 'acumeds-pharmacy-prod-secret-key-2026'
    app.config['SESSION_COOKIE_NAME'] = 'acumeds_pharmacy_session'
    app.config['DEFAULT_LANGUAGE'] = DEFAULT_LANGUAGE

    # Paytm configuration (loaded from environment variables)
    app.config['PAYTM_ENV'] = os.getenv('PAYTM_ENV', 'prod')
    app.config['PAYTM_MID'] = os.getenv('PAYTM_MID', '')
    app.config['PAYTM_MERCHANT_KEY'] = os.getenv('PAYTM_MERCHANT_KEY', '')
    app.config['PAYTM_WEBSITE'] = os.getenv('PAYTM_WEBSITE', 'DEFAULT')
    app.config['PAYTM_CALLBACK_URL'] = os.getenv('PAYTM_CALLBACK_URL', '')
    app.config['PAYTM_CHANNEL_ID'] = os.getenv('PAYTM_CHANNEL_ID', 'WEB')
    app.config['PAYTM_INDUSTRY_TYPE'] = os.getenv('PAYTM_INDUSTRY_TYPE', 'Retail')
    app.config['MANUAL_UPI_ID'] = os.getenv('MANUAL_UPI_ID', DEFAULT_MANUAL_UPI_ID).strip()
    app.config['MANUAL_UPI_NAME'] = os.getenv('MANUAL_UPI_NAME', DEFAULT_MANUAL_UPI_NAME).strip() or 'AcuMeds'
    app.config['ENABLE_PAYMENT_GATEWAY'] = bool(
        app.config['PAYTM_MID'] and app.config['PAYTM_MERCHANT_KEY']
    )

    # SMS configuration (for delivery OTP)
    app.config['SMS_PROVIDER'] = os.getenv('SMS_PROVIDER', 'console').strip().lower()
    app.config['SMS_COUNTRY_CODE'] = os.getenv('SMS_COUNTRY_CODE', '+91').strip() or '+91'
    app.config['TWILIO_ACCOUNT_SID'] = os.getenv('TWILIO_ACCOUNT_SID', '').strip()
    app.config['TWILIO_AUTH_TOKEN'] = os.getenv('TWILIO_AUTH_TOKEN', '').strip()
    app.config['TWILIO_FROM_NUMBER'] = os.getenv('TWILIO_FROM_NUMBER', '').strip()
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '').strip()
    app.config['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'
    
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
    
    # Enable ProxyFix for reverse-proxy production deployments (Nginx/Render/Railway)
    try:
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    except Exception:
        pass

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

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
    
    # Load user function for Flask-Login
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    from app.routes import auth_bp, medicine_bp, cart_bp, order_bp, delivery_bp, recommendation_bp, admin_bp, main_bp_final_unique, doctor_consultation_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(medicine_bp)
    app.register_blueprint(cart_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(delivery_bp)
    app.register_blueprint(recommendation_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(doctor_consultation_bp)
    app.register_blueprint(main_bp_final_unique)  # Registering the final unique main_bp_final_unique blueprint

    @app.route('/hub')
    def acumeds_live_hub():
        """Serve AcuMeds Live Project Hub dashboard."""
        from flask import send_file
        hub_path = os.path.join(project_root, 'AcuMeds_Live_Hub.html')
        if os.path.exists(hub_path):
            return send_file(hub_path)
        return "Live Hub not found", 404


    @app.context_processor
    def inject_cart_count():
        """Provide cart count for the navbar badge."""
        try:
            from flask_login import current_user
            from app.models import CartItem

            if current_user.is_authenticated and current_user.id != 1:
                existing_count = CartItem.query.filter_by(user_id=current_user.id).count()
                if existing_count == 0:
                    guest_items = CartItem.query.filter_by(user_id=1).all()
                    if guest_items:
                        for item in guest_items:
                            item.user_id = current_user.id
                        db.session.commit()

            user_id = current_user.id if current_user.is_authenticated else 1
            cart_count = CartItem.query.filter_by(user_id=user_id).count()
        except Exception:
            cart_count = 0

        return {'cart_count': cart_count}
    
    # Create tables
    with app.app_context():
        db.create_all()
        # Ensure DB has upgraded recommendation columns for existing databases
        try:
            import sqlite3
            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(recommendations)")
            cols = [row[1] for row in cur.fetchall()]
            if 'symptoms_matched' not in cols:
                try:
                    cur.execute("ALTER TABLE recommendations ADD COLUMN symptoms_matched TEXT")
                except sqlite3.OperationalError:
                    pass
            if 'confidence' not in cols:
                try:
                    cur.execute("ALTER TABLE recommendations ADD COLUMN confidence INTEGER DEFAULT 0")
                except sqlite3.OperationalError:
                    pass
            # Add patient detail columns if missing
            if 'patient_name' not in cols:
                try:
                    cur.execute("ALTER TABLE recommendations ADD COLUMN patient_name TEXT")
                except sqlite3.OperationalError:
                    pass
            # Ensure users table has age/gender/role/admin columns
            try:
                cur.execute("PRAGMA table_info(users)")
                user_cols = [r[1] for r in cur.fetchall()]
                if 'age' not in user_cols:
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN age INTEGER")
                    except sqlite3.OperationalError:
                        pass
                if 'gender' not in user_cols:
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN gender TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'role' not in user_cols:
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'customer'")
                    except sqlite3.OperationalError:
                        pass
                if 'is_admin' not in user_cols:
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE")
                    except sqlite3.OperationalError:
                        pass
                if 'is_active' not in user_cols:
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                    except sqlite3.OperationalError:
                        pass
                conn.commit()
            except Exception:
                pass
            if 'patient_age' not in cols:
                try:
                    cur.execute("ALTER TABLE recommendations ADD COLUMN patient_age INTEGER")
                except sqlite3.OperationalError:
                    pass
            if 'patient_gender' not in cols:
                try:
                    cur.execute("ALTER TABLE recommendations ADD COLUMN patient_gender TEXT")
                except sqlite3.OperationalError:
                    pass
            # Ensure symptom_title column exists as well
            if 'symptom_title' not in cols:
                try:
                    cur.execute("ALTER TABLE recommendations ADD COLUMN symptom_title TEXT")
                except sqlite3.OperationalError:
                    pass

            # Ensure orders table has payment columns
            try:
                cur.execute("PRAGMA table_info(orders)")
                order_cols = [r[1] for r in cur.fetchall()]
                if 'payment_method' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN payment_method TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'payment_status' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN payment_status TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'payment_reference' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN payment_reference TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_request_status' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_request_status TEXT DEFAULT 'None'")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_request_amount' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_request_amount REAL")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_request_reason' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_request_reason TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_requested_at' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_requested_at TIMESTAMP")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_requested_by' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_requested_by TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_status' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_status TEXT DEFAULT 'Not Refunded'")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_amount' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_amount REAL")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_reason' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_reason TEXT")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_processed_at' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_processed_at TIMESTAMP")
                    except sqlite3.OperationalError:
                        pass
                if 'refund_processed_by' not in order_cols:
                    try:
                        cur.execute("ALTER TABLE orders ADD COLUMN refund_processed_by TEXT")
                    except sqlite3.OperationalError:
                        pass
            except Exception:
                pass

            # Ensure delivery tables exist for existing databases
            try:
                cur.execute("PRAGMA table_info(delivery_agents)")
                if not cur.fetchall():
                    try:
                        cur.execute("CREATE TABLE IF NOT EXISTS delivery_agents (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER UNIQUE NOT NULL, vehicle_number VARCHAR(40), city VARCHAR(80), active BOOLEAN DEFAULT TRUE, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    except sqlite3.OperationalError:
                        pass
                cur.execute("PRAGMA table_info(deliveries)")
                if not cur.fetchall():
                    try:
                        cur.execute("CREATE TABLE IF NOT EXISTS deliveries (id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER UNIQUE NOT NULL, delivery_agent_id INTEGER NOT NULL, status VARCHAR(30) DEFAULT 'Assigned', assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, picked_up_at TIMESTAMP, out_for_delivery_at TIMESTAMP, delivered_at TIMESTAMP, otp_code VARCHAR(8), otp_verified_at TIMESTAMP, delivery_fee DECIMAL(10, 2) DEFAULT 0, cash_to_collect DECIMAL(10, 2) DEFAULT 0, last_lat REAL, last_lng REAL, last_location_at TIMESTAMP, notes TEXT)")
                    except sqlite3.OperationalError:
                        pass
                cur.execute("PRAGMA table_info(delivery_status_updates)")
                if not cur.fetchall():
                    try:
                        cur.execute("CREATE TABLE IF NOT EXISTS delivery_status_updates (id INTEGER PRIMARY KEY AUTOINCREMENT, delivery_id INTEGER NOT NULL, status VARCHAR(30) NOT NULL, note TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    except sqlite3.OperationalError:
                        pass
            except Exception:
                pass

            # Ensure medicines table has shopkeeper_id column
            try:
                cur.execute("PRAGMA table_info(medicines)")
                med_cols = [r[1] for r in cur.fetchall()]
                if 'shopkeeper_id' not in med_cols:
                    try:
                        cur.execute("ALTER TABLE medicines ADD COLUMN shopkeeper_id INTEGER")
                    except sqlite3.OperationalError:
                        pass
                if 'gallery_images' not in med_cols:
                    try:
                        cur.execute("ALTER TABLE medicines ADD COLUMN gallery_images TEXT DEFAULT '[]'")
                    except sqlite3.OperationalError:
                        pass
            except Exception:
                pass

            # Ensure cart_items table has shopkeeper_id column
            try:
                cur.execute("PRAGMA table_info(cart_items)")
                cart_cols = [r[1] for r in cur.fetchall()]
                if 'shopkeeper_id' not in cart_cols:
                    try:
                        cur.execute("ALTER TABLE cart_items ADD COLUMN shopkeeper_id INTEGER")
                    except sqlite3.OperationalError:
                        pass
            except Exception:
                pass

            # Ensure doctor_appointments table has payment columns
            try:
                cur.execute("PRAGMA table_info(doctor_appointments)")
                appt_cols = [r[1] for r in cur.fetchall()]
                if 'payment_method' not in appt_cols:
                    try:
                        cur.execute("ALTER TABLE doctor_appointments ADD COLUMN payment_method VARCHAR(80)")
                    except sqlite3.OperationalError:
                        pass
                if 'payment_reference' not in appt_cols:
                    try:
                        cur.execute("ALTER TABLE doctor_appointments ADD COLUMN payment_reference VARCHAR(120)")
                    except sqlite3.OperationalError:
                        pass
                if 'transaction_id' not in appt_cols:
                    try:
                        cur.execute("ALTER TABLE doctor_appointments ADD COLUMN transaction_id VARCHAR(120)")
                    except sqlite3.OperationalError:
                        pass
                if 'invoice_number' not in appt_cols:
                    try:
                        cur.execute("ALTER TABLE doctor_appointments ADD COLUMN invoice_number VARCHAR(120)")
                    except sqlite3.OperationalError:
                        pass
                if 'payment_date' not in appt_cols:
                    try:
                        cur.execute("ALTER TABLE doctor_appointments ADD COLUMN payment_date TIMESTAMP")
                    except sqlite3.OperationalError:
                        pass
            except Exception:
                pass

            conn.commit()
            conn.close()
        except Exception:
            pass
        # (end DB migration try)
    
    return app
