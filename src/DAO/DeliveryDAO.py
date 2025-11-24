from typing import Optional

from src.Model.Delivery import Delivery
from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from .DBConnector import DBConnector


class DeliveryDAO(metaclass=Singleton):
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector) -> None:
        self.db_connector = db_connector

    @log
    def create_delivery(self, order_id: int, driver_id: int) -> Delivery:
        raw_created_delivery = self.db_connector.sql_query(
            """
            INSERT INTO Deliveries (delivery_order_id, delivery_driver_id, delivery_state)
            VALUES (%(order_id)s, %(driver_id)s, DEFAULT)
            RETURNING *;
            """,
            {"order_id": order_id, "driver_id": driver_id},
            "one",
        )
        return Delivery(**raw_created_delivery)

    @log
    def get_deliveries_by_driver(self, delivery_id_driver: int) -> Optional[Delivery]:
        raw_deliveries = self.db_connector.sql_query(
            """SELECT *
               FROM Deliveries
               WHERE delivery_driver_id=%s
               ORDER BY delivery_created_at DESC
            """,
            [delivery_id_driver],
            "all",
        )
        if raw_deliveries is None:
            return []
        return [Delivery(**raw_delivery) for raw_delivery in raw_deliveries]

    @log
    def get_driver_current_delivery(self, delivery_id_driver: int) -> Optional[Delivery]:
        raw_delivery = self.db_connector.sql_query(
            """SELECT *
               FROM Deliveries
                WHERE delivery_driver_id=%s
                AND delivery_state=1;
            """,
            [delivery_id_driver],
            "one",
        )
        if raw_delivery is None:
            return None
        return Delivery(**raw_delivery)

    @log
    def get_delivery_by_user(self, customer_id: int) -> Optional[Delivery]:
        raw_delivery = self.db_connector.sql_query(
            """SELECT d.*
            FROM Deliveries AS d
            INNER JOIN Orders AS o ON d.delivery_order_id = o.order_id
            WHERE order_customer_id=%s
            """,
            [customer_id],
            "one",
        )

        return Delivery(**raw_delivery) if raw_delivery else None

    @log
    def get_delivery_by_order_id(self, order_id: int) -> Optional[Delivery]:
        raw_delivery = self.db_connector.sql_query(
            """SELECT *
            FROM Deliveries AS d
            WHERE delivery_order_id=%s
            """,
            [order_id],
            "one",
        )
        if raw_delivery is None:
            return None
        return Delivery(**raw_delivery)

    @log
    def update_delivery_state(self, delivery_id: int, state: int) -> Delivery:
        if state not in (0, 1, 2):
            raise ValueError("State can only take 1, 2 or 3 as value.")
        raw_update_delivery = self.db_connector.sql_query(
            """
            UPDATE Deliveries SET delivery_state=%(state)s
            WHERE delivery_order_id=%(delivery_id)s RETURNING *;
            """,
            {"state": state, "delivery_id": delivery_id},
            "one",
        )
        return Delivery(**raw_update_delivery)

    @log
    def change_driver(self, delivery_id: int, driver_id: int) -> Delivery:
        raw_update_delivery = self.db_connector.sql_query(
            """
            UPDATE Deliveries SET delivery_driver_id=%(driver_id)s
            WHERE delivery_driver_id=%(delivery_id)s RETURNING *;
            """,
            {"driver_id": driver_id, "delivery_id": delivery_id},
            "one",
        )
        return Delivery(**raw_update_delivery)

    @log
    def delete_delivery(self, delivery_id: int) -> None:
        raw_delete_delivery = self.db_connector.sql_query(
            """
            DELETE FROM Deliveries WHERE delivery_order_id=%s RETURNING *;
            """,
            [delivery_id],
            "one",
        )
        return Delivery(**raw_delete_delivery)
