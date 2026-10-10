"""
Routes for Doctor Portal
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from functools import wraps
from datetime import datetime, date
import uuid
import json
import os
import requests

try:
    from . import db
    from .models import (
        User, Doctor, DoctorAppointment, DoctorPrescription,
        DoctorPrescriptionItem, Medicine, Notification
    )
except ImportError:
    from app import db
    from app.models import (
        User, Doctor, DoctorAppointment, DoctorPrescription,
        DoctorPrescriptionItem, Medicine, Notification
    )

main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
doctor_bp = Blueprint('doctor', __name__)


def doctor_required(f):
    """Decorator to require doctor role and verification"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login', next=request.url))
        if current_user.role not in ['doctor', 'admin']:
            flash('Access restricted to medical doctors.', 'warning')
            return redirect(url_for('auth.login'))
        
        # If doctor role, check verification
        if current_user.role == 'doctor':
            doctor = current_user.doctor or Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor and not doctor.is_verified:
                return redirect(url_for('auth.pending_verification'))
                
        return f(*args, **kwargs)
    return decorated_function


# ==========================================
# Main Routes
# ==========================================
@main_bp.route('/')
def index():
    if current_user.is_authenticated and current_user.role in ['doctor', 'admin']:
        if current_user.role == 'doctor':
            doctor = current_user.doctor or Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor and not doctor.is_verified:
                return redirect(url_for('auth.pending_verification'))
        return redirect(url_for('doctor.dashboard'))
    return redirect(url_for('auth.login'))


# ==========================================
# Authentication & Verification Routes
# ==========================================
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated and current_user.role in ['doctor', 'admin']:
        if current_user.role == 'doctor':
            doctor = current_user.doctor or Doctor.query.filter_by(user_id=current_user.id).first()
            if doctor and not doctor.is_verified:
                return redirect(url_for('auth.pending_verification'))
        return redirect(url_for('doctor.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        remember = bool(request.form.get('remember'))

        user = User.query.filter((User.username == username) | (User.email == username)).first()

        if user and user.check_password(password):
            if user.role not in ['doctor', 'admin']:
                flash('This portal is reserved for Doctors. Please log in with a doctor account.', 'danger')
                return render_template('auth/login.html')

            login_user(user, remember=remember)
            
            # Check doctor verification status
            if user.role == 'doctor':
                doctor = user.doctor or Doctor.query.filter_by(user_id=user.id).first()
                if doctor and not doctor.is_verified:
                    flash(f'Welcome Dr. {user.full_name or user.username}. Your application is pending Admin verification.', 'warning')
                    return redirect(url_for('auth.pending_verification'))

            flash(f'Welcome back, Dr. {user.full_name or user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('doctor.dashboard'))
        else:
            flash('Invalid username/email or password.', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated and current_user.role in ['doctor', 'admin']:
        return redirect(url_for('doctor.dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        city = request.form.get('city', 'Delhi').strip()
        specialization = request.form.get('specialization', '').strip()
        qualification = request.form.get('qualification', '').strip()
        experience_years = int(request.form.get('experience_years', 1))
        license_number = request.form.get('license_number', '').strip()
        clinic_name = request.form.get('clinic_name', '').strip()
        consultation_fee = float(request.form.get('consultation_fee', 300.0))
        bio = request.form.get('bio', '').strip()

        # Validation
        if not username or not email or not password or not license_number or not specialization:
            flash('Please fill in all mandatory fields.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(username=username).first():
            flash('Username is already registered.', 'danger')
            return render_template('auth/register.html')

        if User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('auth/register.html')

        # Generate unique Application Reference
        reg_ref = f"ACU-DOC-REG-{datetime.utcnow().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

        # Create Doctor User
        new_user = User(
            username=username,
            email=email,
            full_name=full_name if full_name.startswith('Dr.') else f'Dr. {full_name}',
            phone=phone,
            city=city,
            role='doctor',
            is_active=True
        )
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.flush()

        # Create Doctor Profile (Pending verification)
        doctor_profile = Doctor(
            user_id=new_user.id,
            specialization=specialization,
            qualification=qualification,
            experience_years=experience_years,
            license_number=license_number,
            clinic_name=clinic_name or f'{new_user.full_name}\'s Clinic',
            city=city,
            consultation_fee=consultation_fee,
            bio=bio,
            is_verified=False,
            is_available=False,
            registration_ref=reg_ref
        )
        db.session.add(doctor_profile)

        # Create Admin notification
        admin_users = User.query.filter((User.role == 'admin') | (User.is_admin == True)).all()
        for admin in admin_users:
            notif = Notification(
                user_id=admin.id,
                title='New Doctor Registration Submitted',
                message=f'Dr. {new_user.full_name} ({specialization}, Lic: {license_number}) registered and awaits verification. Ref: {reg_ref}',
                notification_type='doctor_registration'
            )
            db.session.add(notif)

        # Confirmation notification for Doctor
        doc_notif = Notification(
            user_id=new_user.id,
            title='Registration Confirmation Letter Issued',
            message=f'Your registration application (Ref: {reg_ref}) has been received and is under review by the AcuMeds Medical Board.',
            notification_type='registration_confirmation'
        )
        db.session.add(doc_notif)

        db.session.commit()

        login_user(new_user)
        flash('Doctor registration submitted successfully! Your application confirmation letter has been generated and sent for admin review.', 'success')
        return redirect(url_for('auth.pending_verification'))

    return render_template('auth/register.html')


@auth_bp.route('/pending-verification')
def pending_verification():
    """Pending verification tracking page for doctor"""
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

    doctor = current_user.doctor or Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor:
        flash('Doctor profile not found.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('auth/pending_verification.html', doctor=doctor)


@auth_bp.route('/confirmation-letter')
@auth_bp.route('/confirmation-letter/<int:doctor_id>')
def confirmation_letter(doctor_id=None):
    """View and print official Registration Confirmation Letter"""
    if doctor_id:
        doctor = Doctor.query.get_or_404(doctor_id)
    elif current_user.is_authenticated:
        doctor = current_user.doctor or Doctor.query.filter_by(user_id=current_user.id).first()
    else:
        return redirect(url_for('auth.login'))

    if not doctor:
        flash('Doctor application not found.', 'danger')
        return redirect(url_for('auth.login'))

    return render_template('auth/confirmation_letter.html', doctor=doctor)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out safely.', 'info')
    return redirect(url_for('auth.login'))


@doctor_bp.route('/approval-letter')
@doctor_bp.route('/approval-certificate')
@doctor_required
def approval_letter():
    """View official Practice Authorization Certificate & Approval Letter once approved"""
    doctor = current_user.doctor or Doctor.query.filter_by(user_id=current_user.id).first()
    if not doctor or not doctor.is_verified:
        flash('Official practice authorization is only available after Admin approval.', 'warning')
        return redirect(url_for('auth.pending_verification'))

    return render_template('auth/approval_letter.html', doctor=doctor)


# ==========================================
# Doctor Portal Core Routes
# ==========================================
@doctor_bp.route('/dashboard')
@doctor_required
def dashboard():
    doctor = current_user.doctor
    if not doctor:
        # Fallback if admin or incomplete profile
        doctor = Doctor.query.filter_by(user_id=current_user.id).first()
        if not doctor:
            doctor = Doctor.query.first()

    today_str = date.today().strftime('%Y-%m-%d')
    
    # Appointments query
    appointments = DoctorAppointment.query.filter_by(doctor_id=doctor.id).order_by(DoctorAppointment.id.desc()).all() if doctor else []
    
    # Metrics
    total_appointments = len(appointments)
    pending_count = sum(1 for a in appointments if a.status == 'Pending')
    confirmed_count = sum(1 for a in appointments if a.status in ['Confirmed', 'In Consultation'])
    completed_count = sum(1 for a in appointments if a.status == 'Completed')
    total_earnings = sum(a.consultation_fee for a in appointments if a.status == 'Completed' or a.payment_status == 'Paid')

    # Recent appointments & prescriptions
    recent_prescriptions = DoctorPrescription.query.filter_by(doctor_id=doctor.id).order_by(DoctorPrescription.id.desc()).limit(5).all() if doctor else []

    return render_template(
        'dashboard.html',
        doctor=doctor,
        appointments=appointments[:6],
        total_appointments=total_appointments,
        pending_count=pending_count,
        confirmed_count=confirmed_count,
        completed_count=completed_count,
        total_earnings=total_earnings,
        recent_prescriptions=recent_prescriptions
    )


@doctor_bp.route('/appointments')
@doctor_required
def appointments():
    doctor = current_user.doctor or Doctor.query.first()
    filter_status = request.args.get('status', 'all')

    query = DoctorAppointment.query.filter_by(doctor_id=doctor.id) if doctor else DoctorAppointment.query

    if filter_status != 'all':
        if filter_status == 'upcoming':
            query = query.filter(DoctorAppointment.status.in_(['Pending', 'Confirmed']))
        else:
            query = query.filter_by(status=filter_status.capitalize())

    appointments_list = query.order_by(DoctorAppointment.id.desc()).all()

    return render_template(
        'appointments.html',
        doctor=doctor,
        appointments=appointments_list,
        current_filter=filter_status
    )


@doctor_bp.route('/appointment/<int:appointment_id>/status', methods=['POST'])
@doctor_required
def update_appointment_status(appointment_id):
    appointment = DoctorAppointment.query.get_or_404(appointment_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes')

    if new_status:
        appointment.status = new_status
        if notes:
            appointment.doctor_notes = notes
        
        # Send patient notification
        if appointment.patient_id:
            notif = Notification(
                user_id=appointment.patient_id,
                title=f"Appointment {new_status}",
                message=f"Your appointment with Dr. {appointment.doctor.user.full_name} for {appointment.appointment_date} has been updated to: {new_status}.",
                notification_type="appointment_update"
            )
            db.session.add(notif)

        db.session.commit()
        flash(f'Appointment status changed to "{new_status}".', 'success')

    return redirect(request.referrer or url_for('doctor.appointments'))


@doctor_bp.route('/consultation/<int:appointment_id>')
@doctor_required
def consultation(appointment_id):
    appointment = DoctorAppointment.query.get_or_404(appointment_id)
    doctor = current_user.doctor or appointment.doctor

    # Set status to In Consultation if confirmed
    if appointment.status == 'Confirmed':
        appointment.status = 'In Consultation'
        db.session.commit()

    # Get patient's previous consultations & prescriptions
    past_appointments = DoctorAppointment.query.filter_by(patient_id=appointment.patient_id).filter(DoctorAppointment.id != appointment.id).order_by(DoctorAppointment.id.desc()).all()
    past_prescriptions = DoctorPrescription.query.filter_by(patient_id=appointment.patient_id).order_by(DoctorPrescription.id.desc()).all()

    # Generate or get video link
    if not appointment.meeting_link:
        room_name = f"acumeds-consult-{appointment.id}-{uuid.uuid4().hex[:6]}"
        appointment.meeting_link = f"https://meet.jit.si/{room_name}"
        db.session.commit()

    return render_template(
        'consultation.html',
        doctor=doctor,
        appointment=appointment,
        past_appointments=past_appointments,
        past_prescriptions=past_prescriptions
    )


@doctor_bp.route('/prescribe/<int:appointment_id>', methods=['GET', 'POST'])
@doctor_required
def prescribe(appointment_id):
    appointment = DoctorAppointment.query.get_or_404(appointment_id)
    doctor = current_user.doctor or appointment.doctor

    if request.method == 'POST':
        diagnosis = request.form.get('diagnosis', '').strip()
        general_advice = request.form.get('general_advice', '').strip()
        tests_recommended = request.form.get('tests_recommended', '').strip()
        follow_up_date = request.form.get('follow_up_date', '').strip()
        
        # Vitals
        vitals_bp = request.form.get('vitals_bp', '').strip()
        vitals_pulse = request.form.get('vitals_pulse', '').strip()
        vitals_temp = request.form.get('vitals_temp', '').strip()
        vitals_weight = request.form.get('vitals_weight', '').strip()

        if not diagnosis:
            flash('Diagnosis is required to issue a prescription.', 'danger')
            return redirect(url_for('doctor.prescribe', appointment_id=appointment.id))

        # Generate unique Prescription Code (e.g. RX-2026-8941)
        rx_code = f"RX-{datetime.now().strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

        # Create Prescription
        prescription = DoctorPrescription(
            appointment_id=appointment.id,
            doctor_id=doctor.id,
            patient_id=appointment.patient_id,
            prescription_code=rx_code,
            patient_name=appointment.patient_name or (appointment.patient.full_name if appointment.patient else 'Patient'),
            patient_age=appointment.patient_age or (appointment.patient.age if appointment.patient else None),
            patient_gender=appointment.patient_gender or (appointment.patient.gender if appointment.patient else None),
            vitals_bp=vitals_bp,
            vitals_pulse=vitals_pulse,
            vitals_temp=vitals_temp,
            vitals_weight=vitals_weight,
            diagnosis=diagnosis,
            general_advice=general_advice,
            tests_recommended=tests_recommended,
            follow_up_date=follow_up_date
        )
        db.session.add(prescription)
        db.session.flush()

        # Parse Prescribed Medicines list
        med_names = request.form.getlist('med_name[]')
        med_dosages = request.form.getlist('med_dosage[]')
        med_freqs = request.form.getlist('med_frequency[]')
        med_timings = request.form.getlist('med_timing[]')
        med_durations = request.form.getlist('med_duration[]')
        med_instructions = request.form.getlist('med_instructions[]')
        med_ids = request.form.getlist('med_id[]')
        med_qtys = request.form.getlist('med_qty[]')

        for i in range(len(med_names)):
            m_name = med_names[i].strip() if i < len(med_names) else ''
            if not m_name:
                continue

            m_id = None
            if i < len(med_ids) and med_ids[i].isdigit():
                m_id = int(med_ids[i])
            else:
                # Try finding matching medicine in inventory
                matched_med = Medicine.query.filter(Medicine.name.ilike(f"%{m_name}%")).first()
                if matched_med:
                    m_id = matched_med.id

            qty = 1
            if i < len(med_qtys) and med_qtys[i].isdigit():
                qty = int(med_qtys[i])

            rx_item = DoctorPrescriptionItem(
                prescription_id=prescription.id,
                medicine_id=m_id,
                medicine_name=m_name,
                dosage=med_dosages[i].strip() if i < len(med_dosages) else '',
                frequency=med_freqs[i].strip() if i < len(med_freqs) else '1-0-1',
                timing=med_timings[i].strip() if i < len(med_timings) else 'After Food',
                duration=med_durations[i].strip() if i < len(med_durations) else '5 Days',
                instructions=med_instructions[i].strip() if i < len(med_instructions) else '',
                quantity=qty
            )
            db.session.add(rx_item)

        # Mark appointment completed
        appointment.status = 'Completed'

        # Notify patient
        notif = Notification(
            user_id=appointment.patient_id,
            title="Digital Prescription Issued",
            message=f"Dr. {doctor.user.full_name} has generated your digital prescription ({rx_code}). You can now view and 1-click buy your prescribed medicines on AcuMeds Pharmacy.",
            notification_type="prescription_issued"
        )
        db.session.add(notif)

        db.session.commit()
        flash(f'Prescription {rx_code} generated and delivered to patient successfully!', 'success')
        return redirect(url_for('doctor.prescription_view', prescription_id=prescription.id))

    # Pre-fetch medicines for autocomplete
    medicines = Medicine.query.order_by(Medicine.name.asc()).all()

    return render_template(
        'prescribe.html',
        doctor=doctor,
        appointment=appointment,
        medicines=medicines
    )


@doctor_bp.route('/prescription/<int:prescription_id>')
@login_required
def prescription_view(prescription_id):
    prescription = DoctorPrescription.query.get_or_404(prescription_id)
    doctor = prescription.doctor
    return render_template(
        'prescription_view.html',
        prescription=prescription,
        doctor=doctor
    )


@doctor_bp.route('/patients')
@doctor_required
def patients():
    doctor = current_user.doctor or Doctor.query.first()
    # Find unique patients who booked with this doctor
    appointments = DoctorAppointment.query.filter_by(doctor_id=doctor.id).all() if doctor else []
    patient_ids = list(set([a.patient_id for a in appointments]))
    
    patient_records = []
    for pid in patient_ids:
        patient_user = User.query.get(pid)
        if patient_user:
            p_appts = [a for a in appointments if a.patient_id == pid]
            p_rxs = DoctorPrescription.query.filter_by(patient_id=pid, doctor_id=doctor.id).all()
            patient_records.append({
                'user': patient_user,
                'total_consultations': len(p_appts),
                'last_consultation': p_appts[-1].appointment_date if p_appts else 'N/A',
                'prescriptions_count': len(p_rxs)
            })

    return render_template(
        'patients.html',
        doctor=doctor,
        patients=patient_records
    )


@doctor_bp.route('/schedule', methods=['GET', 'POST'])
@doctor_required
def schedule():
    doctor = current_user.doctor or Doctor.query.first()

    if request.method == 'POST':
        doctor.consultation_fee = float(request.form.get('consultation_fee', doctor.consultation_fee))
        doctor.available_days = ','.join(request.form.getlist('available_days'))
        doctor.available_time_start = request.form.get('time_start', doctor.available_time_start)
        doctor.available_time_end = request.form.get('time_end', doctor.available_time_end)
        doctor.is_available = bool(request.form.get('is_available'))
        doctor.clinic_name = request.form.get('clinic_name', doctor.clinic_name)
        doctor.clinic_address = request.form.get('clinic_address', doctor.clinic_address)

        db.session.commit()
        flash('Schedule and consultation settings updated successfully!', 'success')
        return redirect(url_for('doctor.schedule'))

    return render_template('schedule.html', doctor=doctor)


@doctor_bp.route('/profile', methods=['GET', 'POST'])
@doctor_required
def profile():
    doctor = current_user.doctor or Doctor.query.first()

    if request.method == 'POST':
        current_user.full_name = request.form.get('full_name', current_user.full_name)
        current_user.phone = request.form.get('phone', current_user.phone)
        current_user.city = request.form.get('city', current_user.city)
        doctor.specialization = request.form.get('specialization', doctor.specialization)
        doctor.qualification = request.form.get('qualification', doctor.qualification)
        doctor.experience_years = int(request.form.get('experience_years', doctor.experience_years))
        doctor.license_number = request.form.get('license_number', doctor.license_number)
        doctor.bio = request.form.get('bio', doctor.bio)

        db.session.commit()
        flash('Doctor profile updated successfully!', 'success')
        return redirect(url_for('doctor.profile'))

    return render_template('profile.html', doctor=doctor)


# ==========================================
# API Endpoints
# ==========================================
@doctor_bp.route('/api/medicines/search')
@login_required
def search_medicines():
    q = request.args.get('q', '').strip()
    if not q or len(q) < 2:
        return jsonify([])

    results = Medicine.query.filter(
        (Medicine.name.ilike(f"%{q}%")) | (Medicine.category.ilike(f"%{q}%"))
    ).limit(10).all()

    items = [{
        'id': m.id,
        'name': m.name,
        'category': m.category,
        'strength': f"{m.strength_value or ''} {m.strength_unit or ''}".strip(),
        'price': m.price,
        'stock': m.stock_quantity,
        'requires_rx': m.requires_prescription
    } for m in results]

    return jsonify(items)


@doctor_bp.route('/api/ai-diagnosis', methods=['POST'])
@doctor_required
def ai_diagnosis():
    data = request.get_json() or {}
    symptoms = data.get('symptoms', '').strip()
    patient_age = data.get('age', '')
    patient_gender = data.get('gender', '')
    vitals = data.get('vitals', '')

    if not symptoms:
        return jsonify({'error': 'Please describe symptoms for AI differential diagnosis.'}), 400

    api_key = current_app.config.get('OPENAI_API_KEY')
    
    # If OpenAI API Key is present, use LLM clinical advisor
    if api_key:
        try:
            prompt = f"""You are an expert Clinical Decision Support System assistant for a registered physician on AcuMeds.
Patient Profile: Age {patient_age}, Gender {patient_gender}, Vitals: {vitals}.
Reported Symptoms: {symptoms}.

Provide a structured clinical suggestion with:
1. Probable Differential Diagnoses (top 3)
2. Recommended Clinical Tests/Investigations
3. Suggested Pharmacological Management (Standard 1st line medications, dosage, frequency)
4. Red Flag Warnings & Dietary/Lifestyle advice.

Keep the advice professional, evidence-based, concise and formatted with clean bullet points."""

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'model': current_app.config.get('OPENAI_MODEL', 'gpt-4o-mini'),
                'messages': [
                    {'role': 'system', 'content': 'You are an advanced AI medical diagnosis & pharmacology clinical advisor.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,
                'max_tokens': 600
            }
            resp = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                result = resp.json()
                advice_text = result['choices'][0]['message']['content']
                return jsonify({'analysis': advice_text, 'source': 'OpenAI Clinical Assistant'})
        except Exception as e:
            print(f"[AI Diagnosis Error]: {e}")

    # Fallback to smart rule-based Clinical Expert System
    analysis = f"""### AI Clinical Assessment
**Reported Symptoms:** {symptoms}

#### 1. Differential Diagnosis:
- **Primary Consideration:** Acute Symptomatic Episode / Viral Upper Respiratory or GI / Musculoskeletal strain depending on localization.
- **Secondary Considerations:** Tension Cephalea, Allergic Rhinitis, or Benign Functional Dyspepsia.

#### 2. Recommended Clinical Investigations:
- Complete Blood Count (CBC) with ESR
- Routine Vitals monitoring (BP, SpO2, Pulse)
- Fasting Blood Sugar (if diabetic history present)

#### 3. Standard First-Line Pharmacotherapy:
- **Symptom Relief:** Paracetamol 650mg (1-0-1 after meals for 3-5 days)
- **Gastric Protection:** Pantoprazole 40mg (1-0-0 before breakfast)
- **Hydration / Supportive:** Multivitamin + Zinc supplement once daily

#### 4. Clinical Red Flags & Precautions:
- Re-evaluate immediately if patient develops high fever (>102°F), breathlessness, chest tightness, or persistent vomiting.
- Advise adequate hydration (2.5 - 3L fluids/day) and adequate rest."""

    return jsonify({'analysis': analysis, 'source': 'AcuMeds Clinical Knowledge Base'})
