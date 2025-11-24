from datetime import datetime
from typing import Dict, List, Optional

from src.Model.Bundle import Bundle
from src.Model.Item import Item
from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from .DBConnector import DBConnector
from .ItemDAO import ItemDAO
from .OrderableDAO import OrderableDAO


class BundleDAO(metaclass=Singleton):
    db_connector: DBConnector
    orderable_dao: OrderableDAO
    item_dao: ItemDAO

    def __init__(self, db_connector: DBConnector, orderable_dao: OrderableDAO, item_dao: ItemDAO):
        self.db_connector = db_connector
        self.orderable_dao = orderable_dao
        self.item_dao = item_dao

    # CREATE
    @log
    def create_bundle(
        self,
        bundle_name: str,
        bundle_reduction: int,
        bundle_description: str,
        bundle_availability_start_date: datetime,
        bundle_availability_end_date: datetime,
        bundle_items: Dict[Item, int],
        bundle_image: Optional[str] = None,
        is_in_menu: bool = False,
    ):
        orderable_id = self.orderable_dao.create_orderable(
            "bundle", bundle_name, bundle_image, is_in_menu
        )
        raw_bundle = self.db_connector.sql_query(
            """
            INSERT INTO Bundles (bundle_id, orderable_id, bundle_name,
                                bundle_reduction, bundle_description,
                                bundle_availability_start_date,
                                bundle_availability_end_date)
            VALUES
            (DEFAULT, %(orderable_id)s, %(bundle_name)s, %(bundle_reduction)s,
             %(bundle_description)s, %(bundle_availability_start_date)s,
             %(bundle_availability_end_date)s)
            RETURNING *;
            """,
            {
                "orderable_id": orderable_id,
                "bundle_name": bundle_name,
                "bundle_reduction": bundle_reduction,
                "bundle_description": bundle_description,
                "bundle_availability_start_date": bundle_availability_start_date,
                "bundle_availability_end_date": bundle_availability_end_date,
            },
            "one",
        )

        bundle_id = raw_bundle["bundle_id"]
        for item, qty in bundle_items.items():
            self.db_connector.sql_query(
                """INSERT INTO Bundle_Items (bundle_id, item_id, item_quantity)
                   VALUES (%(bundle_id)s, %(item_id)s, %(item_quantity)s);
                """,
                {"bundle_id": bundle_id, "item_id": item.item_id, "item_quantity": qty},
                "none",
            )

        raw_bundle["bundle_items"] = self._get_items_from_bundle(bundle_id)
        orderable_infos = self.orderable_dao.get_info_from_orderable(orderable_id)
        raw_bundle_full = {**raw_bundle, **orderable_infos}

        return Bundle(**raw_bundle_full)

    # READ
    @log
    def get_bundle_by_id(self, bundle_id: int) -> Optional[Bundle]:
        """
        Retrieve the bundle associated with a given id.

        Args
        ----
        bundle_id (int):
            Unique identifier of the bundle whose id is requested.

        Returns
        -------
        Bundle or None
            An Bundle object containing the id information
            if found in the database, None otherwise.
        """

        raw_bundle = self.db_connector.sql_query(
            "SELECT * FROM Bundles WHERE bundle_id = %s",
            [bundle_id],
            "one",
        )
        if raw_bundle is None:
            return None

        raw_bundle["bundle_items"] = self._get_items_from_bundle(bundle_id)
        orderable_infos = self.orderable_dao.get_info_from_orderable(raw_bundle["orderable_id"])
        raw_bundle_full = {**raw_bundle, **orderable_infos}
        return Bundle(**raw_bundle_full)

    @log
    def get_bundle_by_orderable_id(self, orderable_id: int) -> Optional[Bundle]:
        """
        Retrieve the bundle associated with a given oderable id.

        Args
        ----
        orderable_id (int):
            Unique identifier of the orderable object

        Returns
        -------
        Bundle or None
            An Bundle object or None if not found
        """
        raw_bundle = self.db_connector.sql_query(
            "SELECT * FROM Bundles WHERE orderable_id = %s",
            [orderable_id],
            "one",
        )

        if raw_bundle is None:
            return None

        raw_bundle["bundle_items"] = self._get_items_from_bundle(raw_bundle["bundle_id"])
        orderable_infos = self.orderable_dao.get_info_from_orderable(raw_bundle["orderable_id"])
        raw_bundle_full = {**raw_bundle, **orderable_infos}
        return Bundle(**raw_bundle_full)

    @log
    def get_all_bundle(self) -> Optional[List[Bundle]]:
        raw_bundles = self.db_connector.sql_query(
            "SELECT bundle_id FROM Bundles", return_type="all"
        )

        if not raw_bundles:
            return []

        return [self.get_bundle_by_id(raw_bundle["bundle_id"]) for raw_bundle in raw_bundles]

    @log
    def update_bundle(self, bundle_id: int, update: dict):
        if self.get_bundle_by_id(bundle_id) is None:
            return None

        parameters_update = [
            "bundle_name",
            "bundle_reduction",
            "bundle_description",
            "bundle_availability_start_date",
            "bundle_availability_end_date",
            "bundle_items",
            "bundle_image",
        ]
        for key in update.keys():
            if key not in parameters_update:
                raise ValueError(f"{key} is not a parameter of Bundle.")

        if update.get("bundle_image"):
            bundle = self.get_bundle_by_id(bundle_id)
            orderable_id = bundle.orderable_id
            bundle_name = (
                update.get("bundle_name") if update.get("bundle_name") else bundle.bundle_name
            )
            self.orderable_dao.update_image(
                orderable_id, "bundle", bundle_name, update["bundle_image"]
            )
            update.pop("bundle_image")

        if update.get("bundle_items"):
            bundle_items = update["bundle_items"]
            self.db_connector.sql_query(
                """DELETE FROM Bundle_Items WHERE bundle_id=%s;
                """,
                [bundle_id],
                "none",
            )
            for item, qty in bundle_items.items():
                self.db_connector.sql_query(
                    """INSERT INTO Bundle_Items
                       VALUES(%(bundle_id)s, %(item_id)s, %(item_quantity)s);
                    """,
                    {"bundle_id": bundle_id, "item_id": item.item_id, "item_quantity": qty},
                    "none",
                )
            update.pop("bundle_items")

        if len(update) == 0:
            return self.get_bundle_by_id(bundle_id)

        updated_fields = [f"{field} = %({field})s" for field in update.keys()]
        set_field = ", ".join(updated_fields)
        params = {**update, "bundle_id": bundle_id}

        self.db_connector.sql_query(
            f"""
            UPDATE Bundles
            SET {set_field}
            WHERE bundle_id = %(bundle_id)s;
            """,
            params,
            "none",
        )

        return self.get_bundle_by_id(bundle_id)

    @log
    def delete_bundle(self, bundle_id: int):
        bundle = self.get_bundle_by_id(bundle_id)
        if bundle:
            orderable_id = bundle.orderable_id

            self.db_connector.sql_query(
                """DELETE FROM Bundle_Items WHERE bundle_id=%s;
                """,
                [bundle_id],
                "none",
            )
            self.orderable_dao.delete_orderable(orderable_id)
            self.db_connector.sql_query(
                """ DELETE FROM Bundles WHERE bundle_id=%s
                    RETURNING *;""",
                [bundle_id],
                "one",
            )

        return None

    def _get_items_from_bundle(self, bundle_id: int) -> Dict[Item, int]:
        raw_items = self.db_connector.sql_query(
            """
            SELECT i.*, bi.item_id, bi.item_quantity
            FROM Bundle_Items AS bi
            INNER JOIN Items AS i ON bi.item_id=i.item_id
            WHERE bi.bundle_id=%s;
            """,
            [bundle_id],
            "all",
        )

        if not raw_items:
            return {}

        items_dict = {}
        for raw_item in raw_items:
            quantity = raw_item["item_quantity"]

            item = self.item_dao.get_item_by_id(raw_item["item_id"])

            if item:
                items_dict[item] = quantity

        return items_dict
