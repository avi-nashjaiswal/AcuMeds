import sqlite3
import os

db_path = 'database/pharmacy.db'

if not os.path.exists(db_path):
    print(f"❌ Database file does not exist at {db_path}")
else:
    print(f"✅ Database file exists")
    print(f"   File size: {os.path.getsize(db_path)} bytes")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"\n✅ Tables found: {len(tables)}")
    for table in tables:
        print(f"   - {table[0]}")
    
    # Check users
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"\n✅ Total users in database: {count}")
    
    cursor.execute("SELECT id, username, email, role FROM users ORDER BY id")
    for row in cursor.fetchall():
        print(f"   [{row[0]}] {row[1]} ({row[2]}) - Role: {row[3]}")
    
    conn.close()
