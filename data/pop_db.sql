INSERT INTO fd.user (id_user, username, hash_password, salt, user_type, sign_up_date) VALUES
(1,'groupe8', '0fb57c52498aa60e706f4c065f8681a10786fffca4e375880a6f9354075c7913', '148832655724dae986ad7fb0b44a727b11befb22ff319bc3fc9804c296ccff36', 'admin', '2000-01-01'), -- Pwd: Sq5GxkKbvi3(
(2, 'jane_smith', '54188f349247996b9dcfa428a9318d23a727d16a282929f702074db5fcae5edc', 'e7dd6e29e784440d9fa5fb2a7b8f0a884197247a3d41072590cee330359bcea4', 'customer', '2024-02-20'), -- Pwd: wZm$JT4vLhp@
(3, 'bob_driver', '344f2ef0ccd686819cebde68d63a4965f13d9c8664deab1d1184d2981753a15c', '37a7af87bf28c447f88774398c073c32374a17281daceb87dc25bb3677d62813', 'driver', '2024-01-10'), -- Pwd: $ge8)4AP2Oj)
(4,'john_doe', '6d0efe03fdae098e0cd67c1805b20181befea2162978102943b29a2b304a0d23', 'cd5e3de8653d246f2c572c49468c9a8891f4ae33de4048ee2d9c6f7a54b7cc48', 'customer', '2024-01-15'), -- Pwd: 5Clfso1Ld&#(
(5, 'charlie_customer', '29891ef18fd51873f7b73e2a5446d57e4c6b5f5cf4f49f705a3be04479db94cc', 'aa42289de71e4e16b720ee2e6cb74a0c41f0e0b65d4a70cb8d15415c01cef93c', 'customer', '2024-03-05'), -- Pwd: BAp6O#pF(z6A
(6, 'emma_white', '114110414987309953cef16fb636fe64b717aa1114499a1292d00b974fd12e55', 'a5d6573955d868f0c4c67db05f134a6a33d7122aefb01df5ef297380a2587081', 'customer', '2024-04-10'), -- Pwd: 3%R*6#r9TqXE
(7, 'liam_brown', 'bd7f0b7c01a7650f3fbb338807a5fada5c3d731dbdb3aa2fb0535077512e8891', '451cb307c3240179cf6fd6f1813791024c1745c9c7128910a04262d26a60ebbc', 'customer', '2024-05-01'), -- Pwd: 61o4)!mh6APF
(8, 'sophia_clark', 'cb597753c62dc8df46c8f0fd5367f82c46c7b0f4cdc36400e276dca8f36b0ca5', 'c87499199d36c42becfa9199b3d220c6e90f06ddb91632e3eaf99a8bce914b6f', 'customer', '2024-05-15'), -- Pwd: jdqLFj6O&0I2
(9, 'Bryanisinthekitchen', 'b05657c8b698170d8e35db17484e832228ea5c027e035ae8eb2de78087c1a50d', '786e21382164a7667bab9bce9b41077a86e0ff01c567370f8421847f60bf8064', 'driver', '2024-02-15'), -- Pwd: @sv5*gNLw4sm
(10, 'Maxivitesse', 'e024562a4cfebf5bed32ee204d3349722efce9fb7b058e65986274f706d3317c', '36437258a6311e841f5b726b5e7759e4eb698c6f2a168d6d43384e68bda9d40c', 'driver', '2024-03-20'), -- Pwd: R3c*f#3bF1H%
(11, 'james_lewis', '5c0e665092ef000f7ed297eceb54fa52c9fb66fde409af0a7d2a3a8cc5ff36cf', '1f58912c6ccf0c21759c2042c329ed10d3964b47d5767a0fd87b5130f8b41d26', 'admin', '2024-01-20'), -- Pwd: 0zMzh3Fyli)$
(12, 'ava_walker', '984c6742d1c1a4895d4a30116ddd9e2b8728d60428f2c22a7b0c1010a060043c', '52e3fa0c832ecaa1802bd1773fbfda05a13b1d3332bbb1e76bcdf741142673f5', 'customer', '2024-06-01'), -- Pwd: hl*O4o5nnbH)
(13, 'william_hall', '2d83014064f177b65938212d98e327f5224a8baa5bf9f27f8221676e7ed720e3', '3cbdd98e3f1ed2caa46cc81b1f9fde31fccd20cf6cde57279e208904bea6e892', 'customer', '2024-06-10'); -- Pwd: 0STU37RVhTY^

INSERT INTO fd.address (city, postal_code, street_name, street_number) VALUES
('Rennes', '35000', 'Rue de la Soif', 10),
('Rennes', '35000', 'Place de la Mairie', 25),
('Rennes', '35200', 'Avenue Jean Jaurès', 50),
('Rennes', '35700', 'Rue de Fougères', 15),
('Rennes', '35000', 'Place Sainte-Anne', 100);

INSERT INTO fd.customer (id_user, name, phone_number) VALUES
(4, 'John Doe', '+33 6 01 02 03 04'),
(2, 'Jane Smith', '+33 6 12 34 56 78'),
(5, 'Charlie Customer', '+33 6 23 45 67 89'),
(6, 'Emma White', '+33 6 06 06 06 06'),
(7, 'Liam Brown', '+33 6 07 07 07 07'),
(8, 'Sophia Clark', '+33 6 08 08 08 08'),
(12, 'Ava Walker', '+33 6 12 12 12 12'),
(13, 'William Hall', '+33 6 13 13 13 13');

INSERT INTO fd.admin (id_user, name, phone_number) VALUES
(1, 'Groupe 8', '+33 7 69 52 27 94');

INSERT INTO fd.driver (id_user, name, phone_number, vehicle_type, availability) VALUES
(3, 'Bob Driver', '+33 6 45 67 89 01', 'bike', TRUE),
(9, 'Bryan Donato Da Costa', '+33 6 56 87 46 89', 'car', TRUE),
(10, 'Maxine Voinson', '+33 6 67 54 78 91', 'car', TRUE);

INSERT INTO fd.item (name, item_type, price, stock, availability) VALUES
('Banh mi', 'main', 10.50, 20, TRUE),
('Fajitas', 'main', 14.00, 15, TRUE),
('Galettes bretonnes', 'main', 9.00, 30, TRUE),
('Caesar Salad', 'starter', 8.50, 10, TRUE),
('Greek Salad', 'starter', 7, 10, TRUE),
('Tarte aux pommes', 'dessert', 6.00, 8, TRUE),
('Coca Cola', 'drink', 3.00, 30, TRUE),
('Mineral Water', 'drink', 2.00, 25, TRUE),
('Lemonade', 'drink', 3, 20, TRUE),
('Classic Burger', 'main', 11.00, 12, TRUE),
('Fries', 'side', 3, 18, TRUE),
('Mozzarella sticks', 'side', 4, 15, TRUE);

INSERT INTO fd.bundle (name, description, bundle_type,  price, discount) VALUES
('Banh mi Menu', 'Banh mi + Drink + Dessert', 'predefined', 17.00, NULL),
('Burger Menu', 'Burger + Fries + Drink', 'predefined', 16.00, NULL);

INSERT INTO fd.bundle (name, description, bundle_type, price, discount) VALUES
('Promo for couple', 'Buy 2 main, get 10% off', 'discount',  NULL, 0.10),
('Main and drink', '', 'discount', NULL, 0.20),
('Complete bundle', '', 'discount', NULL, 0.2);

INSERT INTO fd.bundle_required_item (id_bundle, item_type, quantity_required) VALUES
(3, 'main', 2),
(4, 'main', 1),
(4, 'drink', 1),
(5, 'main', 1),
(5, 'starter', 1),
(5, 'dessert', 1);

INSERT INTO fd.bundle_item (id_bundle, id_item) VALUES
(1, 1),
(1, 9),
(1, 6),
(2, 9),
(2, 10),
(2, 11);

INSERT INTO fd.order (id_user, status, price, id_address, order_date) VALUES
(1, 'delivered', 13.5, 1, '2024-10-01 12:30:00'),
(2, 'in_progress', 31, 2, '2024-10-06 18:45:00'),
(5, 'pending', 19, 3, '2024-10-06 19:15:00'),
(4, 'in_progress', 11, 4, '2024-10-06 20:00:00'),
(4, 'in_progress', 15.5, 5, '2024-10-06 20:05:00'); 

INSERT INTO fd.delivery (id_driver, status, delivery_time) VALUES
(3, 'delivered', '2024-10-01 13:15:00'),
(3, 'in_progress', NULL),
(3, 'in_progress', NULL);

INSERT INTO fd.delivery_order (id_delivery, id_order) VALUES
(1, 1),
(2, 2),
(2, 4),
(2, 5);

INSERT INTO fd.order_item (id_order, id_item) VALUES
(1, 1),
(1, 6),
(2, 2),
(2, 8),
(3, 9),
(3, 10),
(3, 5),
(4, 3),
(4, 7),
(5, 4),
(5, 11),
(5, 6);


SELECT setval('fd.user_id_user_seq', (SELECT MAX(id_user) FROM fd.user));
SELECT setval('fd.address_id_address_seq', (SELECT MAX(id_address) FROM fd.address));
SELECT setval('fd.item_id_item_seq', (SELECT MAX(id_item) FROM fd.item));
SELECT setval('fd.bundle_id_bundle_seq', (SELECT MAX(id_bundle) FROM fd.bundle));
SELECT setval('fd.order_id_order_seq', (SELECT MAX(id_order) FROM fd.order));
SELECT setval('fd.delivery_id_delivery_seq', (SELECT MAX(id_delivery) FROM fd.delivery));