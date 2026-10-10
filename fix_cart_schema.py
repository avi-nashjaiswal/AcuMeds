import sqlite3

conn = sqlite3.connect('admin_system/database/pharmacy.db')
cursor = conn.cursor()

try:
    # Add the shopkeeper_id column if it doesn't exist
    cursor.execute('ALTER TABLE cart_items ADD COLUMN shopkeeper_id INTEGER')
    conn.commit()
    print('✅ Added shopkeeper_id column to cart_items table')
except sqlite3.OperationalError as e:
    if 'duplicate column name' in str(e):
        print('⚠️  Column already exists')
    else:
        print(f'❌ Error: {e}')

# Verify
cursor.execute("PRAGMA table_info(cart_items)")
columns = cursor.fetchall()
print('\n✅ cart_items table columns:')
for col in columns:
    print(f'   - {col[1]} ({col[2]})')

conn.close()
