import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db')
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT id, username, email, role, is_active, is_admin FROM users")
for u in cur.fetchall():
    print(u)

conn.close()
