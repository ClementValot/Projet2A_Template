DROP SCHEMA IF EXISTS project CASCADE;
CREATE SCHEMA project;

-- Table: Addresses
CREATE TABLE project.Addresses (
    address_id SERIAL PRIMARY KEY,
    address_number INT NOT NULL,
    address_street VARCHAR(256) NOT NULL,
    address_city VARCHAR(128) NOT NULL,
    address_postal_code VARCHAR(8) NOT NULL,
    address_country VARCHAR(128) NOT NULL
);

-- Table: Customers
CREATE TABLE project.Customers (
    customer_id SERIAL PRIMARY KEY,
    customer_first_name VARCHAR(128),
    customer_last_name VARCHAR(128),
    customer_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    customer_phone VARCHAR(16),
    customer_mail VARCHAR(128),
    customer_password_hash VARCHAR(512) NOT NULL,
    customer_salt CHAR(256) NOT NULL,
    customer_address_id INTEGER,
    FOREIGN KEY (customer_address_id) REFERENCES project.Addresses(address_id)
);

-- Table: Admins
CREATE TABLE project.Admins (
    admin_id SERIAL PRIMARY KEY,
    username VARCHAR(32) NOT NULL,
    admin_first_name VARCHAR(128),
    admin_last_name VARCHAR(128),
    admin_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    admin_password_hash VARCHAR(512),
    admin_salt CHAR(256)
);

-- Table: Drivers
CREATE TABLE project.Drivers (
    driver_id SERIAL PRIMARY KEY,
    driver_first_name VARCHAR(128),
    driver_last_name VARCHAR(128),
    driver_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    driver_password_hash VARCHAR(512),
    driver_salt CHAR(256),
    driver_is_delivering BOOLEAN,
    driver_phone VARCHAR(16)
);

-- Table: Orders
CREATE TABLE project.Orders (
    order_id SERIAL PRIMARY KEY,
    order_customer_id INTEGER,
    order_state INTEGER,
    order_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    order_paid_at TIMESTAMP DEFAULT NULL,
    FOREIGN KEY (order_customer_id) REFERENCES project.Customers(customer_id) ON DELETE SET NULL
);

-- Table: Items
CREATE TABLE project.Items (
    item_id SERIAL PRIMARY KEY,
    orderable_id INTEGER NOT NULL,
    item_name VARCHAR(128),
    item_price FLOAT(24) CHECK (item_price >= 0),
    item_type VARCHAR(32),
    item_description VARCHAR(256),
    item_stock INTEGER CHECK (item_stock >= 0)
);


-- Table: Bundles
CREATE TABLE project.Bundles (
    bundle_id SERIAL PRIMARY KEY,
    orderable_id INTEGER NOT NULL,
    bundle_name VARCHAR(128),
    -- bundle reduction: if 20% off, it's 20. Python App handles calculations.
    bundle_reduction INTEGER CHECK (bundle_reduction > 0 AND bundle_reduction < 100),
    bundle_description VARCHAR(256),
    bundle_availability_start_date DATE,
    bundle_availability_end_date DATE CHECK (bundle_availability_end_date > bundle_availability_start_date)
);

-- Table: Bundle_Items
CREATE TABLE project.Bundle_Items (
    bundle_id INTEGER,
    item_id INTEGER,
    item_quantity INTEGER CHECK (item_quantity > 0),
    PRIMARY KEY (bundle_id, item_id),
    FOREIGN KEY (bundle_id) REFERENCES project.Bundles(bundle_id),
    -- ON DELETE RESTRICT is the default behavior
    -- explicits the prevention of deleting items that are in a bundle
    FOREIGN KEY (item_id) REFERENCES project.Items(item_id) ON DELETE RESTRICT
);
-- Table: Orderable
CREATE TABLE project.Orderables (
    orderable_id SERIAL PRIMARY KEY,
    orderable_type VARCHAR(8) NOT NULL CHECK (orderable_type IN ('item', 'bundle')),
    orderable_image_name VARCHAR(255) DEFAULT NULL,
    orderable_image_url VARCHAR(512) DEFAULT NULL,
    is_in_menu BOOLEAN DEFAULT false
);
-- linking items and bundle to orderable
-- Table: Order_contents
CREATE TABLE project.Order_contents (
    order_id INTEGER,
    orderable_id INTEGER,
    orderable_quantity INTEGER,
    -- item_price FLOAT(24) CHECK (item_price >= 0),
    PRIMARY KEY (order_id, orderable_id),
    FOREIGN KEY (order_id) REFERENCES project.Orders(order_id),
    FOREIGN KEY (orderable_id) REFERENCES project.Orderables(orderable_id)
);

-- Table: Deliveries
CREATE TABLE project.Deliveries (
    delivery_order_id INTEGER,
    delivery_driver_id INTEGER,
    delivery_created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    delivery_state INTEGER DEFAULT 0,
    PRIMARY KEY (delivery_order_id, delivery_driver_id),
    FOREIGN KEY (delivery_order_id) REFERENCES project.Orders(order_id),
    FOREIGN KEY (delivery_driver_id) REFERENCES project.Drivers(driver_id)
);
