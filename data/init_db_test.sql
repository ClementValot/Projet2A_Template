DROP SCHEMA IF EXISTS tests CASCADE;
CREATE SCHEMA tests;

-- Table user
DROP TABLE IF EXISTS tests.user CASCADE;
CREATE TABLE tests.user (
    id_user SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    hash_password VARCHAR(100) NOT NULL,
    salt VARCHAR(128) NOT NULL,
    user_type VARCHAR(10) NOT NULL,
    sign_up_date DATE 
);

-- Table address
DROP TABLE IF EXISTS tests.address CASCADE;
CREATE TABLE tests.address (
    id_address SERIAL PRIMARY KEY,
    city VARCHAR(20) NOT NULL,
    postal_code VARCHAR(5) NOT NULL,
    street_name VARCHAR(50) NOT NULL,
    street_number VARCHAR(10) NOT NULL
);


-- Table customer
DROP TABLE IF EXISTS tests.customer CASCADE;
CREATE TABLE tests.customer (
    id_user INT PRIMARY KEY REFERENCES tests.user(id_user) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(40) NOT NULL
);

-- Table admin
DROP TABLE IF EXISTS tests.admin CASCADE;
CREATE TABLE tests.admin (
    id_user INT PRIMARY KEY REFERENCES tests.user(id_user) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(40) NOT NULL
);

-- Table driver
DROP TABLE IF EXISTS tests.driver CASCADE;
CREATE TABLE tests.driver (
    id_user INT PRIMARY KEY REFERENCES tests.user(id_user) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(40) NOT NULL,
    vehicle_type VARCHAR(50),
    availability BOOLEAN DEFAULT TRUE
);

-- Table item
DROP TABLE IF EXISTS tests.item CASCADE;
CREATE TABLE tests.item (
    id_item SERIAL PRIMARY KEY,
    name VARCHAR(20) NOT NULL,
    description VARCHAR(300),
    item_type VARCHAR(20) NOT NULL,
    price FLOAT NOT NULL,
    stock INT NOT NULL,
    availability BOOLEAN NOT NULL
);

-- Table bundle
DROP TABLE IF EXISTS tests.bundle CASCADE;
CREATE TABLE tests.bundle (
    id_bundle SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(300),
    bundle_type VARCHAR(20) NOT NULL,
    price FLOAT, 
    discount FLOAT 
);

-- Table bundle_required_item
DROP TABLE IF EXISTS tests.bundle_required_item CASCADE;
CREATE TABLE tests.bundle_required_item (
    id_bundle INT REFERENCES tests.bundle(id_bundle) ON DELETE CASCADE,
    item_type VARCHAR(50) NOT NULL,
    quantity_required INT NOT NULL,
    PRIMARY KEY (id_bundle, item_type)
);

-- Table bundle_item 
DROP TABLE IF EXISTS tests.bundle_item CASCADE;
CREATE TABLE tests.bundle_item (
    id_bundle INT REFERENCES tests.bundle(id_bundle) ON DELETE CASCADE,
    id_item INT REFERENCES tests.item(id_item) ON DELETE CASCADE,
    PRIMARY KEY (id_bundle, id_item)
);

-- Table order
DROP TABLE IF EXISTS tests.order CASCADE;
CREATE TABLE tests.order (
    id_order SERIAL PRIMARY KEY,
    id_user INT REFERENCES tests.user(id_user) ON DELETE CASCADE,
    status VARCHAR(20) NOT NULL,
    price FLOAT,
    id_address INT REFERENCES tests.address(id_address),
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table delivery
DROP TABLE IF EXISTS tests.delivery CASCADE;
CREATE TABLE tests.delivery (
    id_delivery SERIAL PRIMARY KEY,
    id_driver INT REFERENCES tests.driver(id_user) ON DELETE SET NULL,
    status VARCHAR(20) NOT NULL,
    delivery_time TIMESTAMP
);

-- Table delivery_order 
DROP TABLE IF EXISTS tests.delivery_order CASCADE;
CREATE TABLE tests.delivery_order (
    id_delivery INT REFERENCES tests.delivery(id_delivery) ON DELETE CASCADE,
    id_order INT REFERENCES tests.order(id_order) ON DELETE CASCADE,
    PRIMARY KEY (id_delivery, id_order)
);

-- Table order_item
DROP TABLE IF EXISTS tests.order_item CASCADE;

CREATE TABLE tests.order_item (
    id_order INT REFERENCES tests.order(id_order) ON DELETE CASCADE,
    id_item INT REFERENCES tests.item(id_item) ON DELETE CASCADE,
    quantity INT DEFAULT 1,
    CONSTRAINT unique_order_item UNIQUE (id_order, id_item)
);