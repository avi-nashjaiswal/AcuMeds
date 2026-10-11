"""
Flask application initialization for Doctor system
"""
import ast
for _ast_attr in ('Str', 'Num', 'Bytes', 'NameConstant', 'Ellipsis'):
    if not hasattr(ast, _ast_attr):
        setattr(ast, _ast_attr, getattr(ast, 'Constant', object))

import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()


def _load_env_file(file_path):
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
                if ((value.startswith('"') and value.endswith('"')) or
                        (value.startswith("'") and value.endswith("'"))):
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

    app = Flask(
        __name__,
        template_folder=os.path.join(basedir, '..', 'templates'),
        static_folder=os.path.join(basedir, '..', 'static'),
        static_url_path='/static'
    )
    
    try:
        from doctor_system import config as app_config
        app.config.from_object(app_config)
    except ImportError:
        try:
            import config as app_config
            app.config.from_object(app_config)
        except Exception:
            pass

    database_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI')
    if database_url:
        if database_url.startswith('postgres://'):
            database_url = database_url.replace('postgres://', 'postgresql://', 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    elif not app.config.get('SQLALCHEMY_DATABASE_URI'):
        _db_path = os.path.abspath(os.path.join(basedir, os.pardir, os.pardir, 'admin_system', 'database', 'pharmacy.db'))
        os.makedirs(os.path.dirname(_db_path), exist_ok=True)
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{_db_path}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY') or 'acumeds-doctor-prod-secret-key-2026'
    app.config['SESSION_COOKIE_NAME'] = 'acumeds_doctor_session'
    app.config['OPENAI_API_KEY'] = os.getenv('OPENAI_API_KEY', '').strip()
    app.config['OPENAI_MODEL'] = os.getenv('OPENAI_MODEL', 'gpt-4o-mini').strip() or 'gpt-4o-mini'

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
    login_manager.login_message_category = 'info'

    # User loader
    try:
        from .models import User
    except ImportError:
        from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        try:
            return User.query.get(int(user_id))
        except Exception:
            return None

    # Register blueprints
    try:
        from .routes import auth_bp, doctor_bp, main_bp
    except ImportError:
        from app.routes import auth_bp, doctor_bp, main_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(doctor_bp)

    @app.route('/health')
    def health_check():
        """Health check endpoint for Render monitoring."""
        from flask import jsonify
        import time
        return jsonify({"status": "ok", "service": "doctor_telehealth", "timestamp": int(time.time())}), 200

    @app.after_request
    def add_cors_headers(response):
        """Enable CORS for cross-domain communication between separate portals."""
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,POST,PUT,DELETE,OPTIONS'
        return response

    # Context processors
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'AcuMeds Doctor Portal',
            'currency_symbol': '₹'
        }

    # Ensure tables and demo data exist
    with app.app_context():
        db.create_all()
        _seed_demo_doctors(db)

    return app


def _seed_demo_doctors(db_instance):
    """Seed demo doctor accounts and sample appointments if none exist"""
    try:
        try:
            from .models import User, Doctor, Medicine, DoctorAppointment, DoctorPrescription, DoctorPrescriptionItem
        except ImportError:
            from app.models import User, Doctor, Medicine, DoctorAppointment, DoctorPrescription, DoctorPrescriptionItem

        # Demo Doctor 1: Dr. Rajesh Sharma
        doc1_user = User.query.filter_by(username='doctor1').first()
        if not doc1_user:
            doc1_user = User(
                username='doctor1',
                email='dr.rajesh@acumeds.com',
                full_name='Dr. Rajesh Sharma, MD',
                phone='+91 98765 43210',
                address='Apollo Health City, Jubilee Hills',
                city='Delhi',
                role='doctor',
                age=45,
                gender='Male'
            )
            doc1_user.set_password('doctor123')
            db_instance.session.add(doc1_user)
            db_instance.session.flush()

            doc1 = Doctor(
                user_id=doc1_user.id,
                specialization='Cardiology & Internal Medicine',
                qualification='MBBS, MD (Medicine), DM (Cardiology)',
                experience_years=16,
                license_number='MCI-DL-2008-88421',
                clinic_name='Sharma Heart & Multispeciality Clinic',
                clinic_address='Suite 402, Metro Healthcare Complex, Connaught Place, New Delhi',
                city='Delhi',
                consultation_fee=400.0,
                bio='Senior Consultant Cardiologist with 16+ years of clinical excellence in hypertension, cardiac care, diabetic heart health, and preventive medicine.',
                rating=4.9,
                total_reviews=128,
                is_verified=True,
                is_available=True,
                available_days='Mon,Tue,Wed,Thu,Fri,Sat',
                available_time_start='09:00 AM',
                available_time_end='07:00 PM'
            )
            db_instance.session.add(doc1)
            db_instance.session.flush()

        # Demo Doctor 2: Dr. Priya Patel
        doc2_user = User.query.filter_by(username='doctor2').first()
        if not doc2_user:
            doc2_user = User(
                username='doctor2',
                email='dr.priya@acumeds.com',
                full_name='Dr. Priya Patel, MBBS, DCH',
                phone='+91 98111 22334',
                address='Max Super Care, Saket',
                city='Delhi',
                role='doctor',
                age=38,
                gender='Female'
            )
            doc2_user.set_password('doctor123')
            db_instance.session.add(doc2_user)
            db_instance.session.flush()

            doc2 = Doctor(
                user_id=doc2_user.id,
                specialization='Pediatrics & Child Care',
                qualification='MBBS, DCH, DNB (Pediatrics)',
                experience_years=11,
                license_number='MCI-DL-2013-55219',
                clinic_name='Little Smiles Pediatric Center',
                clinic_address='Block B, Green Park Extension, New Delhi',
                city='Delhi',
                consultation_fee=350.0,
                bio='Dedicated pediatrician specializing in newborn care, child immunization, pediatric allergy management, and adolescent healthcare.',
                rating=4.95,
                total_reviews=94,
                is_verified=True,
                is_available=True,
                available_days='Mon,Tue,Wed,Thu,Fri',
                available_time_start='10:00 AM',
                available_time_end='06:00 PM'
            )
            db_instance.session.add(doc2)
            db_instance.session.flush()

        # Demo Doctor 3: Dr. Amit Verma (Dermatologist)
        doc3_user = User.query.filter_by(username='doctor3').first()
        if not doc3_user:
            doc3_user = User(
                username='doctor3',
                email='dr.amit@acumeds.com',
                full_name='Dr. Amit Verma, MD',
                phone='+91 97222 33445',
                address='Skin & Aesthetic Clinic',
                city='Delhi',
                role='doctor',
                age=41,
                gender='Male'
            )
            doc3_user.set_password('doctor123')
            db_instance.session.add(doc3_user)
            db_instance.session.flush()

            doc3 = Doctor(
                user_id=doc3_user.id,
                specialization='Dermatology & Cosmetology',
                qualification='MBBS, MD (Dermatology, Venereology & Leprosy)',
                experience_years=14,
                license_number='MCI-DL-2010-33104',
                clinic_name='DermaPlus Aesthetic & Hair Clinic',
                clinic_address='12 Hauz Khas Enclave, New Delhi',
                city='Delhi',
                consultation_fee=500.0,
                bio='Expert dermatologist with specialized training in clinical dermatology, acne treatments, eczema, psoriasis, and aesthetic skin rejuvenation.',
                rating=4.88,
                total_reviews=76,
                is_verified=True,
                is_available=True,
                available_days='Tue,Wed,Thu,Fri,Sat,Sun',
                available_time_start='11:00 AM',
                available_time_end='08:00 PM'
            )
            db_instance.session.add(doc3)
            db_instance.session.flush()

        # Check if there is a customer user to link sample appointment
        customer_user = User.query.filter_by(role='customer').first()
        if customer_user and doc1_user:
            doc1 = Doctor.query.filter_by(user_id=doc1_user.id).first()
            if doc1:
                sample_appt = DoctorAppointment.query.filter_by(doctor_id=doc1.id, patient_id=customer_user.id).first()
                if not sample_appt:
                    sample_appt = DoctorAppointment(
                        patient_id=customer_user.id,
                        doctor_id=doc1.id,
                        appointment_date='Today',
                        appointment_time='04:30 PM',
                        consultation_type='Online Video',
                        patient_name=customer_user.full_name or customer_user.username,
                        patient_age=customer_user.age or 32,
                        patient_gender=customer_user.gender or 'Male',
                        patient_phone=customer_user.phone or '+91 9988776655',
                        symptoms='Mild chest discomfort after exertion, occasional breathlessness, blood pressure 135/88 mmHg.',
                        status='Confirmed',
                        consultation_fee=doc1.consultation_fee,
                        payment_status='Paid',
                        meeting_link='https://meet.jit.si/acumeds-consult-demo-room'
                    )
                    db_instance.session.add(sample_appt)

        db_instance.session.commit()
    except Exception as e:
        db_instance.session.rollback()
        print(f"[Seed] Note on seeding doctors: {e}")
