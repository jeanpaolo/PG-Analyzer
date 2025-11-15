-- Sample data for testing PostgreSQL Performance Analyzer
-- This creates a realistic database structure with various scenarios to test

-- Create schemas
CREATE SCHEMA IF NOT EXISTS sales;
CREATE SCHEMA IF NOT EXISTS inventory;
CREATE SCHEMA IF NOT EXISTS analytics;

-- Create tables with various characteristics

-- Customers table (well-designed)
CREATE TABLE IF NOT EXISTS sales.customers (
    customer_id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Orders table (large, frequently accessed)
CREATE TABLE IF NOT EXISTS sales.orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES sales.customers(customer_id),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    shipping_address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Order items table (very large, join-heavy)
CREATE TABLE IF NOT EXISTS sales.order_items (
    item_id SERIAL PRIMARY KEY,
    order_id INTEGER NOT NULL REFERENCES sales.orders(order_id),
    product_id INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    discount DECIMAL(5, 2) DEFAULT 0
);

-- Products table
CREATE TABLE IF NOT EXISTS inventory.products (
    product_id SERIAL PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    stock_quantity INTEGER DEFAULT 0,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Product reviews (table with potential bloat)
CREATE TABLE IF NOT EXISTS inventory.product_reviews (
    review_id SERIAL PRIMARY KEY,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    review_text TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Analytics table (large table with sequential scans)
CREATE TABLE IF NOT EXISTS analytics.page_views (
    view_id BIGSERIAL PRIMARY KEY,
    user_id INTEGER,
    page_url TEXT NOT NULL,
    referrer TEXT,
    user_agent TEXT,
    ip_address INET,
    view_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes (some useful, some unused)

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_orders_customer_id ON sales.orders(customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_order_date ON sales.orders(order_date);
CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON sales.order_items(order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product_id ON sales.order_items(product_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON inventory.products(category);

-- Potentially unused indexes (for testing unused index detection)
CREATE INDEX IF NOT EXISTS idx_customers_phone ON sales.customers(phone);
CREATE INDEX IF NOT EXISTS idx_products_created_at ON inventory.products(created_at);
CREATE INDEX IF NOT EXISTS idx_reviews_updated_at ON inventory.product_reviews(updated_at);

-- Missing index scenario (page_views table will have high sequential scans)
-- Intentionally not creating index on page_views(user_id) to test missing index detection

-- Insert sample data

-- Customers
INSERT INTO sales.customers (email, first_name, last_name, phone) 
SELECT 
    'customer' || i || '@example.com',
    'First' || i,
    'Last' || i,
    '+1-555-' || LPAD(i::text, 4, '0')
FROM generate_series(1, 1000) i
ON CONFLICT (email) DO NOTHING;

-- Products
INSERT INTO inventory.products (product_name, category, price, stock_quantity, description)
SELECT 
    'Product ' || i,
    CASE (i % 5)
        WHEN 0 THEN 'Electronics'
        WHEN 1 THEN 'Clothing'
        WHEN 2 THEN 'Books'
        WHEN 3 THEN 'Home & Garden'
        ELSE 'Sports'
    END,
    (RANDOM() * 1000 + 10)::DECIMAL(10,2),
    (RANDOM() * 1000)::INTEGER,
    'Description for product ' || i
FROM generate_series(1, 500) i
ON CONFLICT DO NOTHING;

-- Orders
INSERT INTO sales.orders (customer_id, order_date, total_amount, status, shipping_address)
SELECT 
    (RANDOM() * 999 + 1)::INTEGER,
    CURRENT_TIMESTAMP - (RANDOM() * INTERVAL '365 days'),
    (RANDOM() * 1000 + 20)::DECIMAL(10,2),
    CASE (RANDOM() * 4)::INTEGER
        WHEN 0 THEN 'pending'
        WHEN 1 THEN 'processing'
        WHEN 2 THEN 'shipped'
        ELSE 'delivered'
    END,
    'Address ' || i
FROM generate_series(1, 5000) i
ON CONFLICT DO NOTHING;

-- Order items
INSERT INTO sales.order_items (order_id, product_id, quantity, unit_price, discount)
SELECT 
    (RANDOM() * 4999 + 1)::INTEGER,
    (RANDOM() * 499 + 1)::INTEGER,
    (RANDOM() * 5 + 1)::INTEGER,
    (RANDOM() * 500 + 10)::DECIMAL(10,2),
    (RANDOM() * 20)::DECIMAL(5,2)
FROM generate_series(1, 15000) i
ON CONFLICT DO NOTHING;

-- Product reviews (with some updates to create dead tuples)
INSERT INTO inventory.product_reviews (product_id, customer_id, rating, review_text)
SELECT 
    (RANDOM() * 499 + 1)::INTEGER,
    (RANDOM() * 999 + 1)::INTEGER,
    (RANDOM() * 5 + 1)::INTEGER,
    'Review text for product ' || i
FROM generate_series(1, 3000) i
ON CONFLICT DO NOTHING;

-- Update some reviews to create bloat
UPDATE inventory.product_reviews 
SET review_text = 'Updated review text', updated_at = CURRENT_TIMESTAMP
WHERE review_id % 3 = 0;

-- Page views (large table for sequential scan testing)
INSERT INTO analytics.page_views (user_id, page_url, referrer, user_agent, ip_address, view_timestamp)
SELECT 
    (RANDOM() * 999 + 1)::INTEGER,
    '/page/' || (RANDOM() * 100)::INTEGER,
    CASE WHEN RANDOM() > 0.5 THEN 'https://google.com' ELSE 'https://facebook.com' END,
    'Mozilla/5.0',
    ('192.168.' || (RANDOM() * 255)::INTEGER || '.' || (RANDOM() * 255)::INTEGER)::INET,
    CURRENT_TIMESTAMP - (RANDOM() * INTERVAL '30 days')
FROM generate_series(1, 20000) i
ON CONFLICT DO NOTHING;

-- Create a view
CREATE OR REPLACE VIEW sales.customer_order_summary AS
SELECT 
    c.customer_id,
    c.email,
    c.first_name,
    c.last_name,
    COUNT(o.order_id) as total_orders,
    SUM(o.total_amount) as total_spent
FROM sales.customers c
LEFT JOIN sales.orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.email, c.first_name, c.last_name;

-- Create a materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.daily_sales AS
SELECT 
    DATE(order_date) as sale_date,
    COUNT(*) as order_count,
    SUM(total_amount) as total_revenue
FROM sales.orders
GROUP BY DATE(order_date)
ORDER BY sale_date DESC;

-- Create sequences
CREATE SEQUENCE IF NOT EXISTS sales.invoice_number_seq START 1000;

-- Grant permissions to testuser
GRANT USAGE ON SCHEMA sales TO testuser;
GRANT USAGE ON SCHEMA inventory TO testuser;
GRANT USAGE ON SCHEMA analytics TO testuser;

GRANT SELECT ON ALL TABLES IN SCHEMA sales TO testuser;
GRANT SELECT ON ALL TABLES IN SCHEMA inventory TO testuser;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO testuser;

GRANT SELECT ON ALL SEQUENCES IN SCHEMA sales TO testuser;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA inventory TO testuser;
GRANT SELECT ON ALL SEQUENCES IN SCHEMA analytics TO testuser;

-- Analyze tables to update statistics
ANALYZE;

-- Display summary
SELECT 'Database setup complete!' as status;
SELECT schemaname, COUNT(*) as table_count 
FROM pg_tables 
WHERE schemaname IN ('sales', 'inventory', 'analytics')
GROUP BY schemaname;
