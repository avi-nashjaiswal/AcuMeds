#!/usr/bin/env python
"""
Database initialization script - Run this first time to create demo users
Usage: python init_db.py
"""
import os
import sys
from werkzeug.security import generate_password_hash

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.models import User, Shopkeeper, Medicine

def init_database():
    """Initialize database with demo users and medicines"""
    
    app = create_app()
    
    with app.app_context():
        # Drop all tables and recreate
        print("Creating database tables...")
        db.create_all()
        
        # Clear existing data
        User.query.delete()
        Shopkeeper.query.delete()
        Medicine.query.delete()
        
        # Create admin user
        print("Creating admin user...")
        admin = User(
            username='admin',
            email='admin@pharmacy.com',
            full_name='Admin User',
            is_admin=True,
            role='admin'
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin user created")
        print("  Username: admin")
        print("  Password: admin123")
        
        # Create test customer
        print("\nCreating test customer...")
        customer = User(
            username='customer1',
            email='customer@pharmacy.com',
            full_name='Test Customer',
            role='customer'
        )
        customer.set_password('password123')
        db.session.add(customer)
        db.session.commit()
        print("✓ Test customer created")
        print("  Username: customer1")
        print("  Password: password123")
        
        # Create shopkeeper users
        print("\nCreating shopkeeper users...")
        shopkeeper_data = [
            ('healthplus', 'healthplus@pharmacy.com', 'Health Plus Pharmacy'),
            ('medcare', 'medcare@pharmacy.com', 'Med Care Pharmacy'),
            ('wellhealth', 'wellhealth@pharmacy.com', 'Well Health Pharmacy'),
        ]
        
        for username, email, shop_name in shopkeeper_data:
            user = User(
                username=username,
                email=email,
                full_name=shop_name,
                role='shopkeeper'
            )
            user.set_password('shopkeeper123')
            db.session.add(user)
            db.session.flush()
            
            shopkeeper = Shopkeeper(
                user_id=user.id,
                shop_name=shop_name,
                license_number=f'PH-2025-{username.upper()}',
                city='India',
                contact_number='+91-9876543210',
                verified=True
            )
            db.session.add(shopkeeper)
            db.session.commit()
            print(f"✓ {shop_name} created - Username: {username} / Password: shopkeeper123")
        
        # Add sample medicines
        print("\nAdding sample medicines...")
        medicines = [
            {
                'name': 'Paracetamol 500mg',
                'category': 'Pain Relief',
                'description': 'Effective pain reliever and fever reducer',
                'price': 15.00,
                'stock_quantity': 100,
                'requires_prescription': False
            },
            {
                'name': 'Amoxicillin 500mg',
                'category': 'Antibiotic',
                'description': 'Broad-spectrum antibiotic for infections',
                'price': 45.00,
                'stock_quantity': 50,
                'requires_prescription': True
            },
            {
                'name': 'Cough Syrup',
                'category': 'Cough & Cold',
                'description': 'Effective for dry and productive cough',
                'price': 75.00,
                'stock_quantity': 75,
                'requires_prescription': False
            },
            {
                'name': 'Vitamin C Tablet',
                'category': 'Vitamins',
                'description': 'Boosts immunity and health',
                'price': 25.00,
                'stock_quantity': 200,
                'requires_prescription': False
            },
            {
                'name': 'Aspirin 75mg',
                'category': 'Cardiovascular',
                'description': 'For blood thinning and heart health',
                'price': 35.00,
                'stock_quantity': 60,
                'requires_prescription': False
            },
        ]
        
        for med in medicines:
            medicine = Medicine(**med)
            db.session.add(medicine)
        
        db.session.commit()
        print(f"✓ {len(medicines)} medicines added")
        
        print("\n" + "="*60)
        print("DATABASE INITIALIZATION COMPLETE!")
        print("="*60)
        print("\n📝 LOGIN CREDENTIALS:\n")
        print("ADMIN:")
        print("  Username: admin")
        print("  Password: admin123\n")
        print("CUSTOMER:")
        print("  Username: customer1")
        print("  Password: password123\n")
        print("SHOPKEEPER:")
        print("  Username: healthplus (or medcare, wellhealth)")
        print("  Password: shopkeeper123\n")

if __name__ == '__main__':
    init_database()
