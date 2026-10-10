import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), '..', 'admin_system', 'database', 'pharmacy.db')
print("DB Path:", os.path.abspath(db_path))

conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
tables = [row[0] for row in cur.fetchall()]
print(f"\nTables found ({len(tables)}):", tables)

print("\nTable Details:")
for table in tables:
    cur.execute(f"PRAGMA table_info({table})")
    cols = cur.fetchall()
    cur.execute(f"SELECT COUNT(*) FROM {table}")
    count = cur.fetchone()[0]
    print(f"\n--- Table: {table} ({count} rows) ---")
    for col in cols:
        print(f"  {col[1]:25s} {col[2]:15s} {'PK' if col[5] else ''} {'NOT NULL' if col[3] else ''} default={col[4]}")

conn.close()
