-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    age INTEGER,
    gender VARCHAR(20),
    role VARCHAR(20) DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_admin BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE
);

-- Shopkeepers Table
CREATE TABLE IF NOT EXISTS shopkeepers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER UNIQUE NOT NULL,
    shop_name VARCHAR(120) NOT NULL,
    license_number VARCHAR(80),
    license_document VARCHAR(255),
    city VARCHAR(80),
    contact_number VARCHAR(20),
    verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Medicines Table
CREATE TABLE IF NOT EXISTS medicines (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(120) NOT NULL,
    category VARCHAR(80) NOT NULL,
    description TEXT,
    strength_value REAL,
    strength_unit VARCHAR(20),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    requires_prescription BOOLEAN DEFAULT FALSE,
    side_effects TEXT,
    usage_instructions TEXT,
    image VARCHAR(255) DEFAULT 'images/medicine-default.png',
    shopkeeper_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id)
);

-- Cart items Table
CREATE TABLE IF NOT EXISTS cart_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    shopkeeper_id INTEGER,
    quantity INTEGER NOT NULL,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id),
    FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id)
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'Pending',
    estimated_delivery_date DATE,
    shopkeeper_id INTEGER,
    customer_name VARCHAR(120) NOT NULL,
    customer_phone VARCHAR(20),
    customer_email VARCHAR(120),
    assigned_date TIMESTAMP,
    delivery_date TIMESTAMP,
    delivery_address TEXT,
    delivery_notes TEXT,
    delivery_proof VARCHAR(255),
    payment_reference VARCHAR(120),
    refund_request_status VARCHAR(50) DEFAULT 'None',
    refund_request_amount DECIMAL(10, 2),
    refund_request_reason TEXT,
    refund_requested_at TIMESTAMP,
    refund_requested_by VARCHAR(120),
    refund_status VARCHAR(50) DEFAULT 'Not Refunded',
    refund_amount DECIMAL(10, 2),
    refund_reason TEXT,
    refund_processed_at TIMESTAMP,
    refund_processed_by VARCHAR(120),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (shopkeeper_id) REFERENCES shopkeepers(id)
);

-- Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price_at_purchase DECIMAL(10, 2) NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id)
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

-- Medicine Ratings Table
CREATE TABLE IF NOT EXISTS medicine_ratings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    medicine_id INTEGER NOT NULL,
    order_item_id INTEGER NOT NULL UNIQUE,
    rating INTEGER NOT NULL,
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (medicine_id) REFERENCES medicines(id),
    FOREIGN KEY (order_item_id) REFERENCES order_items(id)
);

-- Prescriptions Table
CREATE TABLE IF NOT EXISTS prescriptions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    file_path VARCHAR(255),
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Symptom Recommendations Table
CREATE TABLE IF NOT EXISTS recommendations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    symptoms VARCHAR(500),
    recommended_medicines TEXT,
    symptoms_matched TEXT,
    confidence INTEGER DEFAULT 0,
    recommendation_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Notifications Table
CREATE TABLE IF NOT EXISTS notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50),
    related_order_id INTEGER,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (related_order_id) REFERENCES orders(id)
);

-- Create indexes for faster queries
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_medicine_category ON medicines(category);
CREATE INDEX idx_cart_user ON cart_items(user_id);
CREATE INDEX idx_order_user ON orders(user_id);
CREATE INDEX idx_order_shopkeeper ON orders(shopkeeper_id);
CREATE INDEX idx_delivery_agent ON deliveries(delivery_agent_id);
CREATE INDEX idx_delivery_order ON deliveries(order_id);
CREATE INDEX idx_delivery_status ON deliveries(status);
CREATE INDEX idx_delivery_updates_delivery ON delivery_status_updates(delivery_id);
CREATE INDEX idx_prescription_user ON prescriptions(user_id);
CREATE INDEX idx_notification_user ON notifications(user_id);
CREATE INDEX idx_notification_read ON notifications(is_read);
CREATE INDEX idx_rating_medicine ON medicine_ratings(medicine_id);
CREATE INDEX idx_rating_user ON medicine_ratings(user_id);
CREATE INDEX idx_rating_order_item ON medicine_ratings(order_item_id);
