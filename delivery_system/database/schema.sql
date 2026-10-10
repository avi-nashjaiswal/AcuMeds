-- Delivery System Database Schema

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    age INTEGER,
    gender VARCHAR(20),
    phone VARCHAR(20),
    address TEXT,
    city VARCHAR(80),
    role VARCHAR(20) DEFAULT 'delivery',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Shopkeepers Table
CREATE TABLE IF NOT EXISTS shopkeepers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    shop_name VARCHAR(120) NOT NULL,
    city VARCHAR(80),
    contact_number VARCHAR(20),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Delivery Agents Table
CREATE TABLE IF NOT EXISTS delivery_agents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    vehicle_number VARCHAR(40),
    city VARCHAR(80),
    active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    shopkeeper_id INTEGER,
    delivery_address TEXT,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    estimated_delivery_date DATE,
    assigned_date TIMESTAMP,
    delivery_date TIMESTAMP,
    delivery_notes TEXT,
    delivery_proof VARCHAR(255),
    payment_method VARCHAR(80) DEFAULT 'Cash on Delivery',
    payment_status VARCHAR(50) DEFAULT 'Pending',
    payment_reference VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id)
);

-- Deliveries Table
CREATE TABLE IF NOT EXISTS deliveries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER UNIQUE NOT NULL,
    delivery_agent_id INTEGER NOT NULL,
    status VARCHAR(30) DEFAULT 'Assigned',
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    picked_up_at TIMESTAMP,
    out_for_delivery_at TIMESTAMP,
    delivered_at TIMESTAMP,
    otp_code VARCHAR(8),
    otp_verified_at TIMESTAMP,
    delivery_fee DECIMAL(10, 2) DEFAULT 0,
    cash_to_collect DECIMAL(10, 2) DEFAULT 0,
    last_lat REAL,
    last_lng REAL,
    last_location_at TIMESTAMP,
    notes TEXT,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (delivery_agent_id) REFERENCES delivery_agents(id)
);

-- Delivery Status Updates Table
CREATE TABLE IF NOT EXISTS delivery_status_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    delivery_id INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    note TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (delivery_id) REFERENCES deliveries(id)
);

-- Indexes
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_shopkeeper ON orders(shopkeeper_id);
CREATE INDEX idx_order_status ON orders(status);
CREATE INDEX idx_delivery_agent ON deliveries(delivery_agent_id);
CREATE INDEX idx_delivery_order ON deliveries(order_id);
CREATE INDEX idx_delivery_status ON deliveries(status);
CREATE INDEX idx_delivery_updates_delivery ON delivery_status_updates(delivery_id);
