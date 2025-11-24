from typing import List, Optional

from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderDAO import OrderDAO
from src.Model.Item import Item
from src.utils.log_decorator import log


class ItemService:
    item_dao: ItemDAO
    order_dao: OrderDAO

    def __init__(self, item_dao: ItemDAO, order_dao: OrderDAO):
        self.item_dao = item_dao
        self.order_dao = order_dao

    @log
    def get_item_by_id(self, item_id: int) -> Optional[Item]:
        """
        Retrieves an item from the DB by its id.

        Parameters
        ----------
        item_id : int
            id of the item to be retrieved

        Returns
        -------
        Optional[Item]
            The item with the id provided as input

        Raises
        ------
        ValueError
            raised if item id is invalid
        """
        item = self.item_dao.get_item_by_id(item_id)
        if item is None:
            raise ValueError(f"[ItemService] Cannot find: item with ID {item_id} not found.")
        return item

    @log
    def get_all_items(self) -> Optional[List[Item]]:
        """
        Retrieves all the items in the DB

        Returns
        -------
        Optional[List[Item]]
            A list of all items in the DB
        """
        items = self.item_dao.get_all_items()
        return items

    @log
    def create_item(
        self,
        item_name: str,
        item_price: int,
        item_type: str,
        item_description: str,
        item_stock: int,
        item_image: Optional[str] = None,
        is_in_menu: bool = False,
    ) -> Optional[Item]:
        if item_price <= 0:
            raise ValueError("[ItemService] Cannot create item: Price must be strictly positive")

        if item_stock < 0:
            raise ValueError("[ItemService] Cannot create item: Stock must be positive")

        created_item = self.item_dao.create_item(
            item_name=item_name,
            item_price=item_price,
            item_type=item_type,
            item_description=item_description,
            item_stock=item_stock,
            item_image=item_image,
            is_in_menu=is_in_menu,
        )
        return created_item

    @log
    def update_item(self, item_id: int, update: dict) -> Optional[Item]:
        """
        Allows to update one, multiple or all fields of an item

        Parameters
        ----------
        item_id : int
            id of the item to be modified
        update : dict
            a dictionary with the field names as keys and the updated field values as values

        Returns
        -------
        Optional[Item]
            the modified item

        Raises
        ------
        ValueError
            raised if no fields are modified
        ValueError
            raised if trying to set a null or negative price
        ValueError
            raised if trying to set a negative stock
        """
        self.get_item_by_id(item_id)

        if update.get("item_price") is not None and update.get("item_price") <= 0.0:
            raise ValueError("[ItemService] Cannot update item: Price must be strictly positive")

        if update.get("item_stock") and update.get("item_stock") < 0:
            raise ValueError("[ItemService] Cannot update item: Stock must be positive")

        update = {key: value for key, value in update.items() if value is not None}
        item = self.item_dao.update_item(item_id, update=update)
        return item

    @log
    def delete_item(self, item_id: int) -> None:
        """
        Deletes an item from the database by its ID.

        Parameters
        ----------
        item_id : int
            The ID of the item to delete.
        """
        self.get_item_by_id(item_id)
        self.item_dao.delete_item_by_id(item_id)
