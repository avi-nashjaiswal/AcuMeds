"""
Automated Integration Test Suite for AcuMeds Doctor System
"""
import os
import sys
import unittest
import importlib
import werkzeug

if not hasattr(werkzeug, '__version__'):
    werkzeug.__version__ = '3.0.0'

basedir = os.path.abspath(os.path.dirname(__file__))


def load_app(system_dir_name):
    """Cleanly load app module from a specific portal folder without namespace clashes"""
    for mod in list(sys.modules.keys()):
        if mod in ['app', 'config'] or mod.startswith('app.'):
            del sys.modules[mod]

    sys_path = os.path.join(basedir, system_dir_name)
    if sys_path in sys.path:
        sys.path.remove(sys_path)
    sys.path.insert(0, sys_path)

    import app
    return app.create_app(), app.db


class DoctorSystemTests(unittest.TestCase):
    def test_01_doctor_portal(self):
        """Test Doctor portal authentication and dashboard"""
        app, db = load_app('doctor_system')
        client = app.test_client()

        # Login page
        res = client.get('/auth/login')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Doctor Portal', res.data)

        # Login with demo doctor
        login_res = client.post('/auth/login', data={
            'username': 'doctor1',
            'password': 'doctor123'
        }, follow_redirects=True)
        self.assertEqual(login_res.status_code, 200)
        self.assertIn(b'Clinical Practice Dashboard', login_res.data)

        # Verify DB models
        with app.app_context():
            from app.models import User, Doctor, DoctorAppointment
            user = User.query.filter_by(username='doctor1').first()
            self.assertIsNotNone(user)
            self.assertEqual(user.role, 'doctor')
            self.assertTrue(user.is_doctor())
            self.assertIsNotNone(user.doctor)
            self.assertTrue(user.doctor.is_verified)

    def test_02_pharmacy_doctor_booking_and_cart(self):
        """Test patient booking from pharmacy_system and 1-click cart fulfillment"""
        app, db = load_app('pharmacy_system')
        client = app.test_client()

        # Browse doctors
        res = client.get('/doctors')
        self.assertEqual(res.status_code, 200)
        self.assertIn(b'Consult Top Verified Doctors', res.data)

        with app.app_context():
            from app.models import Doctor, DoctorAppointment, DoctorPrescription, DoctorPrescriptionItem, Medicine, CartItem
            import uuid

            doc = Doctor.query.first()
            self.assertIsNotNone(doc)

            test_p_name = f"Patient {uuid.uuid4().hex[:6]}"

            # Book appointment
            book_res = client.post(f'/book-appointment/{doc.id}', data={
                'patient_name': test_p_name,
                'patient_age': '29',
                'patient_gender': 'Male',
                'patient_phone': '+91 98765 00000',
                'appointment_date': 'Today',
                'appointment_time': '05:00 PM',
                'consultation_type': 'Online Video',
                'symptoms': 'Throat irritation and mild fever for 2 days.'
            }, follow_redirects=True)
            self.assertEqual(book_res.status_code, 200)

            appt = DoctorAppointment.query.filter_by(patient_name=test_p_name).first()
            self.assertIsNotNone(appt)
            self.assertEqual(appt.status, 'Confirmed')

            # Create digital prescription linked to appointment
            test_rx_code = f"RX-TEST-{uuid.uuid4().hex[:6].upper()}"
            rx = DoctorPrescription(
                appointment_id=appt.id,
                doctor_id=doc.id,
                patient_id=appt.patient_id,
                prescription_code=test_rx_code,
                patient_name=appt.patient_name,
                patient_age=appt.patient_age,
                patient_gender=appt.patient_gender,
                vitals_bp='120/80 mmHg',
                diagnosis='Acute Pharyngitis',
                general_advice='Warm saline gargle 3 times daily.'
            )
            db.session.add(rx)
            db.session.flush()

            # Add medicine items
            med = Medicine.query.first()
            rx_item = DoctorPrescriptionItem(
                prescription_id=rx.id,
                medicine_id=med.id if med else None,
                medicine_name=med.name if med else 'Paracetamol 650mg',
                dosage='650 mg',
                frequency='1-0-1',
                timing='After Food',
                duration='3 Days',
                quantity=1
            )
            db.session.add(rx_item)
            appt.status = 'Completed'
            db.session.commit()

            # Test 1-click cart addition
            cart_res = client.post(f'/prescription/{rx.id}/add-to-cart', follow_redirects=True)
            self.assertEqual(cart_res.status_code, 200)

            # View prescription detail page
            rx_view_res = client.get(f'/prescription/{rx.id}/view')
            self.assertEqual(rx_view_res.status_code, 200)
            self.assertIn(b'Acute Pharyngitis', rx_view_res.data)

    def test_03_admin_portal_doctor_management(self):
        """Test Admin portal doctors listing and verification routes"""
        app, db = load_app('admin_system')
        client = app.test_client()

        with app.app_context():
            from app.models import Doctor, DoctorAppointment
            doctors = Doctor.query.all()
            self.assertGreaterEqual(len(doctors), 1)

            # Login admin and check doctors page
            login_res = client.post('/auth/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            self.assertEqual(login_res.status_code, 200)

            docs_res = client.get('/doctors')
            self.assertEqual(docs_res.status_code, 200)
            self.assertIn(b'Doctors Network', docs_res.data)


if __name__ == '__main__':
    unittest.main()
