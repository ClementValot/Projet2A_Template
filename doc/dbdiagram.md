```mermaid
---
config:
  theme: default
title: UBEJR data model
---

classDiagram
   class Addresses {
        INT address_id PK
        INT address_number
        VARCHAR address_street
        VARCHAR address_city
        VARCHAR address_postal_code
        VARCHAR address_country
    }
    
    class Customers {
        INT customer_id PK
        VARCHAR customer_first_name
        VARCHAR customer_last_name
        TIMESTAMP customer_created_at
        VARCHAR customer_phone
        VARCHAR customer_mail
        VARCHAR customer_password_hash
        CHAR customer_salt
        INT customer_address_id FK
    }
    
    class Admins {
        INT admin_id PK
        VARCHAR username
        VARCHAR admin_first_name
        VARCHAR admin_last_name
        TIMESTAMP admin_created_at
        VARCHAR admin_password_hash
        CHAR admin_salt
    }
    
    class Drivers {
        INT driver_id PK
        VARCHAR driver_first_name
        VARCHAR driver_last_name
        TIMESTAMP driver_created_at
        VARCHAR driver_password_hash
        CHAR driver_salt
        BOOLEAN driver_is_delivering
        VARCHAR driver_phone
    }
    
    class Orders {
        INT order_id PK
        INT order_customer_id FK
        INT order_state
        DATE order_date
        TIME order_time
        BOOLEAN order_is_paid
        BOOLEAN order_is_prepared
    }
    
    class Items {
        INT item_id PK
        INT orderable_id FK
        VARCHAR item_name
        FLOAT item_price
        VARCHAR item_type
        VARCHAR item_description
        INT item_stock
    }
    
    class Bundles {
        INT bundle_id PK
        INT orderable_id FK
        VARCHAR bundle_name
        INT bundle_reduction
        VARCHAR bundle_description
        DATE bundle_availability_start_date
        DATE bundle_availability_end_date
    }
    
    class Bundle_Items {
        INT bundle_id FK
        INT item_id FK
        INT item_quantity
        PRIMARY KEY (bundle_id, item_id)
    }
    
    class Orderables {
        INT orderable_id PK
        VARCHAR orderable_type
        BOOLEAN is_in_menu
    }
    
    class Order_contents {
        INT order_id FK
        INT orderable_id FK
        INT orderable_quantity
        PRIMARY KEY (order_id, orderable_id)
    }
    
    class Deliveries {
        INT delivery_order_id FK
        INT delivery_driver_id FK
        INT delivery_state
        PRIMARY KEY (delivery_order_id, delivery_driver_id)
    }


    %% ============================
    %% Relationships
    %% ============================

    Customers "1" --> "1" Addresses : lives_at
    Orders "1" --> "1" Customers : placed_by
    Order_Contents "*" --> "1" Orders : belongs_to
    Order_Contents "*" --> "1" Orderables : includes
    Items "1" --> "1" Orderables : is_a
    Bundles "1" --> "1" Orderables : is_a
    Bundle_Items "*" --> "1" Bundles : contains
    Bundle_Items "*" --> "1" Items : includes
    Deliveries "*" --> "1" Orders : delivers
    Deliveries "*" --> "1" Drivers : handled_by
