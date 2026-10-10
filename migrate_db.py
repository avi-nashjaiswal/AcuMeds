#!/usr/bin/env python
"""
Database migration script to add missing columns to pharmacy.db
"""
import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), 'admin_system', 'database', 'pharmacy.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print("Database Migration Script")
print("=" * 50)

# Check and add missing columns in users table
print("\nChecking users table...")
cursor.execute("PRAGMA table_info(users)")
user_columns = {row[1] for row in cursor.fetchall()}

if 'city' not in user_columns:
    cursor.execute('ALTER TABLE users ADD COLUMN city VARCHAR(80)')
    print('[+] Added city column to users table')
else:
    print('[OK] city column already exists in users table')

# Check and add missing columns in shopkeepers table
print("\nChecking shopkeepers table...")
cursor.execute("PRAGMA table_info(shopkeepers)")
shopkeeper_columns = {row[1] for row in cursor.fetchall()}

if 'verified_at' not in shopkeeper_columns:
    cursor.execute('ALTER TABLE shopkeepers ADD COLUMN verified_at DATETIME')
    print('[+] Added verified_at column to shopkeepers table')
else:
    print('[OK] verified_at column already exists in shopkeepers table')

if 'verification_notes' not in shopkeeper_columns:
    cursor.execute('ALTER TABLE shopkeepers ADD COLUMN verification_notes TEXT')
    print('[+] Added verification_notes column to shopkeepers table')
else:
    print('[OK] verification_notes column already exists in shopkeepers table')

# Check and add missing columns in orders table
print("\nChecking orders table...")
cursor.execute("PRAGMA table_info(orders)")
order_columns = {row[1] for row in cursor.fetchall()}

if 'customer_name' not in order_columns:
    cursor.execute('ALTER TABLE orders ADD COLUMN customer_name VARCHAR(120)')
    print('[+] Added customer_name column to orders table')
else:
    print('[OK] customer_name column already exists in orders table')

if 'customer_phone' not in order_columns:
    cursor.execute('ALTER TABLE orders ADD COLUMN customer_phone VARCHAR(20)')
    print('[+] Added customer_phone column to orders table')
else:
    print('[OK] customer_phone column already exists in orders table')

if 'customer_email' not in order_columns:
    cursor.execute('ALTER TABLE orders ADD COLUMN customer_email VARCHAR(120)')
    print('[+] Added customer_email column to orders table')
else:
    print('[OK] customer_email column already exists in orders table')

if 'payment_reference' not in order_columns:
    cursor.execute('ALTER TABLE orders ADD COLUMN payment_reference VARCHAR(120)')
    print('[+] Added payment_reference column to orders table')
else:
    print('[OK] payment_reference column already exists in orders table')

if 'assigned_date' not in order_columns:
    cursor.execute('ALTER TABLE orders ADD COLUMN assigned_date TIMESTAMP')
    print('[+] Added assigned_date column to orders table')
else:
    print('[OK] assigned_date column already exists in orders table')

# Check and add missing columns in medicines table
print("\nChecking medicines table...")
cursor.execute("PRAGMA table_info(medicines)")
medicine_columns = {row[1] for row in cursor.fetchall()}

if 'strength_value' not in medicine_columns:
    cursor.execute('ALTER TABLE medicines ADD COLUMN strength_value REAL')
    print('[+] Added strength_value column to medicines table')
else:
    print('[OK] strength_value column already exists in medicines table')

if 'strength_unit' not in medicine_columns:
    cursor.execute('ALTER TABLE medicines ADD COLUMN strength_unit VARCHAR(20)')
    print('[+] Added strength_unit column to medicines table')
else:
    print('[OK] strength_unit column already exists in medicines table')

# Check and add missing columns in cart_items table
print("\nChecking cart_items table...")
cursor.execute("PRAGMA table_info(cart_items)")
cart_columns = {row[1] for row in cursor.fetchall()}

if 'shopkeeper_id' not in cart_columns:
    cursor.execute('ALTER TABLE cart_items ADD COLUMN shopkeeper_id INTEGER')
    print('[+] Added shopkeeper_id column to cart_items table')
else:
    print('[OK] shopkeeper_id column already exists in cart_items table')

# Check and add missing columns in doctors table
print("\nChecking doctors table...")
cursor.execute("PRAGMA table_info(doctors)")
doctor_columns = {row[1] for row in cursor.fetchall()}

if 'verified_at' not in doctor_columns:
    cursor.execute('ALTER TABLE doctors ADD COLUMN verified_at DATETIME')
    print('[+] Added verified_at column to doctors table')
else:
    print('[OK] verified_at column already exists in doctors table')

if 'verification_notes' not in doctor_columns:
    cursor.execute('ALTER TABLE doctors ADD COLUMN verification_notes TEXT')
    print('[+] Added verification_notes column to doctors table')
else:
    print('[OK] verification_notes column already exists in doctors table')

if 'registration_ref' not in doctor_columns:
    cursor.execute('ALTER TABLE doctors ADD COLUMN registration_ref VARCHAR(100)')
    print('[+] Added registration_ref column to doctors table')
else:
    print('[OK] registration_ref column already exists in doctors table')

if 'approval_letter_ref' not in doctor_columns:
    cursor.execute('ALTER TABLE doctors ADD COLUMN approval_letter_ref VARCHAR(100)')
    print('[+] Added approval_letter_ref column to doctors table')
else:
    print('[OK] approval_letter_ref column already exists in doctors table')

if 'rejection_reason' not in doctor_columns:
    cursor.execute('ALTER TABLE doctors ADD COLUMN rejection_reason TEXT')
    print('[+] Added rejection_reason column to doctors table')
else:
    print('[OK] rejection_reason column already exists in doctors table')

conn.commit()
conn.close()
print("\n" + "=" * 50)
print('[OK] Database schema updated successfully')
print("=" * 50)
