"""
Database initialization script for Delivery system
"""
import sqlite3
import os
import random
from werkzeug.security import generate_password_hash


def _otp_code():
    return f"{random.randint(0, 999999):06d}"


def init_db():
    """Initialize the database and create tables"""
    db_path = os.path.join(os.path.dirname(__file__), 'delivery.db')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    with open(schema_path, 'r') as f:
        schema = f.read()

    cursor.executescript(schema)
    conn.commit()

    # Clear existing data
    cursor.execute("DELETE FROM delivery_status_updates")
    cursor.execute("DELETE FROM deliveries")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM delivery_agents")
    cursor.execute("DELETE FROM users")

    # Add admin user
    admin_password = generate_password_hash('admin123')
    cursor.execute(
        "INSERT INTO users (username, email, password_hash, full_name, role) VALUES (?, ?, ?, ?, ?)",
        ('admin', 'admin@delivery.com', admin_password, 'Admin User', 'admin')
    )

    # Add delivery agents
    agent_password = generate_password_hash('delivery123')
    agents = [
        ('delivery1', 'delivery1@delivery.com', 'Delivery Agent One', 'Delhi', 'DL-01-1234'),
        ('delivery2', 'delivery2@delivery.com', 'Delivery Agent Two', 'Mumbai', 'MH-02-5678')
    ]

    agent_ids = []
    for username, email, full_name, city, vehicle in agents:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, role, city) VALUES (?, ?, ?, ?, ?, ?)",
            (username, email, agent_password, full_name, 'delivery', city)
        )
        user_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO delivery_agents (user_id, city, vehicle_number, active) VALUES (?, ?, ?, ?)",
            (user_id, city, vehicle, True)
        )
        agent_ids.append(cursor.lastrowid)

    # Add sample customers
    customer_password = generate_password_hash('customer123')
    customers = [
        ('ravi', 'ravi@example.com', 'Ravi Kumar', '9000000001', 'Delhi'),
        ('anita', 'anita@example.com', 'Anita Singh', '9000000002', 'Mumbai'),
        ('imran', 'imran@example.com', 'Imran Ali', '9000000003', 'Pune')
    ]

    customer_ids = []
    for username, email, full_name, phone, city in customers:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, full_name, phone, role, city) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (username, email, customer_password, full_name, phone, 'customer', city)
        )
        customer_ids.append(cursor.lastrowid)

    # Add sample orders
    orders = [
        (customer_ids[0], '12 Park Street, Delhi', 420.0, 'Cash on Delivery'),
        (customer_ids[1], '77 Lake View, Mumbai', 850.0, 'Online'),
        (customer_ids[2], '21 MG Road, Pune', 260.0, 'Cash on Delivery')
    ]

    order_ids = []
    for user_id, address, amount, payment_method in orders:
        cursor.execute(
            "INSERT INTO orders (user_id, delivery_address, total_amount, payment_method, payment_status, status) VALUES (?, ?, ?, ?, ?, ?)",
            (user_id, address, amount, payment_method, 'Pending', 'Pending')
        )
        order_ids.append(cursor.lastrowid)

    # Assign deliveries to first two orders
    for i, order_id in enumerate(order_ids[:2]):
        agent_id = agent_ids[i % len(agent_ids)]
        otp_code = _otp_code()
        cursor.execute(
            "INSERT INTO deliveries (order_id, delivery_agent_id, status, otp_code, delivery_fee, cash_to_collect) VALUES (?, ?, ?, ?, ?, ?)",
            (order_id, agent_id, 'Assigned', otp_code, 30.0, orders[i][2] if orders[i][3] == 'Cash on Delivery' else 0.0)
        )
        delivery_id = cursor.lastrowid
        cursor.execute(
            "INSERT INTO delivery_status_updates (delivery_id, status, note) VALUES (?, ?, ?)",
            (delivery_id, 'Assigned', 'Assigned by admin')
        )

    conn.commit()
    conn.close()
    print(f"Database initialized successfully at {db_path}")


if __name__ == '__main__':
    init_db()
