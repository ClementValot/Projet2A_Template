from typing import List

from src.Model.item import Item

from .DBConnector import DBConnector


class ItemDAO:
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector) -> None:
        self.db_connector = db_connector

    def find_item_by_id(self, id_item: int) -> Item:
        raw_item = self.db_connector.sql_query("SELECT * from item WHERE id_item=%s", [id_item], "one")
        if raw_item is None:
            return None
        return Item(**raw_item)

    def get_items_by_ids(self, item_ids: List[int]) -> List[Item]:
        if not item_ids:
            return []

        placeholders = ", ".join(["%s"] * len(item_ids))

        query = f"SELECT * FROM item WHERE id_item IN ({placeholders})"

        raw_items = self.db_connector.sql_query(query, item_ids, "all")

        if not raw_items:
            return []

        return [Item(**raw_item) for raw_item in raw_items]

    def find_all_items(self) -> list[Item]:
        raw_all_items = self.db_connector.sql_query("SELECT * FROM item", {}, "all")
        return [Item(**item) for item in raw_all_items]

    def update_item(self, item: Item) -> bool:
        success_indicator = self.db_connector.sql_query(
            """
            UPDATE item
            SET name = %(name)s,
                item_type = %(item_type)s,
                price = %(price)s,
                description = %(description)s,
                stock = %(stock)s,
                availability = %(availability)s
            WHERE id_item = %(id_item)s; 
            """,
            {
                "id_item": item.id_item,
                "name": item.name,
                "item_type": item.item_type,
                "price": item.price,
                "description": item.description,
                "stock": item.stock,
                "availability": item.availability,
            },
            return_type=None,
        )
        if success_indicator is True or success_indicator is False:
            return success_indicator
        return True

    def add_item(self, item: Item) -> Item:
        raw_created_item = self.db_connector.sql_query(
            """
        INSERT INTO "item" (id_item, name, item_type, price, description, stock, availability)
        VALUES (DEFAULT, %(name)s, %(item_type)s, %(price)s, %(description)s, %(stock)s, %(availability)s)
        RETURNING *;
        """,
            {
                "name": item.name,
                "item_type": item.item_type,
                "price": item.price,
                "description": item.description,
                "stock": item.stock,
                "availability": item.availability,
            },
            "one",
        )
        return Item(**raw_created_item)

    def delete_item(self, id_item: int) -> bool:
        success_indicator = self.db_connector.sql_query(
            """
            DELETE FROM item
            WHERE id_item = %s;
            """,
            (id_item,),
            return_type=None,
        )

        if success_indicator is True or success_indicator is False:
            return success_indicator

        return True
