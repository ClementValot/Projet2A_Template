import logging
from typing import List, Optional

from src.DAO.DBConnector import DBConnector
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.delivery import Delivery
from src.Model.order import Order


class DeliveryDAO:
    db_connector: DBConnector
    user_dao: UserDAO
    order_dao: OrderDAO

    def __init__(self, db_connector: DBConnector, user_dao: UserDAO, order_dao: OrderDAO) -> None:
        self.db_connector = db_connector
        self.user_dao = user_dao
        self.order_dao = order_dao

    def find_delivery_by_id(self, id_delivery: int) -> Optional[Delivery]:
        """Find a delivery by its ID.

        Args:
            id_delivery: The ID of the delivery to find.

        Returns:
            Delivery object if found, None otherwise.
        """
        try:
            raw_delivery = self.db_connector.sql_query(
                "SELECT * FROM delivery WHERE id_delivery = %(id_delivery)s", {"id_delivery": id_delivery}, "one"
            )
            if raw_delivery is None:
                return None

            driver = None
            if raw_delivery["id_driver"] is not None:
                driver = self.user_dao.find_user_by_id(raw_delivery["id_driver"])

            raw_order_ids = self.db_connector.sql_query(
                "SELECT id_order FROM delivery_order WHERE id_delivery = %(id_delivery)s",
                {"id_delivery": id_delivery},
                "all",
            )

            orders = []
            for order_data in raw_order_ids:
                order = self.order_dao.find_order_by_id(order_data["id_order"])
                if order:
                    orders.append(order)

            return Delivery(
                id_delivery=raw_delivery["id_delivery"],
                driver=driver,
                orders=orders,
                status=raw_delivery["status"],
                delivery_time=raw_delivery["delivery_time"],
            )
        except Exception as e:
            logging.error(f"Failed to fetch delivery {id_delivery}: {e}")
            return None

    def find_all_deliveries(self) -> List[Delivery]:
        """Returns a list of all Delivery objects from the database.

        Returns:
            List[Delivery]: A list of Delivery objects (empty if no deliveries exist).
        """
        try:
            raw_deliveries = self.db_connector.sql_query("SELECT * FROM delivery", {}, "all")

            deliveries = []
            for delivery_data in raw_deliveries:
                driver = None
                if delivery_data["id_driver"] is not None:
                    driver = self.user_dao.find_user_by_id(delivery_data["id_driver"])

                raw_order_ids = self.db_connector.sql_query(
                    """
                    SELECT id_order 
                    FROM delivery_order 
                    WHERE id_delivery = %(id_delivery)s
                    """,
                    {"id_delivery": delivery_data["id_delivery"]},
                    "all",
                )

                orders = []
                for order_data in raw_order_ids:
                    order = self.order_dao.find_order_by_id(order_data["id_order"])
                    if order:
                        orders.append(order)

                deliveries.append(
                    Delivery(
                        id_delivery=delivery_data["id_delivery"],
                        driver=driver,
                        orders=orders,
                        status=delivery_data["status"],
                        delivery_time=delivery_data["delivery_time"],
                    )
                )

            return deliveries
        except Exception as e:
            logging.error(f"Failed to fetch all deliveries: {e}")
            return []

    def find_in_progress_deliveries_by_driver(self, driver_id: int) -> List[Delivery]:
        """Retrieve all deliveries assigned to a given driver
        that are currently 'in_progress'.
        Args:
            driver_id (int): The driver's ID.

        Returns:
            List[Delivery]: A list of deliveries in progress for that driver.
        """
        try:
            raw_deliveries = self.db_connector.sql_query(
                """
                SELECT *
                FROM delivery
                WHERE id_driver = %(driver_id)s
                AND status = 'in_progress';
                """,
                {"driver_id": driver_id},
                "all",
            )

            deliveries = []
            for raw_delivery in raw_deliveries:
                delivery = self.find_delivery_by_id(raw_delivery["id_delivery"])
                if delivery:
                    deliveries.append(delivery)

            return deliveries

        except Exception as e:
            logging.error(f"Failed to fetch in-progress deliveries for driver {driver_id}: {e}")
            return []

    def update_delivery(self, delivery: Delivery) -> bool:
        """Update an existing delivery.

        Args:
            delivery: The Delivery object with updated information.

        Returns:
            bool: True if update succeeded, False otherwise.
        """
        try:
            id_driver = delivery.driver.id_user

            res = self.db_connector.sql_query(
                """
                UPDATE delivery
                SET id_driver = %(id_driver)s,
                    status = %(status)s,
                    delivery_time = %(delivery_time)s
                WHERE id_delivery = %(id_delivery)s
                RETURNING id_delivery;
                """,
                {
                    "id_delivery": delivery.id_delivery,
                    "id_driver": id_driver,
                    "status": delivery.status,
                    "delivery_time": delivery.delivery_time,
                },
                "one",
            )
            return res is not None
        except Exception as e:
            logging.error(f"Failed to update delivery {delivery.id_delivery}: {e}")
            return False

    def add_delivery(self, delivery: Delivery) -> Optional[Delivery]:
        """Add a new delivery to the database.

        Args:
            delivery: The Delivery object to add.

        Returns:
            Delivery: The created delivery with its ID, or None if failed.
        """
        try:
            id_driver = delivery.driver.id_user

            raw_created_delivery = self.db_connector.sql_query(
                """
                INSERT INTO delivery (id_driver, status, delivery_time)
                VALUES (%(id_driver)s, %(status)s, %(delivery_time)s)
                RETURNING *;
                """,
                {"id_driver": id_driver, "status": delivery.status, "delivery_time": delivery.delivery_time},
                "one",
            )

            id_delivery = raw_created_delivery["id_delivery"]

            for order in delivery.orders:
                order_id = order.id_order if hasattr(order, "id_order") else order
                self.db_connector.sql_query(
                    """
                    INSERT INTO delivery_order (id_delivery, id_order)
                    VALUES (%(id_delivery)s, %(id_order)s)
                    """,
                    {"id_delivery": id_delivery, "id_order": order_id},
                    None,
                )

            return self.find_delivery_by_id(id_delivery)
        except Exception as e:
            logging.error(f"Failed to add delivery: {e}")
            return None

    def delete_delivery(self, id_delivery: int) -> bool:
        """Delete a delivery from the database.

        Args:
            id_delivery: The ID of the delivery to delete.

        Returns:
            bool: True if the deletion succeeded, False otherwise.
        """
        try:
            self.db_connector.sql_query(
                "DELETE FROM delivery_order WHERE id_delivery = %(id_delivery)s", {"id_delivery": id_delivery}, None
            )

            res = self.db_connector.sql_query(
                "DELETE FROM delivery WHERE id_delivery = %(id_delivery)s RETURNING id_delivery;",
                {"id_delivery": id_delivery},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.error(f"Failed to delete delivery {id_delivery}: {e}")
            return False
