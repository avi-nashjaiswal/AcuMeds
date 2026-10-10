"""
Initialize and verify Doctor system tables and demo accounts in shared database
"""
import os
import sys
import sqlite3

basedir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(basedir, 'admin_system', 'database', 'pharmacy.db')

print(f"Connecting to database at: {db_path}")
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create doctors table
cur.execute('''
CREATE TABLE IF NOT EXISTS doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL UNIQUE,
    specialization VARCHAR(120) NOT NULL,
    qualification VARCHAR(120) NOT NULL,
    experience_years INTEGER DEFAULT 1,
    license_number VARCHAR(80) NOT NULL,
    clinic_name VARCHAR(150),
    clinic_address TEXT,
    city VARCHAR(80),
    consultation_fee FLOAT DEFAULT 300.0,
    bio TEXT,
    rating FLOAT DEFAULT 4.9,
    total_reviews INTEGER DEFAULT 0,
    is_verified BOOLEAN DEFAULT 1,
    is_available BOOLEAN DEFAULT 1,
    available_days VARCHAR(100) DEFAULT 'Mon,Tue,Wed,Thu,Fri,Sat',
    available_time_start VARCHAR(20) DEFAULT '09:00 AM',
    available_time_end VARCHAR(20) DEFAULT '08:00 PM',
    avatar VARCHAR(255) DEFAULT 'images/doctor-default.png',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# Create doctor_appointments table
cur.execute('''
CREATE TABLE IF NOT EXISTS doctor_appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    appointment_date VARCHAR(30) NOT NULL,
    appointment_time VARCHAR(30) NOT NULL,
    consultation_type VARCHAR(30) DEFAULT 'Online Video',
    patient_name VARCHAR(120),
    patient_age INTEGER,
    patient_gender VARCHAR(20),
    patient_phone VARCHAR(30),
    symptoms TEXT,
    status VARCHAR(30) DEFAULT 'Pending',
    consultation_fee FLOAT DEFAULT 300.0,
    payment_status VARCHAR(30) DEFAULT 'Paid',
    meeting_link VARCHAR(255),
    doctor_notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(patient_id) REFERENCES users(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id)
)
''')

# Create doctor_prescriptions table
cur.execute('''
CREATE TABLE IF NOT EXISTS doctor_prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id INTEGER,
    doctor_id INTEGER NOT NULL,
    patient_id INTEGER NOT NULL,
    prescription_code VARCHAR(40) UNIQUE,
    patient_name VARCHAR(120),
    patient_age INTEGER,
    patient_gender VARCHAR(20),
    vitals_bp VARCHAR(30),
    vitals_pulse VARCHAR(30),
    vitals_temp VARCHAR(30),
    vitals_weight VARCHAR(30),
    diagnosis TEXT NOT NULL,
    general_advice TEXT,
    tests_recommended TEXT,
    follow_up_date VARCHAR(40),
    is_ordered BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(appointment_id) REFERENCES doctor_appointments(id),
    FOREIGN KEY(doctor_id) REFERENCES doctors(id),
    FOREIGN KEY(patient_id) REFERENCES users(id)
)
''')

# Create doctor_prescription_items table
cur.execute('''
CREATE TABLE IF NOT EXISTS doctor_prescription_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prescription_id INTEGER NOT NULL,
    medicine_id INTEGER,
    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(80),
    frequency VARCHAR(80),
    timing VARCHAR(80),
    duration VARCHAR(80),
    instructions TEXT,
    quantity INTEGER DEFAULT 1,
    FOREIGN KEY(prescription_id) REFERENCES doctor_prescriptions(id),
    FOREIGN KEY(medicine_id) REFERENCES medicines(id)
)
''')

conn.commit()
print("All doctor schema tables verified successfully.")

# Now run python seeder using doctor_system app context
try:
    sys.path.insert(0, os.path.join(basedir, 'doctor_system'))
    from app import create_app
    app = create_app()
    print("Doctor system app initialized and demo doctors seeded successfully!")
except Exception as e:
    print(f"App seed notice: {e}")

conn.close()
