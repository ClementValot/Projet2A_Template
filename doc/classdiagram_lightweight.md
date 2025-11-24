```mermaid
---
config:
  theme: default
title: UBEJR light class diagram
---

classDiagram
namespace Business_Objects {
    class Address {
        +address_id: int
        +address_number: int
        +address_street: str
        +address_city: str
        +address_postal_code: int
        +address_country: str
    }

    class User {
        +id: int
        +first_name: str
        +last_name: str
        +created_at: datetime
        +password: str
        +salt: str
        +user_role: Literal["admin", "customer", "driver"] = "customer"
    }
    class Admin {
        +username: str
    }

    class Customer {
        +customer_address: Address
        +customer_phone: str
        +customer_mail: str
    }

    class Driver {
        +driver_phone: str
        +driver_is_delivering: bool = False
    }

    class Orderable {
        +orderable_id: int
        +orderable_type: Literal["item", "bundle"]
        +orderable_image_data: Optional[bytes] = None
        +is_in_menu: bool = False
    }

    class Item {
        +item_id: int
        +orderable_id: int
        +item_name: str
        +item_price: float > 0 
        +item_type: Literal["Starter", "Main course", "Dessert", "Side dish", "Drink"]
        +item_description: str
        +item_stock: int >= 0

    }

    class Bundle {
        +bundle_id: int
        +orderable_id: int
        +bundle_name: str
        +bundle_reduction: int
        +bundle_description: str
        +bundle_availability_start_date: datetime
        +bundle_availability_end_date: datetime
        +bundle_items: Dict[Item, int]

    }

    class Order {
        +order_id: int
        +order_customer_id: int
        +order_state: OrderState = OrderState.PENDING
        +order_created_at: datetime
        +order_paid_at: Optional[datetime] = None
        +order_orderables: Dict[Union[Bundle, Item], int]

    }

    class Delivery {
        +delivery_order_id: int
        +delivery_driver_id: int
        +delivery_created_at: datetime
        +delivery_state: Optional[int] = None
    }
}

namespace DAO_Layer {
    class AddressDAO {
        +create_address(address_number: int, address_street: str, address_city: str, address_postal_code: int, address_country: str) : Address
        +get_address_by_customer_id(customer_id: int): Optional[Address]
        +update_address(address_id: int, update: dict): Optional[Address]
        +delete_address_by_id(address_id: int): None
    }

    class CustomerDAO {
        +create_customer(first_name: str, last_name: str, phone: str, mail: str, password_hash: str, salt: str, address_id: int): Customer
        +get_customer_by_email(mail: str) : Optional[Customer]
        +update_customer(customer_id: int, update: dict): Optional[Customer]
        +delete_customer(customer_id: int):None

    }
    class DriverDAO {
        +create_driver(first_name: str, last_name: str, phone: str, password_hash: str, salt: str) : Driver:
        *get_driver_by_id(driver_id: int) : Optional[Driver]:
        *get_driver_by_phone(phone_number: str) : Optional[Driver]:
        *update_driver(driver_id: int, update: dict):
        *delete_driver(driver_id: int): None
    }

    class ItemDAO {
        +create_item(item_name: str, item_price: float, item_type: str, item_description: str, item_stock: int, item_image: Optional[bytes] = None, is_in_menu: bool = False) : Item:
        +get_item_by_id(item_id: int) : Optional[Item]:
        +update_item(item_id: int, update: dict) : Item:
        +delete_item_by_id(item_id: int) : None

    }


    class OrderDAO {
        +create_order(customer_id: int): Order
        +get_order_by_id(order_id: int): Optional[Order]
        +get_all_orders(limit: int): Optional[List[Order]]
        +get_all_orders_by_customer(customer_id: int): Optional[List[Order]]
        +get_customer_current_order(customer_id: int): Optional[Order]
        +get_orders_by_state(state: int, order_by: Literal["DESC", "ASC"] = "DESC"): List[Order]
        +get_actives_orders(self): List[Order]
        +update_order_state(order_id: int, new_state: int): Order

    }

}
namespace Controller_Layer {
    class CustomerController {

    }

    class DriverController {

    }
}

namespace Service_Layer {
    class AddressService {

    }

    class CustomerService {
        login_customer(identifier: str, password: str) : Customer:
        update_address(customer_id: int, update: dict) : Customer:
    }

    class DriverService {
        start_delivery(order_id: int, driver_id: int) : Delivery:
        end_delivery(order_id: int, driver_id: int) : Delivery:
    }



    class ItemService {

    }

 

    class GoogleMapService {
        get_path(destination: str) : str:
        extract_components(address: str) : Dict[str, Union[str, int]]:
        validate_address(address: str) : bool:
    }

    class OrderService {
        mark_as_paid(order_id: int) : Order:
        mark_as_prepared(order_id: int) : Order:
    }

    class StripeService {
        create_checkout_session(order: Order, customer_mail: str) : Dict:
        verify_payment(session_id: int) : Dict:
    }
}
namespace External_APIs {
    class GoogleMapAPI {

        }
    class StripeAPI {

        }
    }






    %% ============================
    %% Relationships
    %% ============================

    Admin --|> User : "inherits from"
    Customer --|> User : "inherits from"
    Driver --|> User : "inherits from"
    Address --|> Customer : "belongs to"

    Item --|> Orderable : "inherits from"
    Bundle --|> Orderable : "inherits from"
    Orderable --|>Order :"is in"
    Order --|> Customer :"ordered by"
    Order --|> Delivery :"handled by"
    Driver --|> Delivery: "handles"

    Address --|> AddressService: "handled by"
    Customer --|> CustomerService: "handled by"
    Driver --|> DriverService: "handled by"

    CustomerService ..> CustomerDAO : "uses"
    DriverService ..> DriverDAO : "uses"
    AddressService ..> AddressDAO: "uses"
    ItemService ..> ItemDAO: "uses"
    OrderService ..> OrderDAO: "uses"

    StripeService ..> StripeAPI: "calls"
    GoogleMapService ..> GoogleMapAPI:"calls"

    DriverController ..> DriverService : "transmits inputs to"
    CustomerController ..> CustomerService : "transmits inputs to"


