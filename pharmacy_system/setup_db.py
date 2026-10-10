#!/usr/bin/env python
"""
Setup script to initialize the database with test data
Run this before testing the app: python setup_db.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, Medicine, Shopkeeper

def setup_database():
    """Initialize database with test data"""
    app = create_app()
    
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created")
        
        # Create admin user if doesn't exist
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@acumeds.com',
                full_name='Admin User',
                role='admin',
                is_admin=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print(f"✓ Admin account created: admin / admin123")
        else:
            print("✓ Admin account already exists")
        
        # Create test medicines
        medicines = [
            ('Aspirin 500mg', 'Pain Relief', 'Effective pain relief and fever reducer', 12.00, 'images/aspirin.svg'),
            ('Vitamin C Tablet', 'Vitamins', 'Boosts immunity and overall health', 5.50, 'images/vitamin-c.svg'),
            ('Cough Syrup', 'Cough & Cold', 'Relief from cough and sore throat', 45.00, 'images/cough-syrup.svg'),
            ('Ibuprofen 400mg', 'Pain Relief', 'Anti-inflammatory and pain reliever', 25.00, 'images/ibuprofen.svg'),
            ('Paracetamol 500mg', 'Pain Relief', 'Fever and pain relief medication', 15.00, 'images/paracetamol.svg'),
            ('Antacid Tablet', 'Digestive', 'Relief from acidity and heartburn', 8.00, 'images/antacid.svg'),
        ]
        
        for name, category, description, price, image in medicines:
            med = Medicine.query.filter_by(name=name).first()
            if not med:
                med = Medicine(
                    name=name,
                    category=category,
                    description=description,
                    price=price,
                    stock_quantity=100,
                    requires_prescription=False,
                    image=image
                )
                db.session.add(med)
        
        db.session.commit()
        print("✓ Test medicines created/verified")
        
        # Create test shopkeeper if doesn't exist
        test_shopkeeper_user = User.query.filter_by(username='testshop').first()
        if not test_shopkeeper_user:
            test_shopkeeper_user = User(
                username='testshop',
                email='testshop@acumeds.com',
                full_name='Test Shop Owner',
                role='shopkeeper'
            )
            test_shopkeeper_user.set_password('shopkeeper123')
            db.session.add(test_shopkeeper_user)
            db.session.flush()
            
            # Create shopkeeper profile
            shopkeeper = Shopkeeper(
                user_id=test_shopkeeper_user.id,
                shop_name='Test Medical Store',
                license_number='LIC-2024-001',
                city='Mumbai',
                contact_number='9876543210',
                verified=False
            )
            db.session.add(shopkeeper)
            db.session.commit()
            print(f"✓ Test shopkeeper created: testshop / shopkeeper123 (Pending verification)")
        else:
            print("✓ Test shopkeeper account already exists")
        
        print("\n" + "="*50)
        print("DATABASE SETUP COMPLETE!")
        print("="*50)
        print("\nTest Accounts:")
        print("  Admin:     admin / admin123")
        print("  Shopkeeper: testshop / shopkeeper123")
        print("\nAdmin Panel: http://localhost:5000/admin/dashboard")
        print("Shopkeeper Portal: http://localhost:5001/auth/login")
        print("="*50)

if __name__ == '__main__':
    setup_database()
