import logging
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.DAO.userDAO import UserDAO
from src.Model.order import Order


class OrderDAO(BaseModel):
    db_connector: DBConnector
    item_dao: ItemDAO
    user_dao: UserDAO
    address_dao: AddressDAO
    bundle_dao: BundleDAO

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def find_order_by_id(self, id_order: int) -> Optional[Order]:
        """Find an order by its ID.

        Args:
            id_order: The ID of the order to find.

        Returns:
            Order object if found, None otherwise.
        """
        try:
            raw_order = self.db_connector.sql_query(
                'SELECT * FROM "order" WHERE id_order = %(id_order)s',
                {"id_order": id_order},
                "one",
            )
            if raw_order is None:
                return None

            customer = None
            if raw_order["id_user"] is not None:
                customer = self.user_dao.find_user_by_id(raw_order["id_user"])

            address = None
            if raw_order["id_address"] is not None:
                address = self.address_dao.find_address_by_id(raw_order["id_address"])

            raw_items = self.db_connector.sql_query(
                """
                SELECT i.*
                FROM item i
                JOIN order_item oi ON i.id_item = oi.id_item
                WHERE oi.id_order = %(id_order)s
                """,
                {"id_order": id_order},
                "all",
            )

            items = []
            for item_data in raw_items:
                item = self.item_dao.find_item_by_id(item_data["id_item"])
                if item:
                    items.append(item)

            return Order(
                id_order=raw_order["id_order"],
                customer=customer,
                address=address,
                items=items,
                status=raw_order["status"],
                price=raw_order["price"],
                order_date=raw_order["order_date"],
            )
        except Exception as e:
            logging.error(f"Failed to fetch order {id_order}: {e}")
            return None

    def find_all_orders(self) -> List[Order]:
        """Returns a list of all Order objects from the database.

        Returns:
            List[Order]: A list of Order objects (empty if no orders exist).
        """
        try:
            raw_orders = self.db_connector.sql_query('SELECT * FROM "order"', {}, "all")

            orders = []
            for order_data in raw_orders:
                order = self.find_order_by_id(order_data["id_order"])
                if order:
                    orders.append(order)

            return orders
        except Exception as e:
            logging.error(f"Failed to fetch all orders: {e}")
            return []

    def find_orders_by_customer(self, id_user: int) -> List[Order]:
        """Find all orders for a specific customer.

        Args:
            id_user: The ID of the customer.

        Returns:
            List[Order]: List of orders for this customer.
        """
        try:
            raw_orders = self.db_connector.sql_query(
                'SELECT * FROM "order" WHERE id_user = %(id_user)s',
                {"id_user": id_user},
                "all",
            )

            orders = []
            for order_data in raw_orders:
                order = self.find_order_by_id(order_data["id_order"])
                if order:
                    orders.append(order)

            return orders
        except Exception as e:
            logging.error(f"Failed to fetch orders for customer {id_user}: {e}")
            return []

    def add_order(self, order: Order) -> Optional[Order]:
        """Add a new order to the database.

        Args:
            order: The Order object to add.

        Returns:
            Order: The created order with its ID, or None if failed.
        """
        try:
            id_user = order.customer.id_user if hasattr(order.customer, "id_user") else order.customer
            id_address = order.address.id_address if hasattr(order.address, "id_address") else order.address

            raw_created_order = self.db_connector.sql_query(
                """
                INSERT INTO "order" (id_user, status, price, id_address, order_date)
                VALUES (%(id_user)s, %(status)s, %(price)s, %(id_address)s, %(order_date)s)
                RETURNING *;
                """,
                {
                    "id_user": id_user,
                    "status": order.status,
                    "price": order.price,
                    "id_address": id_address,
                    "order_date": order.order_date if hasattr(order, "order_date") else datetime.now(),
                },
                "one",
            )

            id_order = raw_created_order["id_order"]

            for item in order.items:
                self.db_connector.sql_query(
                    """
                    INSERT INTO order_item (id_order, id_item)
                    VALUES (%(id_order)s, %(id_item)s)
                    """,
                    {
                        "id_order": id_order,
                        "id_item": item.id_item,
                    },
                    None,
                )

            return self.find_order_by_id(id_order)
        except Exception as e:
            logging.error(f"Failed to add order: {e}")
            return None

    def update_order(self, order: Order) -> bool:
        """Update an existing order.

        Args:
            order: The Order object with updated information.

        Returns:
            bool: True if update succeeded, False otherwise.
        """
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE "order"
                SET id_user = %(id_user)s,
                    status = %(status)s,
                    price = %(price)s,
                    id_address = %(id_address)s,
                    order_date = %(order_date)s
                WHERE id_order = %(id_order)s
                RETURNING id_order;
                """,
                {
                    "id_order": order.id_order,
                    "id_user": order.customer.id_user,
                    "status": order.status,
                    "price": order.price,
                    "id_address": order.address.id_address,
                    "order_date": order.order_date,
                },
                "one",
            )

            self.db_connector.sql_query(
                "DELETE FROM order_item WHERE id_order = %(id_order)s",
                {"id_order": order.id_order},
                None,
            )

            for item in order.items:
                self.db_connector.sql_query(
                """
                INSERT INTO order_item (id_order, id_item, quantity)
                    VALUES (%(id_order)s, %(id_item)s, 1)
                    ON CONFLICT (id_order, id_item)
                    DO UPDATE SET quantity = order_item.quantity + 1
                    """,
                    {
                        "id_order": order.id_order,
                        "id_item": item.id_item,
                    },
                    None,
                )

            return res is not None
        except Exception as e:
            logging.error(f"Failed to update order {order.id_order}: {e}")
            return False

    def delete_order(self, id_order: int) -> bool:
        """Delete an order from the database.

        Args:
            id_order: The ID of the order to delete.

        Returns:
            bool: True if the deletion succeeded, False otherwise.
        """
        try:
            self.db_connector.sql_query(
                "DELETE FROM order_item WHERE id_order = %(id_order)s",
                {"id_order": id_order},
                None,
            )

            self.db_connector.sql_query(
                "DELETE FROM delivery_order WHERE id_order = %(id_order)s",
                {"id_order": id_order},
                None,
            )

            res = self.db_connector.sql_query(
                'DELETE FROM "order" WHERE id_order = %(id_order)s RETURNING id_order;',
                {"id_order": id_order},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.error(f"Failed to delete order {id_order}: {e}")
            return False
