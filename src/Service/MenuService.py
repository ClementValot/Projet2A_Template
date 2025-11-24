from typing import List, Optional, Union

from src.DAO.BundleDAO import BundleDAO
from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderableDAO import OrderableDAO
from src.Model.Bundle import Bundle
from src.Model.Item import Item
from src.utils.log_decorator import log


class MenuService:
    orderable_dao: OrderableDAO
    item_dao: ItemDAO
    bundle_dao: BundleDAO

    def __init__(self, orderable_dao: OrderableDAO, item_dao: ItemDAO, bundle_dao: BundleDAO):
        self.orderable_dao = orderable_dao
        self.item_dao = item_dao
        self.bundle_dao = bundle_dao

    @log
    def get_all_orderables(self, in_menu=True) -> List[Union[Item, Bundle]]:
        """
        Fetch all the orderables

        Parameters
        ----------
        in_menu : bool, optional
            if True only fetch the orderables in the menu, else fetch all orderables
            by default True

        Returns
        -------
        List[Union[Item, Bundle]]
            A list of Item and Bundle object
        """
        orderables = self.orderable_dao.get_all_orderables()

        Orderables_in_menu = []
        for orderable in orderables:
            if orderable["orderable_type"] == "item":
                item = self.item_dao.get_item_by_orderable_id(orderable["orderable_id"])
                if (in_menu and item.is_in_menu) or in_menu is False:
                    Orderables_in_menu.append(item)
            if orderable["orderable_type"] == "bundle":
                bundle = self.bundle_dao.get_bundle_by_orderable_id(orderable["orderable_id"])
                if (in_menu and bundle.is_in_menu) or in_menu is False:
                    Orderables_in_menu.append(bundle)

        return Orderables_in_menu

    @log
    def get_orderable_from_menu(self, orderable_id: int) -> Optional[Union[Item, Bundle]]:
        """
        Fetch an orderable if it's currently on the menu

        Parameters
        ----------
        orderable_id : int
            Unique identifier of the ordereable

        Returns
        -------
        Union[Item, Bundle]
            An Item or Bundle object

        Raises
        ------
        ValueError
            If the orderable id is invalid
        """
        orderable = self.orderable_dao.get_orderable_by_id(orderable_id)
        if orderable is None:
            raise ValueError(
                f"[MenuService] Cannot get orderable: Orderable with ID {orderable_id} not found."
            )
        if orderable["orderable_type"] == "item":
            item = self.item_dao.get_item_by_orderable_id(orderable["orderable_id"])
            return item if item.is_in_menu else None

        if orderable["orderable_type"] == "bundle":
            bundle = self.bundle_dao.get_bundle_by_orderable_id(orderable["orderable_id"])
            return bundle if bundle.is_in_menu else None

    @log
    def remove_orderable_from_menu(self, orderable_id: int) -> Union[Item, Bundle]:
        """
        Check if the orderable can be removed from the menu, if so remove it

        Parameters
        ----------
        orderable_id : int
            Unique identifier of the orderable

        Returns
        -------
        Union[Item, Bundle]
            The removed orderable

        Raises
        ------
        ValueError
            If the orderable id is invalid
        ValueError
            If the orderable is already off the menu
        """
        orderable = self.orderable_dao.get_orderable_by_id(orderable_id)

        if orderable is None:
            raise ValueError(
                f"[MenuService] Cannot remove from menu: Orderable with ID {orderable_id} unknown."
            )

        if orderable["orderable_type"] == "item":
            orderable_instance = self.item_dao.get_item_by_orderable_id(orderable["orderable_id"])
        elif orderable["orderable_type"] == "bundle":
            orderable_instance = self.bundle_dao.get_bundle_by_orderable_id(
                orderable["orderable_id"]
            )

        if not orderable_instance.is_in_menu:
            raise ValueError(
                f"[MenuService] Cannot remove from menu: Orderable with ID {orderable_id} is "
                "already off the menu."
            )

        self.orderable_dao.update_orderable_state(orderable_id, False)
        orderable_instance.is_in_menu = False

        return orderable_instance

    @log
    def add_orderable_to_menu(self, orderable_id: int) -> Union[Item, Bundle]:
        """
        Check if an orderable can be added to the menu, if so add it

        Parameters
        ----------
        orderable_id : int
            Unique identifier of the orderable

        Returns
        -------
        Union[Item, Bundle]
            The added orderable

        Raises
        ------
        ValueError
            If the orderable id is invalid
        ValueError
            If the orderable is already on the menu
        ValueError
            If the item hasn't enough stock
        ValueError
            If the bundle isn't available
        """
        orderable = self.orderable_dao.get_orderable_by_id(orderable_id)

        if orderable is None:
            raise ValueError(
                f"[MenuService] Cannot add to menu: Orderable with ID {orderable_id} unknown."
            )

        if orderable["orderable_type"] == "item":
            orderable_instance = self.item_dao.get_item_by_orderable_id(orderable["orderable_id"])
        elif orderable["orderable_type"] == "bundle":
            orderable_instance = self.bundle_dao.get_bundle_by_orderable_id(
                orderable["orderable_id"]
            )

        if orderable_instance.is_in_menu:
            raise ValueError(
                f"[MenuService] Cannot add to menu: Orderable with ID {orderable_id} is "
                "already on the menu."
            )

        if not orderable_instance.check_availability():
            if orderable["orderable_type"] == "item":
                raise ValueError(
                    f"[MenuService] Cannot add to menu: Item with ID {orderable_id} "
                    "is out of stock."
                )
            else:
                raise ValueError(
                    f"[MenuService] Cannot add to menu: Bundle with ID {orderable_id} "
                    "is not available (check dates or item stock)."
                )

        self.orderable_dao.update_orderable_state(orderable_id, True)
        orderable_instance.is_in_menu = True
        return orderable_instance

    @log
    def get_orderable_image(self, orderable_id: int) -> str:
        """
        Fetch the image url of an orderable

        Parameters
        ----------
        orderable_id : int
            Unique identifier of the orderable

        Returns
        -------
        str
            The url of the orderable img
        """
        return self.orderable_dao.get_image_from_orderable(orderable_id)

    @log
    def get_number_orderables(self) -> int:
        return self.orderable_dao.get_number_orderables()
