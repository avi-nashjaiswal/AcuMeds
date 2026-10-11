"""
Flask application initialization
"""
import ast
for _ast_attr in ('Str', 'Num', 'Bytes', 'NameConstant', 'Ellipsis'):
    if not hasattr(ast, _ast_attr):
        setattr(ast, _ast_attr, getattr(ast, 'Constant', object))

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
import warnings

# Globally suppress RequestsDependencyWarning caused by mixed codec dependencies
try:
    from requests.packages.urllib3.exceptions import RequestsDependencyWarning
    warnings.filterwarnings("ignore", category=RequestsDependencyWarning)
except Exception:
    pass

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    """Application factory function"""
    basedir = os.path.abspath(os.path.dirname(__file__))
    
    # Configuration
    # Serve project-level `static/` directory (not `app/static`)
    project_static = os.path.join(os.path.dirname(basedir), 'static')
    app = Flask(
        __name__,
        template_folder=os.path.join(basedir, '..', 'templates'),
        static_folder=project_static,
        static_url_path='/static'
    )
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') or 'adminsecretkey@pharmacy2024!#$%'
    app.config['SESSION_COOKIE_NAME'] = 'acumeds_admin_session'
    
    # Session configuration - prevent logout on each request
    app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 7 * 24 * 3600  # 7 days
    app.config['SESSION_REFRESH_EACH_REQUEST'] = True  # Refresh session on each request

    # SMS configuration (for delivery OTP)
    app.config['SMS_PROVIDER'] = os.getenv('SMS_PROVIDER', 'console').strip().lower()
    app.config['SMS_COUNTRY_CODE'] = os.getenv('SMS_COUNTRY_CODE', '+91').strip() or '+91'
    app.config['TWILIO_ACCOUNT_SID'] = os.getenv('TWILIO_ACCOUNT_SID', '').strip()
    app.config['TWILIO_AUTH_TOKEN'] = os.getenv('TWILIO_AUTH_TOKEN', '').strip()
    app.config['TWILIO_FROM_NUMBER'] = os.getenv('TWILIO_FROM_NUMBER', '').strip()
    
    # Database configuration - Use SHARED pharmacy database or DATABASE_URL
    database_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        db_path = os.path.join(os.path.dirname(basedir), 'database', 'pharmacy.db')
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Upload configuration (point to project-level static uploads)
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(basedir), 'static', 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
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
    
    # Register blueprints - handle different systems gracefully
    try:
        from app.routes import auth_bp, medicine_bp, cart_bp, order_bp, recommendation_bp, admin_bp, main_bp_final_unique
        app.register_blueprint(auth_bp)
        app.register_blueprint(medicine_bp)
        app.register_blueprint(cart_bp)
        app.register_blueprint(order_bp)
        app.register_blueprint(recommendation_bp)
        app.register_blueprint(admin_bp)
        app.register_blueprint(main_bp_final_unique)
    except ImportError as e:
        # For systems with different blueprint names (e.g., admin_system)
        try:
            from app.routes import auth_bp, dashboard_bp, api_bp
            app.register_blueprint(auth_bp)
            app.register_blueprint(dashboard_bp)
            app.register_blueprint(api_bp)
        except ImportError:
            pass
    
    # Register unified order system
    try:
        from app.unified_orders import unified_bp
        app.register_blueprint(unified_bp)
    except ImportError:
        pass
    
    # User loader
    from app.models import User
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Session management - keep user logged in
    @app.before_request
    def before_request():
        from flask import session
        from datetime import timedelta
        
        session.permanent = True
        app.permanent_session_lifetime = timedelta(days=7)
        session.modified = True
    
    # Create tables
    with app.app_context():
        db.create_all()
        try:
            from app.models import User, DeliveryAgent

            demo_user = User.query.filter_by(username='delivery1').first()
            if not demo_user:
                demo_user = User(
                    username='delivery1',
                    email='delivery1@delivery.com',
                    full_name='Delivery Agent One',
                    phone='9000000001',
                    city='Delhi',
                    role='delivery'
                )
                demo_user.set_password('delivery123')
                db.session.add(demo_user)
                db.session.flush()

                demo_agent = DeliveryAgent(
                    user_id=demo_user.id,
                    city='Delhi',
                    vehicle_number='DL-01-1234',
                    active=True
                )
                db.session.add(demo_agent)
                db.session.commit()
        except Exception:
            db.session.rollback()
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
            # Ensure users table has age/gender/role columns
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
                if 'is_active' not in user_cols:
                    try:
                        cur.execute("ALTER TABLE users ADD COLUMN is_active BOOLEAN DEFAULT TRUE")
                    except sqlite3.OperationalError:
                        pass
                try:
                    cur.execute("PRAGMA table_info(orders)")
                    order_cols = [r[1] for r in cur.fetchall()]
                    if 'assigned_date' not in order_cols:
                        try:
                            cur.execute("ALTER TABLE orders ADD COLUMN assigned_date TIMESTAMP")
                        except sqlite3.OperationalError:
                            pass
                except Exception:
                    pass

                conn.commit()

                # Sync legacy customers from pharmacy_system database if present
                try:
                    project_root = os.path.abspath(os.path.join(os.path.dirname(basedir), '..'))
                    legacy_db = os.path.join(project_root, 'pharmacy_system', 'database', 'pharmacy.db')
                    if os.path.exists(legacy_db) and os.path.abspath(legacy_db) != os.path.abspath(db_path):
                        legacy_conn = sqlite3.connect(legacy_db)
                        legacy_cur = legacy_conn.cursor()
                        legacy_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
                        if legacy_cur.fetchone():
                            legacy_cur.execute("PRAGMA table_info(users)")
                            legacy_cols = [row[1] for row in legacy_cur.fetchall()]
                            if legacy_cols:
                                legacy_cur.execute("SELECT user_id FROM shopkeepers")
                                legacy_shopkeepers = {row[0] for row in legacy_cur.fetchall()}
                                legacy_delivery = set()
                                legacy_cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='delivery_agents'")
                                if legacy_cur.fetchone():
                                    legacy_cur.execute("SELECT user_id FROM delivery_agents")
                                    legacy_delivery = {row[0] for row in legacy_cur.fetchall()}

                                legacy_cur.execute("SELECT {} FROM users".format(', '.join(legacy_cols)))
                                legacy_rows = legacy_cur.fetchall()

                                cur.execute("PRAGMA table_info(users)")
                                admin_cols = [row[1] for row in cur.fetchall()]
                                admin_cols_set = set(admin_cols)
                                insert_cols = [col for col in legacy_cols if col in admin_cols_set and col != 'id']

                                if {'username', 'email', 'password_hash'}.issubset(admin_cols_set):
                                    for row in legacy_rows:
                                        data = dict(zip(legacy_cols, row))
                                        user_id_val = data.get('id')
                                        if user_id_val in legacy_shopkeepers or user_id_val in legacy_delivery:
                                            continue

                                        role_val = (data.get('role') or 'customer').lower()
                                        is_admin_val = data.get('is_admin') or 0
                                        if is_admin_val or role_val in ('admin', 'shopkeeper', 'delivery'):
                                            continue

                                        username = data.get('username')
                                        email = data.get('email')
                                        if not username or not email:
                                            continue

                                        cur.execute("SELECT 1 FROM users WHERE username = ? OR email = ?", (username, email))
                                        if cur.fetchone():
                                            continue

                                        if 'role' in insert_cols:
                                            data['role'] = 'customer'
                                        if 'is_active' in insert_cols and data.get('is_active') is None:
                                            data['is_active'] = 1

                                        values = [data.get(col) for col in insert_cols]
                                        placeholders = ', '.join(['?'] * len(insert_cols))
                                        cur.execute(
                                            "INSERT INTO users ({}) VALUES ({})".format(', '.join(insert_cols), placeholders),
                                            values
                                        )
                                    conn.commit()
                        legacy_conn.close()
                except Exception:
                    pass
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

            # Ensure medicines table has shopkeeper_id column
            try:
                cur.execute("PRAGMA table_info(medicines)")
                med_cols = [r[1] for r in cur.fetchall()]
                if 'shopkeeper_id' not in med_cols:
                    try:
                        cur.execute("ALTER TABLE medicines ADD COLUMN shopkeeper_id INTEGER")
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
