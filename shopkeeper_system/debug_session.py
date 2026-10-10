"""
Debug script to test session persistence in shopkeeper system
Run this to verify cookies and sessions are working correctly
"""
from app import create_app, db
from app.models import User, Shopkeeper
from flask_login import login_user
import sys

app = create_app()

with app.app_context():
    # Create a test client
    client = app.test_client()
    
    print("=" * 70)
    print("SHOPKEEPER SYSTEM - SESSION DEBUG")
    print("=" * 70)
    
    # Step 1: Check if user exists
    print("\n1. Checking for medicareshop user...")
    user = User.query.filter_by(email='medicareshop@pharmacy.com').first()
    
    if user:
        print(f"   ✓ User found: {user.email}")
        shopkeeper = Shopkeeper.query.filter_by(user_id=user.id).first()
        if shopkeeper:
            print(f"   ✓ Shopkeeper profile found: {shopkeeper.shop_name}")
            print(f"   ✓ Verified: {shopkeeper.verified}")
        else:
            print("   ✗ No shopkeeper profile!")
    else:
        print("   ✗ User not found!")
        sys.exit(1)
    
    # Step 2: Test login
    print("\n2. Testing login request...")
    response = client.post('/auth/login', data={
        'email': 'medicareshop@pharmacy.com',
        'password': 'test123456'
    }, follow_redirects=False)
    
    print(f"   Response Status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'N/A')}")
    
    # Check cookies
    if response.headers.get('Set-Cookie'):
        print("   ✓ Session cookie set!")
    else:
        print("   ✗ No session cookie!")
    
    # Step 3: Test protected route
    print("\n3. Testing dashboard access...")
    response = client.get('/', follow_redirects=False)
    print(f"   Response Status: {response.status_code}")
    print(f"   Location: {response.headers.get('Location', 'N/A')}")
    
    # Step 4: Check app config
    print("\n4. Flask Configuration:")
    print(f"   SECRET_KEY set: {bool(app.config.get('SECRET_KEY'))}")
    print(f"   PERMANENT_SESSION_LIFETIME: {app.config.get('PERMANENT_SESSION_LIFETIME')} seconds")
    print(f"   SESSION_REFRESH_EACH_REQUEST: {app.config.get('SESSION_REFRESH_EACH_REQUEST')}")
    print(f"   SESSION_COOKIE_HTTPONLY: {app.config.get('SESSION_COOKIE_HTTPONLY')}")
    print(f"   SESSION_COOKIE_SAMESITE: {app.config.get('SESSION_COOKIE_SAMESITE')}")
    
    print("\n" + "=" * 70)
    print("✓ Debug check complete!")
    print("=" * 70)
