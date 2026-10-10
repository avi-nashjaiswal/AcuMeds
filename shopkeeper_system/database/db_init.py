"""
Database initialization script
This script sets up the SQLite database and creates necessary tables
"""
import sqlite3
import os
from datetime import datetime, timedelta

def init_db():
    """Initialize the database and create tables"""
    db_path = os.path.join(os.path.dirname(__file__), 'pharmacy.db')
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Read and execute schema
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()
    
    # Execute schema
    cursor.executescript(schema)
    conn.commit()

    # Ensure compatibility with older DBs: add new columns if missing
    # Check medicines table columns
    cursor.execute("PRAGMA table_info(medicines)")
    medicine_cols = [row[1] for row in cursor.fetchall()]
    if 'strength_value' not in medicine_cols:
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN strength_value REAL")
        except sqlite3.OperationalError:
            pass
    if 'strength_unit' not in medicine_cols:
        try:
            cursor.execute("ALTER TABLE medicines ADD COLUMN strength_unit VARCHAR(20)")
        except sqlite3.OperationalError:
            pass
    # Check orders table columns
    cursor.execute("PRAGMA table_info(orders)")
    order_cols = [row[1] for row in cursor.fetchall()]
    if 'shopkeeper_id' not in order_cols:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN shopkeeper_id INTEGER")
            cursor.execute("ALTER TABLE orders ADD COLUMN assigned_date TIMESTAMP")
        except sqlite3.OperationalError:
            pass
    if 'delivery_date' not in order_cols:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN delivery_date TIMESTAMP")
            cursor.execute("ALTER TABLE orders ADD COLUMN delivery_address TEXT")
            cursor.execute("ALTER TABLE orders ADD COLUMN delivery_notes TEXT")
            cursor.execute("ALTER TABLE orders ADD COLUMN delivery_proof VARCHAR(255)")
        except sqlite3.OperationalError:
            pass
    if 'payment_method' not in order_cols:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN payment_method VARCHAR(80)")
        except sqlite3.OperationalError:
            pass
    if 'payment_status' not in order_cols:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN payment_status VARCHAR(50) DEFAULT 'Pending'")
        except sqlite3.OperationalError:
            pass
    if 'payment_reference' not in order_cols:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN payment_reference VARCHAR(120)")
        except sqlite3.OperationalError:
            pass
    if 'updated_at' not in order_cols:
        try:
            cursor.execute("ALTER TABLE orders ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
        except sqlite3.OperationalError:
            pass
    
    # Check recommendations table columns
    cursor.execute("PRAGMA table_info(recommendations)")
    cols = [row[1] for row in cursor.fetchall()]
    if 'symptoms_matched' not in cols:
        try:
            cursor.execute("ALTER TABLE recommendations ADD COLUMN symptoms_matched TEXT")
        except sqlite3.OperationalError:
            pass
    if 'confidence' not in cols:
        try:
            cursor.execute("ALTER TABLE recommendations ADD COLUMN confidence INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass
    conn.commit()
    
    # Add sample data
    add_sample_data(cursor, conn)
    
    conn.close()
    print(f"Database initialized successfully at {db_path}")

def add_sample_data(cursor, conn):
    """Add sample medicines and admin user"""
    
    # Clear existing data
    cursor.execute("DELETE FROM medicines")
    cursor.execute("DELETE FROM users")
    cursor.execute("DELETE FROM shopkeepers")
    
    # Add admin user (password: admin123)
    from werkzeug.security import generate_password_hash
    admin_password = generate_password_hash('admin123')
    cursor.execute("""
        INSERT INTO users (username, email, password_hash, full_name, is_admin, role) 
        VALUES (?, ?, ?, ?, ?, ?)
    """, ('admin', 'admin@pharmacy.com', admin_password, 'Admin User', True, 'admin'))
    
    # Add test shopkeepers (verified vendors)
    shopkeeper_password = generate_password_hash('shopkeeper123')
    
    shopkeeper_users = [
        ('healthplus', 'healthplus@pharmacy.com', shopkeeper_password, 'Health Plus Pharmacy', 'shopkeeper'),
        ('medcare', 'medcare@pharmacy.com', shopkeeper_password, 'Med Care Pharmacy', 'shopkeeper'),
        ('wellhealth', 'wellhealth@pharmacy.com', shopkeeper_password, 'Well Health Pharmacy', 'shopkeeper'),
    ]
    
    shopkeeper_ids = []
    for username, email, pwd, fullname, role in shopkeeper_users:
        cursor.execute("""
            INSERT INTO users (username, email, password_hash, full_name, role) 
            VALUES (?, ?, ?, ?, ?)
        """, (username, email, pwd, fullname, role))
        
        user_id = cursor.lastrowid
        shopkeeper_ids.append(user_id)
    
    # Add shopkeeper details
    shopkeeper_details = [
        (shopkeeper_ids[0], 'Health Plus Pharmacy', 'PH-2025-001', 'Mumbai', '+91-9876543210', True),
        (shopkeeper_ids[1], 'Med Care Pharmacy', 'PH-2025-002', 'Delhi', '+91-9876543211', True),
        (shopkeeper_ids[2], 'Well Health Pharmacy', 'PH-2025-003', 'Bangalore', '+91-9876543212', True),
    ]
    
    for user_id, shop_name, license_num, city, contact, verified in shopkeeper_details:
        cursor.execute("""
            INSERT INTO shopkeepers (user_id, shop_name, license_number, city, contact_number, verified) 
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, shop_name, license_num, city, contact, verified))
    
    conn.commit()
    
    # Add sample medicines with realistic Indian market prices (INR)
    # Format: (name, category, description, price, stock_quantity, requires_prescription, side_effects, usage_instructions, image, shopkeeper_id)
    medicines = [
        # Painkillers - distributed across shopkeepers
        ("Aspirin", "Painkillers", "Effective pain relief and fever reducer", 15, 100, False, "Stomach upset, allergic reactions", "Take 1-2 tablets every 4-6 hours", "images/aspirin-photo.svg", shopkeeper_ids[0]),
        ("Ibuprofen", "Painkillers", "Anti-inflammatory pain reliever", 25, 150, False, "GI upset, dizziness", "Take 1 tablet every 6-8 hours", "images/ibuprofen-photo.svg", shopkeeper_ids[1]),
        ("Paracetamol", "Painkillers", "Safe over-the-counter pain reliever", 12, 200, False, "Rare allergic reactions", "Take 1-2 tablets every 4-6 hours", "images/paracetamol-photo.svg", shopkeeper_ids[2]),
        
        # Antibiotics
        ("Amoxicillin", "Antibiotics", "Broad-spectrum antibiotic (500mg)", 65, 50, True, "Allergic reactions, diarrhea", "Take as prescribed by doctor", "images/medicine-default.png", shopkeeper_ids[0]),
        ("Ciprofloxacin", "Antibiotics", "Fluoroquinolone antibiotic (500mg)", 85, 40, True, "Tendon problems, photosensitivity", "Take twice daily with water", "images/medicine-default.png", shopkeeper_ids[1]),
        
        # Cold & Cough
        ("Cough Syrup", "Cold & Cough", "Effective cough suppressant", 80, 80, False, "Drowsiness, dizziness", "Take 10ml every 6 hours", "images/cough-syrup-photo.svg", shopkeeper_ids[2]),
        ("Decongestant", "Cold & Cough", "Nasal congestion relief", 45, 120, False, "Nervousness, insomnia", "Take as directed on package", "images/medicine-default.png", shopkeeper_ids[0]),
        
        # Antacids
        ("Omeprazole", "Antacids", "Reduces stomach acid (20mg)", 70, 60, False, "Headache, abdominal pain", "Take 1 capsule daily", "images/antacid-photo.svg", shopkeeper_ids[1]),
        ("Ranitidine", "Antacids", "Heartburn and acid reflux relief", 55, 70, False, "Headache, constipation", "Take 1-2 tablets as needed", "images/medicine-default.png", shopkeeper_ids[2]),
        
        # Vitamins
        ("Vitamin C", "Vitamins", "Immune system booster", 40, 200, False, "Rare kidney stones", "Take 1 tablet daily", "images/vitamin-c-photo.svg", shopkeeper_ids[0]),
        ("Vitamin B Complex", "Vitamins", "Energy and metabolism support", 60, 150, False, "Nausea, headache", "Take 1 tablet daily", "images/medicine-default.png", shopkeeper_ids[1]),
        
        # Antihistamines
        ("Cetirizine", "Antihistamines", "Allergy and itch relief (10mg)", 35, 100, False, "Drowsiness, dry mouth", "Take 1 tablet once or twice daily", "images/medicine-default.png", shopkeeper_ids[2]),
        ("Loratadine", "Antihistamines", "Non-drowsy allergy relief (10mg)", 75, 90, False, "Headache, dry mouth", "Take 1 tablet daily", "images/medicine-default.png", shopkeeper_ids[0]),
        
        # Diabetes
        ("Metformin", "Diabetes", "Type 2 diabetes management (500mg)", 95, 50, True, "Nausea, metallic taste", "Take as prescribed", "images/medicine-default.png", shopkeeper_ids[1]),
        ("Insulin", "Diabetes", "Insulin for diabetes control", 1500, 30, True, "Hypoglycemia, injection site reactions", "Use as directed by doctor", "images/medicine-default.png", shopkeeper_ids[2]),
    ]
    
    for med in medicines:
        cursor.execute("""
            INSERT INTO medicines (name, category, description, price, stock_quantity, requires_prescription, side_effects, usage_instructions, image, shopkeeper_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, med)
    
    conn.commit()
    print("Sample data added successfully!")

if __name__ == '__main__':
    init_db()
