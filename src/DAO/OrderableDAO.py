from typing import Dict, List, Optional

from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from .DBConnector import DBConnector


class OrderableDAO(metaclass=Singleton):
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    # CREATE
    @log
    def create_orderable(
        self,
        orderable_type: str,
        orderable_name: str,
        orderable_image_url: Optional[str] = None,
        is_in_menu: bool = False,
    ) -> int:
        """
        Create an orderable

        Return
        ------
        int:
            The orderable_id of the created instance
        """

        if orderable_image_url:
            orderable_image_name = (
                f"image_{orderable_type}_{orderable_name.lower().replace(' ', '_')}"
            )
        else:
            orderable_image_name = None
        result = self.db_connector.sql_query(
            """
            INSERT INTO Orderables (orderable_type, orderable_image_name,
                                    orderable_image_url, is_in_menu)
            VALUES (%(orderable_type)s, %(orderable_image_name)s,
                    %(orderable_image_url)s, %(is_in_menu)s)
            RETURNING orderable_id;
            """,
            {
                "orderable_type": orderable_type,
                "is_in_menu": is_in_menu,
                "orderable_image_name": orderable_image_name,
                "orderable_image_url": orderable_image_url,
            },
            "one",
        )
        return result["orderable_id"]

    @log
    def get_orderable_by_id(self, orderable_id: int) -> Optional[Dict]:
        raw_orderable = self.db_connector.sql_query(
            "SELECT * FROM Orderables WHERE orderable_id=%s;", [orderable_id], "one"
        )
        return raw_orderable if raw_orderable else None

    @log
    def get_all_orderables(self) -> List[Dict]:
        raw_orderables = self.db_connector.sql_query(
            """SELECT *
            FROM Orderables
            ORDER BY (is_in_menu is True) DESC
            """,
            return_type="all",
        )
        if not raw_orderables:
            return []

        return raw_orderables

    @log
    def update_orderable_state(self, orderable_id: int, is_in_menu: bool) -> Dict:
        raw_orderable = self.db_connector.sql_query(
            """UPDATE Orderables
            SET is_in_menu = %(is_in_menu)s
            WHERE orderable_id = %(orderable_id)s
            RETURNING *;""",
            {"is_in_menu": is_in_menu, "orderable_id": orderable_id},
            "one",
        )
        return raw_orderable

    @log
    def get_image_from_orderable(self, orderable_id: int) -> bytes:
        raw_orderable = self.db_connector.sql_query(
            "SELECT * FROM Orderables WHERE orderable_id=%s;", [orderable_id], "one"
        )
        return raw_orderable["orderable_image_url"] if raw_orderable else None

    @log
    def update_image(
        self,
        orderable_id: int,
        orderable_type: str,
        orderable_name: str,
        orderable_image_url: str,
    ) -> Dict:
        orderable_image_name = f"image_{orderable_type}_{orderable_name.lower().replace(' ', '_')}"

        raw_orderable = self.db_connector.sql_query(
            """UPDATE Orderables
            SET orderable_image_name = %(orderable_image_name)s,
                orderable_image_url = %(orderable_image_url)s
            WHERE orderable_id = %(orderable_id)s
            RETURNING *;""",
            {
                "orderable_image_name": orderable_image_name,
                "orderable_image_url": orderable_image_url,
                "orderable_id": orderable_id,
            },
            "one",
        )
        return raw_orderable

    @log
    def delete_orderable(self, orderable_id: int) -> None:
        self.db_connector.sql_query(
            "DELETE FROM Orderables WHERE orderable_id = %(orderable_id)s",
            {"orderable_id": orderable_id},
            None,
        )

    def _is_in_menu(self, orderable_id: int) -> bool:
        raw_orderable = self.db_connector.sql_query(
            "SELECT is_in_menu FROM Orderables WHERE orderable_id=%s;", [orderable_id], "one"
        )
        return raw_orderable["is_in_menu"] if raw_orderable else None

    def get_info_from_orderable(self, orderable_id: int) -> Dict:
        raw_infos = {}
        raw_infos["is_in_menu"] = self._is_in_menu(orderable_id)
        raw_infos["orderable_image_url"] = self.get_image_from_orderable(orderable_id)
        raw_infos["orderable_image_name"] = self.db_connector.sql_query(
            "SELECT orderable_image_name FROM Orderables WHERE orderable_id=%s;",
            [orderable_id],
            "one",
        )["orderable_image_name"]
        return raw_infos

    @log
    def get_number_orderables(self) -> int:
        count_orderables = self.db_connector.sql_query(
            """
            SELECT COUNT(*)
            FROM Orderables;
            """,
            return_type="one",
        )
        return count_orderables["count"]
