from datetime import datetime
from typing import Dict, List, Literal, Optional, Union

from src.Model.Bundle import Bundle
from src.Model.Item import Item
from src.Model.Order import Order, OrderState
from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from .BundleDAO import BundleDAO
from .DBConnector import DBConnector
from .ItemDAO import ItemDAO
from .OrderableDAO import OrderableDAO


class OrderDAO(metaclass=Singleton):
    db_connector: DBConnector
    orderable_dao: OrderableDAO
    item_dao: ItemDAO
    bundle_dao: BundleDAO

    def __init__(
        self,
        db_connector: DBConnector,
        orderable_dao: OrderableDAO,
        item_dao: ItemDAO,
        bundle_dao: BundleDAO,
    ) -> None:
        self.db_connector = db_connector
        self.orderable_dao = orderable_dao
        self.item_dao = item_dao
        self.bundle_dao = bundle_dao

    # CREATE
    @log
    def create_order(self, customer_id: int) -> Order:
        raw_order = self.db_connector.sql_query(
            """
            INSERT INTO Orders (order_id,
                               order_customer_id,
                               order_state,
                               order_created_at,
                               order_paid_at)
            VALUES (DEFAULT,
                    %(customer_id)s,
                    0,
                    %(order_date)s,
                    DEFAULT)
            RETURNING *;
            """,
            {
                "customer_id": customer_id,
                "order_date": datetime.now(),
            },
            "one",
        )

        raw_order["order_orderables"] = {}
        return Order(**raw_order)

    # READ
    @log
    def get_order_by_id(self, order_id: int) -> Optional[Order]:
        raw_order = self.db_connector.sql_query(
            """SELECT *
               FROM Orders
               WHERE order_id=%s""",
            [order_id],
            "one",
        )

        if raw_order is None:
            return None

        raw_order["order_orderables"] = self._get_orderables_in_order(order_id)
        return Order(**raw_order)

    @log
    def get_all_orders(self, limit: int) -> Optional[List[Order]]:
        raw_orders = self.db_connector.sql_query(
            "SELECT * from Orders ORDER BY order_created_at DESC LIMIT %s ;", [limit], "all"
        )

        if not raw_orders:
            return []

        Orders = []
        for raw_order in raw_orders:
            raw_order["order_orderables"] = self._get_orderables_in_order(raw_order["order_id"])
            Orders.append(Order(**raw_order))

        return Orders

    @log
    def get_all_orders_by_customer(self, customer_id: int) -> Optional[List[Order]]:
        raw_orders = self.db_connector.sql_query(
            "SELECT * FROM Orders WHERE order_customer_id=%s  ORDER BY order_created_at DESC",
            [customer_id],
            "all",
        )

        if not raw_orders:
            return []

        Orders = []
        for raw_order in raw_orders:
            raw_order["order_orderables"] = self._get_orderables_in_order(raw_order["order_id"])
            Orders.append(Order(**raw_order))

        return Orders

    @log
    def get_customer_current_order(self, customer_id: int) -> Optional[Order]:
        raw_order = self.db_connector.sql_query(
            """SELECT * from Orders
               WHERE order_customer_id=%s
               AND order_state NOT IN (4, 5)
               ORDER BY order_paid_at DESC
               LIMIT 1;
            """,
            [customer_id],
            "one",
        )
        if raw_order is None:
            return None

        raw_order["order_orderables"] = self._get_orderables_in_order(raw_order["order_id"])
        return Order(**raw_order)

    @log
    def get_orders_by_state(
        self, state: int, order_by: Literal["DESC", "ASC"] = "DESC"
    ) -> List[Order]:
        if order_by == "DESC":
            raw_orders = self.db_connector.sql_query(
                """SELECT * FROM Orders
                    WHERE order_state = %s
                    ORDER BY order_created_at DESC;
                """,
                [state],
                "all",
            )
        if order_by == "ASC":
            raw_orders = self.db_connector.sql_query(
                """SELECT * FROM Orders
                    WHERE order_state = %s
                    ORDER BY order_created_at ASC;
                """,
                [state],
                "all",
            )

        if not raw_orders:
            return []

        Orders = []
        for raw_order in raw_orders:
            raw_order["order_orderables"] = self._get_orderables_in_order(raw_order["order_id"])
            Orders.append(Order(**raw_order))

        return Orders

    @log
    def get_actives_orders(self) -> List[Order]:
        raw_orders = self.db_connector.sql_query(
            """SELECT * FROM Orders
                    WHERE order_state IN (0, 1, 2, 3)
                    ORDER BY order_paid_at DESC;
                """,
            return_type="all",
        )

        if not raw_orders:
            return []

        Orders = []
        for raw_order in raw_orders:
            raw_order["order_orderables"] = self._get_orderables_in_order(raw_order["order_id"])
            Orders.append(Order(**raw_order))

        return Orders

    # UPDATE
    @log
    def update_order_state(self, order_id: int, new_state: int) -> Order:
        self.db_connector.sql_query(
            """
            UPDATE Orders
            SET order_state = %(new_state)s
            WHERE order_id = %(order_id)s;
            """,
            {"new_state": new_state, "order_id": order_id},
            "none",
        )
        if new_state == OrderState.PAID.value:
            self.db_connector.sql_query(
                """
                UPDATE Orders
                SET order_paid_at = %(timestamp)s
                WHERE order_id = %(order_id)s;
                """,
                {"timestamp": datetime.now(), "order_id": order_id},
                "none",
            )

        return self.get_order_by_id(order_id)

    # DELETE
    @log
    def delete_order(self, order_id) -> None:
        self.db_connector.sql_query(
            """
            DELETE FROM Order_contents WHERE order_id=%s;
            """,
            [order_id],
            "none",
        )
        self.db_connector.sql_query(
            """
            DELETE FROM Orders WHERE order_id=%s;
            """,
            [order_id],
            "none",
        )
        return None

    @log
    def add_orderable_to_order(self, order_id: int, orderable_id: int, quantity: int = 1) -> Order:
        if self.get_quantity_of_orderables(order_id, orderable_id) >= 1:
            self.db_connector.sql_query(
                """UPDATE Order_contents
                   SET orderable_quantity=orderable_quantity+%(quantity)s
                   WHERE order_id=%(order_id)s AND orderable_id=%(orderable_id)s;
                """,
                {"quantity": quantity, "order_id": order_id, "orderable_id": orderable_id},
                "none",
            )

        else:
            self.db_connector.sql_query(
                """INSERT INTO Order_contents
                   VALUES (%(order_id)s, %(orderable_id)s, %(quantity)s);
                """,
                {"order_id": order_id, "orderable_id": orderable_id, "quantity": quantity},
                "none",
            )

        return self.get_order_by_id(order_id)

    @log
    def remove_orderable_from_order(
        self, order_id: int, orderable_id: int, quantity: int = 1
    ) -> Order:
        # si getquantity < quantity a delete : balancer une erreur  > fait par le service
        if self.get_quantity_of_orderables(order_id, orderable_id) == quantity:
            self.db_connector.sql_query(
                """DELETE FROM Order_contents
                   WHERE order_id=%(order_id)s AND orderable_id=%(orderable_id)s;
                """,
                {"order_id": order_id, "orderable_id": orderable_id},
                "none",
            )
        else:
            self.db_connector.sql_query(
                """UPDATE Order_contents
                   SET orderable_quantity=orderable_quantity-%(quantity)s
                   WHERE order_id=%(order_id)s AND orderable_id=%(orderable_id)s;
                """,
                {"quantity": quantity, "order_id": order_id, "orderable_id": orderable_id},
                "none",
            )

        return self.get_order_by_id(order_id)

    def get_quantity_of_orderables(self, order_id: int, orderable_id: int) -> int:
        result = self.db_connector.sql_query(
            """SELECT orderable_quantity
               FROM Order_contents
               WHERE order_id=%(order_id)s AND orderable_id=%(orderable_id)s;
            """,
            {"order_id": order_id, "orderable_id": orderable_id},
            "one",
        )
        if result is None:
            return 0

        return result["orderable_quantity"]

    def _get_orderables_in_order(self, order_id: int) -> Dict[Union[Item, Bundle], int]:
        raw_orderables = self.db_connector.sql_query(
            """
            SELECT oc.orderable_id, oc.orderable_quantity, o.orderable_type
            FROM Order_contents AS oc
            JOIN Orderables AS o ON oc.orderable_id = o.orderable_id
            WHERE oc.order_id = %s
            """,
            [order_id],
            "all",
        )
        if not raw_orderables:
            return {}

        products_dict = {}
        for raw in raw_orderables:
            orderable_id = raw["orderable_id"]
            quantity = raw["orderable_quantity"]
            orderable_type = raw["orderable_type"]

            if orderable_type == "item":
                product = self.item_dao.get_item_by_orderable_id(orderable_id)
            elif orderable_type == "bundle":
                product = self.bundle_dao.get_bundle_by_orderable_id(orderable_id)

            if product:
                products_dict[product] = quantity

        return products_dict

    @log
    def get_benef(self) -> float:
        raw_orders = self.db_connector.sql_query(
            """
            SELECT o.order_id
            FROM Orders AS o
            WHERE o.order_paid_at IS NOT NULL;
            """,
            return_type="all",
        )
        benef = 0
        for raw_order in raw_orders:
            order = self.get_order_by_id(raw_order["order_id"])
            benef += order.order_price

        return round(benef, 2)

    @log
    def get_number_orders_by_state(self) -> Dict[str, int]:
        count_orders = self.db_connector.sql_query(
            """
            SELECT COUNT(*), o.order_state
            FROM Orders AS o
            GROUP BY o.order_state
            """,
            return_type="all",
        )

        merged_count = {k: v for d in count_orders for k, v in d.items()}

        order_count = {}
        order_count["preparing"] = merged_count.get(1, 0)
        order_count["ready_to_deliver"] = merged_count.get(2, 0)

        return order_count
