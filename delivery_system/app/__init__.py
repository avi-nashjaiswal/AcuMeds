"""
Flask application initialization for Delivery system
"""
from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
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
    project_static = os.path.join(os.path.dirname(basedir), 'static')
    app = Flask(
        __name__,
        template_folder=os.path.join(basedir, '..', 'templates'),
        static_folder=project_static,
        static_url_path='/static'
    )
    app.config['SECRET_KEY'] = 'delivery-secret-key-change-in-production-xyz789'
    app.config['SESSION_COOKIE_NAME'] = 'acumeds_delivery_session'
    app.config['DEFAULT_LANGUAGE'] = DEFAULT_LANGUAGE

    db_path = os.path.join(project_root, 'admin_system', 'database', 'pharmacy.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '').strip()
    app.config['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'

    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(basedir), 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @app.before_request
    def _load_language_context():
        g.current_language = get_current_language()

    # User loader
    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

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

    # Register blueprints
    from app.routes import auth_bp, delivery_bp, main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(delivery_bp)

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
        try:
            import sqlite3

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()
            cur.execute("PRAGMA table_info(users)")
            user_cols = [row[1] for row in cur.fetchall()]
            if 'age' not in user_cols:
                try:
                    cur.execute("ALTER TABLE users ADD COLUMN age INTEGER")
                except sqlite3.OperationalError:
                    pass
            if 'gender' not in user_cols:
                try:
                    cur.execute("ALTER TABLE users ADD COLUMN gender VARCHAR(20)")
                except sqlite3.OperationalError:
                    pass
            conn.commit()
            conn.close()
        except Exception:
            pass

    return app
