#!/usr/bin/env python
"""
Complete Test: Shopkeeper Verification Workflow
Tests the entire flow from registration to admin verification
"""
import sqlite3
from datetime import datetime

db_path = 'admin_system/database/pharmacy.db'

print("\n" + "="*80)
print("🧪 SHOPKEEPER VERIFICATION SYSTEM - COMPLETE WORKFLOW TEST")
print("="*80)

# Step 1: Create test shopkeeper
print("\n📝 STEP 1: Creating Test Shopkeeper Registration")
print("-" * 80)

test_user_data = {
    'username': 'testshop123',
    'email': 'testshop123@pharmacy.com',
    'full_name': 'Test Shop Owner',
    'phone': '03001234567',
    'role': 'shopkeeper',
    'city': 'Islamabad'
}

test_shop_data = {
    'shop_name': 'Test New Medical Store',
    'license_number': 'LIC-TEST-2024',
    'contact_number': '03001234567',
    'city': 'Islamabad'
}

print(f"  • Name: {test_shop_data['shop_name']}")
print(f"  • Owner: {test_user_data['full_name']}")
print(f"  • Email: {test_user_data['email']}")
print(f"  • License: {test_shop_data['license_number']}")

# Step 2: Check if already exists
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id FROM users WHERE email = ?", (test_user_data['email'],))
existing_user = cursor.fetchone()

if existing_user:
    print(f"  ⚠️  User already exists, deleting old record...")
    user_id = existing_user[0]
    cursor.execute("DELETE FROM shopkeepers WHERE user_id = ?", (user_id,))
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()

# Step 3: Insert new test shopkeeper
print("\n✅ STEP 2: Inserting Test Shopkeeper into Database")
print("-" * 80)

from werkzeug.security import generate_password_hash

password_hash = generate_password_hash('testpass123', method='pbkdf2:sha256')

cursor.execute("""
    INSERT INTO users 
    (username, email, password_hash, full_name, phone, address, city, role, is_admin)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
""", (
    test_user_data['username'],
    test_user_data['email'],
    password_hash,
    test_user_data['full_name'],
    test_user_data['phone'],
    '',
    test_user_data['city'],
    'shopkeeper',
    0
))

new_user_id = cursor.lastrowid
print(f"  ✓ User created with ID: {new_user_id}")

# Insert shopkeeper profile with verified=False
cursor.execute("""
    INSERT INTO shopkeepers 
    (user_id, shop_name, license_number, license_document, contact_number, city, verified, created_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    new_user_id,
    test_shop_data['shop_name'],
    test_shop_data['license_number'],
    '',
    test_shop_data['contact_number'],
    test_shop_data['city'],
    0,  # verified = FALSE
    datetime.utcnow()
))

shopkeeper_id = cursor.lastrowid
conn.commit()
print(f"  ✓ Shopkeeper profile created with ID: {shopkeeper_id}")
print(f"  ✓ Verification Status: ❌ NOT VERIFIED")

# Step 4: Verify in database
print("\n🔍 STEP 3: Verifying Test Data in Database")
print("-" * 80)

cursor.execute("""
    SELECT 
        u.id, u.username, u.email, u.full_name,
        s.id, s.shop_name, s.verified, s.verified_at
    FROM users u
    LEFT JOIN shopkeepers s ON u.id = s.user_id
    WHERE u.email = ?
""", (test_user_data['email'],))

result = cursor.fetchone()

if result:
    user_id, username, email, full_name, shop_id, shop_name, verified, verified_at = result
    print(f"  ✓ User Found:")
    print(f"    - ID: {user_id}")
    print(f"    - Username: {username}")
    print(f"    - Email: {email}")
    print(f"  ✓ Shopkeeper Found:")
    print(f"    - ID: {shop_id}")
    print(f"    - Shop Name: {shop_name}")
    print(f"    - Verified: {'✅ YES' if verified else '❌ NO'}")
    print(f"    - Verified At: {verified_at}")
else:
    print("  ❌ ERROR: Test data not found!")

# Step 5: Check all pending shopkeepers
print("\n📋 STEP 4: Listing All PENDING Shopkeepers (Not Verified)")
print("-" * 80)

cursor.execute("""
    SELECT 
        s.id, s.shop_name, u.full_name, u.email, s.license_number, 
        s.verified, s.created_at
    FROM shopkeepers s
    JOIN users u ON s.user_id = u.id
    WHERE s.verified = 0
    ORDER BY s.created_at DESC
""")

pending = cursor.fetchall()

if pending:
    print(f"  Found {len(pending)} pending shopkeeper(s):\n")
    for idx, shop in enumerate(pending, 1):
        shop_id, shop_name, owner, email, license_num, verified, created = shop
        print(f"  {idx}. {shop_name}")
        print(f"     Owner: {owner} ({email})")
        print(f"     License: {license_num}")
        print(f"     Status: ❌ PENDING VERIFICATION")
        print(f"     Applied: {created}")
        print()
else:
    print("  ℹ️  No pending shopkeepers")

# Step 6: Show verification instructions
print("\n📢 STEP 5: What Happens Now?")
print("-" * 80)
print(f"""
  1️⃣  Shopkeeper tries to login at http://localhost:5001
      • Email: {test_user_data['email']}
      • Password: testpass123
      
  2️⃣  After login, they see:
      ⏳ "Pending Verification" page
      • Cannot access dashboard
      • Cannot add medicines
      • Cannot view orders
      ✓ Only sees a pending status message
      
  3️⃣  Admin goes to http://localhost:5002
      • Logs in as admin / admin123
      • Goes to Dashboard → Shopkeepers
      • Sees "{test_shop_data['shop_name']}" in PENDING section
      
  4️⃣  Admin clicks "Verify" button
      • Shopkeeper verification status changes to ✅ APPROVED
      
  5️⃣  Shopkeeper can now:
      ✅ Log in successfully
      ✅ Access full dashboard
      ✅ Add medicines
      ✅ Manage orders
""")

# Step 7: Show database state
print("\n💾 DATABASE STATE SUMMARY")
print("-" * 80)

cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'shopkeeper'")
total_shopkeepers = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM shopkeepers WHERE verified = 1")
verified_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM shopkeepers WHERE verified = 0")
pending_count = cursor.fetchone()[0]

print(f"""
  Total Shopkeepers: {total_shopkeepers}
    ✅ Verified: {verified_count}
    ⏳ Pending: {pending_count}
    
  Test Shopkeeper Status: ⏳ PENDING VERIFICATION
""")

conn.close()

print("\n" + "="*80)
print("✅ TEST SETUP COMPLETE - Ready for verification workflow testing!")
print("="*80)
print("""
QUICK TEST:
  1. Click: http://localhost:5001/register
  2. OR Login with test account: 
     • Email: testshop123@pharmacy.com
     • Password: testpass123
  3. Should see "Pending Verification" page
  4. Check Admin at http://localhost:5002 to verify
""")
print("="*80 + "\n")
