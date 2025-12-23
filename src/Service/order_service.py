from datetime import datetime
from typing import List, Optional

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.customer import Customer
from src.Model.discounted_bundle import DiscountedBundle
from src.Model.one_item_bundle import OneItemBundle
from src.Model.order import Order
from src.Model.predefined_bundle import PredefinedBundle


class OrderService:
    def __init__(self, db_connector: DBConnector):
        """
        Initializes the service and injects dependencies into the DAOs.
        """
        self.item_dao = ItemDAO(db_connector=db_connector)
        self.user_dao = UserDAO(db_connector=db_connector)
        self.address_dao = AddressDAO(db_connector=db_connector)
        self.bundle_dao = BundleDAO(db_connector=db_connector, item_dao=self.item_dao)

        self.order_dao = OrderDAO(
            db_connector=db_connector,
            user_dao=self.user_dao,
            address_dao=self.address_dao,
            item_dao=self.item_dao,
            bundle_dao=self.bundle_dao,
        )

    def create_order(self, customer_id: int, address_id: int) -> Optional[Order]:
        customer = self.user_dao.find_user_by_id(customer_id)
        if not customer or not isinstance(customer, Customer):
            raise ValueError(f"No valid customer found with ID {customer_id}")

        address = self.address_dao.find_address_by_id(address_id)
        if not address:
            raise ValueError(f"No address found with ID {address_id}")

        new_order = Order(
            customer=customer,
            address=address,
            items=[],
            price=0.0,
            status="pending",
            order_date=datetime.now(),
        )

        created_order = self.order_dao.add_order(new_order)
        if not created_order:
            raise Exception("Failed to create the order in the database.")

        return created_order

    def cancel_order(self, order_id: int) -> bool:
        order = self.order_dao.find_order_by_id(order_id)
        if not order:
            raise ValueError(f"No order found with ID {order_id}.")
        return self.order_dao.delete_order(order_id)

    def find_order_by_id(self, order_id: int) -> Optional[Order]:
        order = self.order_dao.find_order_by_id(order_id)
        return order

    def add_bundle_to_order(
        self, order_id: int, bundle: PredefinedBundle | DiscountedBundle | OneItemBundle
    ) -> Optional[Order]:
        """
        Adds all items from a bundle to an existing 'pending' order.
        'bundle' can be a PredefinedBundle, DiscountedBundle, or OneItemBundle from the cart.
        """
        order = self.order_dao.find_order_by_id(order_id)
        if not order:
            raise ValueError(f"No order found with ID {order_id}.")
        if order.status != "pending":
            raise ValueError(f"Cannot modify an order with status '{order.status}'.")

        not_available = [item.name for item in bundle.composition if not item.availability]
        if not_available:
            raise ValueError(
                f"Bundle '{getattr(bundle, 'name', 'unknown')}' is unavailable because items {not_available} are not available."
            )

        for item in bundle.composition:
            order.items.append(item)

        order.price += bundle.compute_price()

        if not self.order_dao.update_order(order):
            raise Exception("Failed to update the order.")

        return self.order_dao.find_order_by_id(order_id)

    def validate_order(self, order_id: int) -> Optional[Order]:
        """
        Validate order: checks stock availability, updates stock, and sets status to 'validated'.
        """
        order = self.order_dao.find_order_by_id(order_id)
        if not order:
            raise ValueError(f"No order found with ID {order_id}.")
        if order.status != "pending":
            raise ValueError(f"Only 'pending' orders can be validated. Current status: '{order.status}'.")
        if not order.items:
            raise ValueError("Cannot validate an empty order.")

        items_needed = {}
        for item in order.items:
            items_needed[item.id_item] = items_needed.get(item.id_item, 0) + 1

        items_to_update = []
        for item_id, quantity_needed in items_needed.items():
            fresh_item = self.item_dao.find_item_by_id(item_id)
            if not fresh_item:
                raise Exception(f"Item ID {item_id} required for order no longer exists.")
            if fresh_item.stock < quantity_needed:
                raise ValueError(
                    f"Not enough stock for item '{fresh_item.name}'. Needed: {quantity_needed}, Available: {fresh_item.stock}."
                )
            fresh_item.stock -= quantity_needed
            if fresh_item.stock == 0:
                fresh_item.availability = False
            items_to_update.append(fresh_item)

        for item_to_update in items_to_update:
            if not self.item_dao.update_item(item_to_update):
                raise Exception(f"Failed to update stock for item {item_to_update.id_item}.")

        order.status = "validated"
        if not self.order_dao.update_order(order):
            raise Exception("Stock was updated, but failed to validate the order status.")

        return order

    def get_order_details(self, order_id: int) -> Optional[Order]:
        order = self.order_dao.find_order_by_id(order_id)
        if not order:
            raise ValueError(f"No order found with ID {order_id}.")
        return order

    def list_orders_for_customer(self, customer_id: int) -> List[Order]:
        customer = self.user_dao.find_user_by_id(customer_id)
        if not customer or not isinstance(customer, Customer):
            raise ValueError(f"No valid customer found with ID {customer_id}")
        return self.order_dao.find_orders_by_customer(customer_id)
