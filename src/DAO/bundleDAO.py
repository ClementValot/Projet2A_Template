import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict

from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.Model.discounted_bundle import DiscountedBundle
from src.Model.predefined_bundle import PredefinedBundle


class BundleDAO(BaseModel):
    db_connector: DBConnector
    item_dao: ItemDAO

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _load_required_item_types(self, bundle_id: int) -> List[str]:
        raw_types = self.db_connector.sql_query(
            """
            SELECT item_type, quantity_required
            FROM bundle_required_item
            WHERE id_bundle = %(bundle_id)s
            """,
            {"bundle_id": bundle_id},
            "all",
        )

        required_item_types = []
        for r in raw_types:
            required_item_types.extend([r["item_type"]] * r["quantity_required"])

        return required_item_types

    def _save_required_item_types(self, bundle_id: int, required_item_types: List[str]):
        type_counts = {}
        for item_type in required_item_types:
            type_counts[item_type] = type_counts.get(item_type, 0) + 1

        self.db_connector.sql_query(
            "DELETE FROM bundle_required_item WHERE id_bundle = %(id_bundle)s", {"id_bundle": bundle_id}, None
        )

        for item_type, quantity in type_counts.items():
            self.db_connector.sql_query(
                """
                INSERT INTO bundle_required_item (id_bundle, item_type, quantity_required)
                VALUES (%(id_bundle)s, %(item_type)s, %(quantity_required)s)
                """,
                {"id_bundle": bundle_id, "item_type": item_type, "quantity_required": quantity},
                None,
            )

    def find_bundle_by_id(self, bundle_id: int) -> Optional[Union[PredefinedBundle, DiscountedBundle]]:
        try:
            raw_bundle = self.db_connector.sql_query(
                "SELECT * FROM bundle WHERE id_bundle = %(bundle_id)s", {"bundle_id": bundle_id}, "one"
            )

            if not raw_bundle:
                return None

            bundle_type = raw_bundle["bundle_type"]
            composition = []
            required_item_types = []

            if bundle_type == "predefined":
                raw_items = self.db_connector.sql_query(
                    """
                    SELECT i.*
                    FROM item i
                    JOIN bundle_item bi ON i.id_item = bi.id_item
                    WHERE bi.id_bundle = %(bundle_id)s
                    """,
                    {"bundle_id": bundle_id},
                    "all",
                )

                for item_data in raw_items:
                    item = self.item_dao.find_item_by_id(item_data["id_item"])
                    if item:
                        composition.append(item)

            elif bundle_type == "discount":
                required_item_types = self._load_required_item_types(bundle_id)

            common_args = {
                "id_bundle": raw_bundle["id_bundle"],
                "name": raw_bundle["name"],
                "description": raw_bundle.get("description"),
            }

            if bundle_type == "predefined":
                return PredefinedBundle(
                    **common_args,
                    price=raw_bundle["price"],
                    composition=composition,
                )

            elif bundle_type == "discount":
                return DiscountedBundle(
                    **common_args,
                    discount=raw_bundle["discount"],
                    required_item_types=required_item_types,
                )

            else:
                return None

        except Exception as e:
            logging.error(f"Failed to fetch bundle {bundle_id}: {e}")
            return None

    def find_all_bundles(self) -> List[Union[PredefinedBundle, DiscountedBundle]]:
        try:
            raw_bundles = self.db_connector.sql_query("SELECT id_bundle FROM bundle", {}, "all")

            bundles = []
            for raw_bundle in raw_bundles:
                bundle = self.find_bundle_by_id(raw_bundle["id_bundle"])
                if bundle:
                    bundles.append(bundle)

            return bundles
        except Exception as e:
            logging.error(f"Failed to fetch all bundles: {e}")
            return []

    def add_predefined_bundle(self, bundle: PredefinedBundle) -> Optional[PredefinedBundle]:
        try:
            raw_created_bundle = self.db_connector.sql_query(
                """
                INSERT INTO bundle (name, description, bundle_type, price, discount)
                VALUES (%(name)s, %(description)s, 'predefined', %(price)s, NULL)
                RETURNING *;
                """,
                {"name": bundle.name, "description": getattr(bundle, "description", None), "price": bundle.price},
                "one",
            )

            id_bundle = raw_created_bundle["id_bundle"]

            for item in bundle.composition:
                item_id = item.id_item if hasattr(item, "id_item") else item
                self.db_connector.sql_query(
                    """
                    INSERT INTO bundle_item (id_bundle, id_item)
                    VALUES (%(id_bundle)s, %(id_item)s)
                    """,
                    {"id_bundle": id_bundle, "id_item": item_id},
                    None,
                )

            logging.info(f"Added predefined bundle: {bundle.name}")
            return self.find_bundle_by_id(id_bundle)
        except Exception as e:
            logging.error(f"Failed to add predefined bundle: {e}")
            return None

    def add_discounted_bundle(self, bundle: DiscountedBundle) -> Optional[DiscountedBundle]:
        try:
            raw_created_bundle = self.db_connector.sql_query(
                """
                INSERT INTO bundle (name, description, bundle_type, price, discount)
                VALUES (%(name)s, %(description)s, 'discount', NULL, %(discount)s)
                RETURNING *;
                """,
                {
                    "name": bundle.name,
                    "description": getattr(bundle, "description", None),
                    "discount": bundle.discount,
                },
                "one",
            )

            id_bundle = raw_created_bundle["id_bundle"]

            self._save_required_item_types(id_bundle, bundle.required_item_types)

            logging.info(f"Added discounted bundle: {bundle.name}")
            return self.find_bundle_by_id(id_bundle)

        except Exception as e:
            logging.error(f"Failed to add discounted bundle: {e}")
            return None

    def update_bundle(self, bundle: Union[PredefinedBundle, DiscountedBundle]) -> bool:
        try:
            if isinstance(bundle, PredefinedBundle):
                self.db_connector.sql_query(
                    """
                    UPDATE bundle
                    SET name = %(name)s,
                        description = %(description)s,
                        price = %(price)s
                    WHERE id_bundle = %(id_bundle)s
                    """,
                    {
                        "id_bundle": bundle.id_bundle,
                        "name": bundle.name,
                        "description": getattr(bundle, "description", None),
                        "price": bundle.price,
                    },
                    None,
                )

                self.db_connector.sql_query(
                    "DELETE FROM bundle_item WHERE id_bundle = %(id_bundle)s", {"id_bundle": bundle.id_bundle}, None
                )

                for item in bundle.composition:
                    item_id = item.id_item if hasattr(item, "id_item") else item
                    self.db_connector.sql_query(
                        """
                        INSERT INTO bundle_item (id_bundle, id_item)
                        VALUES (%(id_bundle)s, %(id_item)s)
                        """,
                        {"id_bundle": bundle.id_bundle, "id_item": item_id},
                        None,
                    )

            elif isinstance(bundle, DiscountedBundle):
                self.db_connector.sql_query(
                    """
                    UPDATE bundle
                    SET name = %(name)s,
                        description = %(description)s,
                        discount = %(discount)s
                    WHERE id_bundle = %(id_bundle)s
                    """,
                    {
                        "id_bundle": bundle.id_bundle,
                        "name": bundle.name,
                        "description": getattr(bundle, "description", None),
                        "discount": bundle.discount,
                    },
                    None,
                )

                self._save_required_item_types(bundle.id_bundle, bundle.required_item_types)

            logging.info(f"Updated bundle: {bundle.name}")
            return True
        except Exception as e:
            logging.error(f"Failed to update bundle {bundle.id_bundle}: {e}")
            return False

    def delete_bundle(self, bundle_id: int) -> bool:
        try:
            self.db_connector.sql_query(
                "DELETE FROM bundle_required_item WHERE id_bundle = %(bundle_id)s", {"bundle_id": bundle_id}, None
            )

            self.db_connector.sql_query(
                "DELETE FROM bundle_item WHERE id_bundle = %(bundle_id)s", {"bundle_id": bundle_id}, None
            )

            self.db_connector.sql_query(
                "DELETE FROM bundle WHERE id_bundle = %(bundle_id)s", {"bundle_id": bundle_id}, None
            )

            logging.info(f"Deleted bundle with ID: {bundle_id}")
            return True
        except Exception as e:
            logging.error(f"Failed to delete bundle {bundle_id}: {e}")
            return False