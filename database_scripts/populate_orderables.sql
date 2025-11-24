INSERT INTO project.Orderables (orderable_type, is_in_menu, orderable_image_name, orderable_image_url)
VALUES
    ('item', true, 'image_item_galette_saucisse', 'https://www.krill.fr/media/recipe/resized/700x700/recipe/352074-R-GALETTE-SAUCISSE-C.jpg'),
    ('item', true, 'image_item_fajitas_vg', 'https://media.bonduelle.com/apr_128477/FRGP14839-fajitas_veggie_30967.webp'),
    ('item', true, 'image_item_coca-cola_33cl', 'https://pizzavia.fr/wp-content/uploads/2025/01/coca.png'),
    ('item', true, 'image_item_bahn-mi', 'https://images.getrecipekit.com/20230518150440-andy-20cooks-20-20bahn-20mi.jpg'),
    ('item', false, 'image_item_tiramisu', 'https://images.ctfassets.net/1p5r6txvlxu4/2AuCQgVaK08nA3Wgm7TJbr/7981b99d4a52359fe5dd1090dd2ec96a/Tiramisu_original.jpg'),
    ('item', false, 'image_item_chips', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQJYqc9TgYa8FBwpM0X98qKK76hzccD-sUhjg&s'),
    ('bundle', true, 'image_bundle_ah_t''as_faim', 'https://uploads.dailydot.com/2024/09/rubbing-hands-emoji.jpg'),
    ('bundle', true, 'image_bundle_la_totale', 'https://i.pinimg.com/564x/c6/c4/1e/c6c41ed61a1ed83c500c7ab0e5a54bfc.jpg'),
    ('bundle', true, 'image_bundle_mejico', 'https://www.larousse.fr/encyclopedie/data/images/1009548-Drapeau_du_Mexique.jpg');

INSERT INTO project.Items (
    orderable_id, item_name, item_price, item_type,
    item_description, item_stock
)
VALUES
    (1, 'Galette Saucisse', 4.90, 'Main course',
        'La meilleure galette saucisse de Rennes', 120),

    (2, 'Fajitas VG', 4, 'Main course',
        'Des fajitas au stick de mozzarella frits', 200),

    (3, 'Coca-Cola 33cl', 1.50, 'Drink',
        'Canette de Coca-Cola', 300),

    (4, 'Bahn-Mi', 3.9, 'Main course',
        'Sandwich vietnamien aux crudités et poulet mariné', 75),

    (5, 'Tiramisu', 3, 'Dessert',
        'Tiramisu-holic', 40),

    (6, 'Chips', 1, 'Side dish',
        'Des chips natures', 250);


INSERT INTO project.Bundles (
    orderable_id, bundle_name, bundle_reduction, bundle_description,
    bundle_availability_start_date, bundle_availability_end_date
)
VALUES
    (7, 'Ah t''as faim', 15,
        '3 Galettes saucisses, 1 paquet de chips et une boisson',
        '2025-01-01', '2025-12-31'),

    (8, 'La totale', 20,
        'Un Bahn-Mi, un paquet de chips, un tiramisu et une boisson',
        '2025-01-01', '2025-12-31'),

    (9, 'Mejico', 20,
        'Une fajitas, 10 Cocas et un paquet de chips',
        '2025-01-01', '2025-12-31');


INSERT INTO project.Bundle_Items (bundle_id, item_id, item_quantity)
VALUES
    (1, 1, 3),
    (1, 6, 1), 
    (1, 3, 1),

    (2, 3, 1),  
    (2, 4, 1),  
    (2, 5, 1),
    (2, 6, 1),
 
    (3, 2, 1),  
    (3, 3, 10),  
    (3, 6, 1);  
