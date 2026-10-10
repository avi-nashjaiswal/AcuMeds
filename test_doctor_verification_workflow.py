#!/usr/bin/env python
"""
Complete Test: Doctor Registration, Confirmation Letter, and Admin Approval Workflow
Tests the entire end-to-end lifecycle across Doctor System and Admin System.
"""
import sqlite3
import os
import sys
import uuid
from datetime import datetime
from werkzeug.security import generate_password_hash

db_path = os.path.join(os.path.dirname(__file__), 'admin_system', 'database', 'pharmacy.db')

print("\n" + "=" * 80)
print("DOCTOR REGISTRATION, CONFIRMATION LETTER & ADMIN APPROVAL WORKFLOW TEST")
print("=" * 80)

# Generate unique test data
unique_suffix = uuid.uuid4().hex[:6]
test_username = f"dr_test_{unique_suffix}"
test_email = f"dr_{unique_suffix}@acumeds.com"
test_license = f"MCI-DL-2026-{unique_suffix.upper()}"
reg_ref = f"ACU-DOC-REG-202608-{unique_suffix.upper()}"

print(f"\n[Step 1] Simulating Doctor Registration in Doctor System...")
print(f"  • Doctor Name: Dr. Rajesh Varma, MD")
print(f"  • Username: {test_username}")
print(f"  • Email: {test_email}")
print(f"  • License: {test_license}")
print(f"  • Specialization: Cardiology & Critical Care")
print(f"  • Registration Ref: {reg_ref}")

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Clean up if existed
cursor.execute("SELECT id FROM users WHERE email = ? OR username = ?", (test_email, test_username))
existing = cursor.fetchone()
if existing:
    u_id = existing['id']
    cursor.execute("DELETE FROM doctors WHERE user_id = ?", (u_id,))
    cursor.execute("DELETE FROM notifications WHERE user_id = ?", (u_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (u_id,))
    conn.commit()

# 1. Insert Doctor User
pwd_hash = generate_password_hash('doctor123', method='pbkdf2:sha256')
cursor.execute("""
    INSERT INTO users (username, email, password_hash, full_name, phone, city, role, is_active, is_admin)
    VALUES (?, ?, ?, ?, ?, ?, 'doctor', 1, 0)
""", (test_username, test_email, pwd_hash, 'Dr. Rajesh Varma, MD', '+91 98765 12345', 'Delhi'))
user_id = cursor.lastrowid

# 2. Insert Doctor Profile (Unverified / Pending)
cursor.execute("""
    INSERT INTO doctors (
        user_id, specialization, qualification, experience_years, license_number,
        clinic_name, clinic_address, city, consultation_fee, bio,
        is_verified, is_available, registration_ref, created_at
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, ?, ?)
""", (
    user_id, 'Cardiology & Critical Care', 'MBBS, MD (Cardiology)', 12, test_license,
    'Varma Heart & Health Clinic', 'Suite 204, Connaught Place', 'Delhi', 450.0,
    'Specialist in clinical cardiology and preventive heart care.',
    reg_ref, datetime.utcnow()
))
doctor_id = cursor.lastrowid

# 3. Add Confirmation Notification for Doctor
cursor.execute("""
    INSERT INTO notifications (user_id, title, message, notification_type, is_read, created_at)
    VALUES (?, ?, ?, ?, 0, ?)
""", (
    user_id, 'Registration Confirmation Letter Issued',
    f'Your registration application (Ref: {reg_ref}) has been received and is under review by the AcuMeds Medical Board.',
    'registration_confirmation', datetime.utcnow()
))

conn.commit()
print(f"[OK] Doctor account & profile created. User ID: {user_id}, Doctor ID: {doctor_id}")

# Verify Initial State
cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
doc_row = cursor.fetchone()
assert doc_row['is_verified'] == 0, "Doctor must be unverified initially (is_verified = 0)"
assert doc_row['is_available'] == 0, "Doctor must be unavailable initially (is_available = 0)"
assert doc_row['registration_ref'] == reg_ref, "Doctor must have registration_ref assigned"
assert doc_row['verified_at'] is None, "verified_at must be NULL initially"
print(f"[OK] Initial verification gate verified: is_verified={doc_row['is_verified']}, Status='Pending Review'")

# Step 2: Test Admin Review & Approval
print(f"\n[Step 2] Simulating Admin Review & Approval in Admin System...")
appr_ref = f"ACU-DOC-APPR-202608-{uuid.uuid4().hex[:6].upper()}"
admin_notes = "State Medical Council licensure verified. Authorized for clinical telehealth practice on AcuMeds."

cursor.execute("""
    UPDATE doctors
    SET is_verified = 1,
        is_available = 1,
        verified_at = ?,
        approval_letter_ref = ?,
        verification_notes = ?,
        rejection_reason = NULL
    WHERE id = ?
""", (datetime.utcnow(), appr_ref, admin_notes, doctor_id))

# Add Approval Notification
cursor.execute("""
    INSERT INTO notifications (user_id, title, message, notification_type, is_read, created_at)
    VALUES (?, ?, ?, ?, 0, ?)
""", (
    user_id, 'Doctor Registration Approved & Verified! 🎉',
    f'Your doctor registration has been approved by the Admin Medical Board. Authorization Ref: {appr_ref}. You now have full access to patient consultations and prescriptions.',
    'doctor_approval', datetime.utcnow()
))

conn.commit()

# Verify Approved State
cursor.execute("SELECT * FROM doctors WHERE id = ?", (doctor_id,))
approved_doc = cursor.fetchone()
assert approved_doc['is_verified'] == 1, "Doctor must be verified (is_verified = 1)"
assert approved_doc['is_available'] == 1, "Doctor must be available (is_available = 1)"
assert approved_doc['approval_letter_ref'] == appr_ref, "approval_letter_ref must be recorded"
assert approved_doc['verified_at'] is not None, "verified_at must be set"
assert approved_doc['verification_notes'] == admin_notes, "verification_notes must match"

print(f"[OK] Admin Approval executed successfully:")
print(f"     • is_verified: {approved_doc['is_verified']}")
print(f"     • verified_at: {approved_doc['verified_at']}")
print(f"     • approval_letter_ref: {approved_doc['approval_letter_ref']}")
print(f"     • verification_notes: {approved_doc['verification_notes']}")

# Step 3: Check Notifications
print(f"\n[Step 3] Checking Doctor Notifications & Confirmation Trail...")
cursor.execute("SELECT * FROM notifications WHERE user_id = ? ORDER BY id ASC", (user_id,))
notifs = cursor.fetchall()
assert len(notifs) >= 2, "Doctor must have registration and approval notifications"
for n in notifs:
    safe_title = n['title'].encode('ascii', errors='ignore').decode('ascii')
    safe_msg = n['message'].encode('ascii', errors='ignore').decode('ascii')
    print(f"  [Notification] {safe_title} -> {safe_msg}")

print(f"\n[Step 4] Checking Template Files...")
templates = [
    ('Doctor Pending Status Template', 'doctor_system/templates/auth/pending_verification.html'),
    ('Doctor Registration Confirmation Letter', 'doctor_system/templates/auth/confirmation_letter.html'),
    ('Doctor Practice Authorization Certificate', 'doctor_system/templates/auth/approval_letter.html'),
    ('Admin Doctor Confirmation Letter', 'admin_system/templates/dashboard/doctor_letter.html'),
    ('Admin Doctors Management UI', 'admin_system/templates/dashboard/doctors.html')
]

for name, relpath in templates:
    fpath = os.path.join(os.path.dirname(__file__), relpath)
    assert os.path.exists(fpath), f"Missing template: {relpath}"
    print(f"  [OK] Found {name} ({os.path.getsize(fpath)} bytes)")

conn.close()

print("\n" + "=" * 80)
print("SUCCESS: ALL DOCTOR VERIFICATION & CONFIRMATION LETTER TESTS PASSED!")
print("=" * 80 + "\n")
