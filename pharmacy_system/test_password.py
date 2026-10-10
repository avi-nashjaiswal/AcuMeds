import sqlite3
from werkzeug.security import check_password_hash

db_path = 'database/pharmacy.db'

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Get customer1's password hash
cursor.execute("SELECT username, password_hash FROM users WHERE username='customer1'")
row = cursor.fetchone()

if row:
    username, pwd_hash = row
    print(f"✅ User found: {username}")
    print(f"   Hash: {pwd_hash[:30]}...")
    
    # Test password
    test_password = 'customer123'
    result = check_password_hash(pwd_hash, test_password)
    print(f"   Password '{test_password}' check: {result}")
    
    # Try other passwords
    for test_pwd in ['customer', '123', 'wrong']:
        result = check_password_hash(pwd_hash, test_pwd)
        print(f"   Password '{test_pwd}' check: {result}")
else:
    print("❌ User not found")

conn.close()
