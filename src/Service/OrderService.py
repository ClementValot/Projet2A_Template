from typing import Dict, List, Literal

from src.DAO.BundleDAO import BundleDAO
from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderableDAO import OrderableDAO
from src.DAO.OrderDAO import OrderDAO
from src.Model.Order import Order, OrderState
from src.utils.log_decorator import log


class OrderService:
    order_dao: OrderDAO
    orderable_dao: OrderableDAO
    item_dao: ItemDAO
    bundle_dao: BundleDAO

    def __init__(
        self,
        order_dao: OrderDAO,
        orderable_dao: OrderableDAO,
        item_dao: ItemDAO,
        bundle_dao: BundleDAO,
    ):
        self.order_dao = order_dao
        self.orderable_dao = orderable_dao
        self.item_dao = item_dao
        self.bundle_dao = bundle_dao
        self.valid_transition = {
            OrderState.PENDING: [OrderState.PAID, OrderState.CANCELLED],
            OrderState.PAID: [OrderState.PREPARED, OrderState.CANCELLED],
            OrderState.PREPARED: [OrderState.DELIVERING, OrderState.CANCELLED],
            OrderState.DELIVERING: [OrderState.DELIVERED, OrderState.CANCELLED],
            OrderState.DELIVERED: [],
            OrderState.CANCELLED: [],
        }

    @log
    def get_order_by_id(self, order_id: int) -> Order:
        """
        Fetch an order by its unique id

        Parameters
        ----------
        order_id : int
            Unique identifier of the order

        Returns
        -------
        Order
            An Order object with all its information

        Raises
        ------
        ValueError
            If the id isn't link to any order
        """
        order = self.order_dao.get_order_by_id(order_id)
        if order is None:
            raise ValueError(f"[Order Service] Cannot find: order with ID {order_id} not found.")
        return order

    @log
    def get_all_orders(self, limit: int) -> List[Order]:
        """
        Fetch a certain number of orders. The firsts orders are the latests.

        Parameters
        ----------
        limit : int
            The number of order you want

        Returns
        -------
        List[Order]
            The retrived orders
        """
        return self.order_dao.get_all_orders(limit)

    @log
    def get_all_orders_by_customer(self, customer_id: int) -> List[Order]:
        """
        Get all the past and current orders of a given customer. Orders are ordered by date
        (latests orders first)

        Parameters
        ----------
        customer_id : int
            The id of the customer whose history you want

        Returns
        -------
        List[Order]
            The list of orders associated with this user
        """
        return self.order_dao.get_all_orders_by_customer(customer_id)

    @log
    def get_customer_current_order(self, customer_id: int) -> Order:
        """
        Fetch the current order of a given customer. It means the order he's currently
        updating

        Parameters
        ----------
        customer_id : int
            The id of the customer whose history you want

        Returns
        -------
        Order
            His current order
        """
        return self.order_dao.get_customer_current_order(customer_id)

    @log
    def get_orders_by_state(
        self, state: OrderState, order_by: Literal["DESC", "ASC"] = "DESC"
    ) -> List[Order]:
        """
        Fetch all the orders with a given state

        Parameters
        ----------
        state: OrderState
            An OrderState object (OrderState.<WANTED STATE>)

        order_by: Literal["DESC", "ASC"]
            How to order the returned order
            - ASC -> The latest orders first
            - DESC -> The earlist orders first
            It is "DESC" by default

        Returns
        -------
        List[Order]
            All the orders of the given state
        """
        return self.order_dao.get_orders_by_state(state.value)

    @log
    def get_available_orders_for_drivers(self) -> List[Order]:
        """
        Fetch all the orders that can be taken by a driver (it means the order paid and prepared)

        Returns
        -------
        List[Order]
            A list of Order objects that are prepared
        """
        return self.order_dao.get_orders_by_state(OrderState.PREPARED.value, order_by="ASC")

    @log
    def get_actives_orders(self) -> List[Order]:
        """
        Fetch all the orders that are not already delivered

        Returns
        -------
        List[Order]
            A list of Order objects
        """
        return self.order_dao.get_actives_orders()

    @log
    def create_order(self, customer_id: int) -> Order:
        """
        Create an order if the customer does not have any active order yet

        Parameters
        ----------
        customer_id : int
            The id of the customer

        Returns
        -------
        Order
            An empty Order object
        """
        orders = self.get_all_orders_by_customer(customer_id)
        states = [order.order_state.value for order in orders]

        if any(state < OrderState.PAID.value for state in states):
            return self.get_customer_current_order(customer_id)

        new_order = self.order_dao.create_order(customer_id=customer_id)
        return new_order

    @log
    def update_order_state(self, order_id: int, new_state: OrderState) -> Order:
        """
        Update the state of an order. The valid state are:
            - PENDING
            - PAID
            - PREPARED
            - DELIVERING
            - DELIVERED
            - CANCELLED

        Parameters
        ----------
        order_id : int
            The identifier of the order
        new_state : OrderState
            The updated state of the order

        Returns
        -------
        Order
            The updated Order object

        Raises
        ------
        ValueError
            If you try to skip a step in the order process
            (example: mark an order as prepared but it wasn't paid yet)
        """
        order = self.get_order_by_id(order_id)

        if new_state not in self.valid_transition[order.order_state]:
            raise ValueError(
                "[OrderService] Cannot change state: Cannot go from "
                f"{order.order_state} to {new_state}."
            )

        updated_order = self.order_dao.update_order_state(order_id, new_state.value)
        return updated_order

    @log
    def mark_as_paid(self, order_id: int) -> Order:
        """
        Update an order as paid

        Parameters
        ----------
        order_id : int
            The unique identifier of the order

        Returns
        -------
        Order
            The updated Order object
        """
        return self.update_order_state(order_id, OrderState.PAID)

    @log
    def mark_as_prepared(self, order_id: int) -> Order:
        """
        Update an order as prepared (it is ready to deliver)

        Parameters
        ----------
        order_id : int
            The unique identifier of the order

        Returns
        -------
        Order
            The updated Order object
        """
        return self.update_order_state(order_id, OrderState.PREPARED)

    @log
    def delete_order(self, order_id: int) -> None:
        """
        Delete an order from the database

        Parameters
        ----------
        order_id : int
            Unique identifier of the order
        """
        self.get_order_by_id(order_id)
        self.order_dao.delete_order(order_id)

    @log
    def add_orderable_to_order(self, orderable_id: int, order_id: int, quantity: int = 1) -> Order:
        """
        Add an orderable to a given order if enough stock is available.

        Parameters
        ----------
        item_id : int
            The id of the item to add
        order_id : int
            The id of the order
        quantity : int
            Number of units to add (default is 1)

        Returns
        -------
        Order
            The updated order object

        Raises
        ------
        ValueError
            If the orderable id isn't associated with any orderable
        ValueError
            If you try to add an item that isn't in the menu
        ValueError
            If the item doesn't have enough stock
        ValueError
            If the bundle isn't in the menu
        ValueError
            If the bundle doesn't have enough stock
        """
        raw_orderable = self.orderable_dao.get_orderable_by_id(orderable_id)

        if raw_orderable is None:
            raise ValueError(f"[OrderService] Orderable with ID {orderable_id} not found.")

        if raw_orderable["orderable_type"] == "item":
            orderable = self.item_dao.get_item_by_orderable_id(orderable_id)
            if not orderable.is_in_menu:
                raise ValueError("[OrderService] The item isn't available.")
            if not orderable.check_stock(quantity):
                raise ValueError(
                    f"[OrderService] Not enough stock for {orderable.item_name}"
                    f" (available: {orderable.item_stock})."
                )
            update_data = {"item_stock": orderable.item_stock - quantity}
            self.item_dao.update_item(orderable.item_id, update_data)

        if raw_orderable["orderable_type"] == "bundle":
            orderable = self.bundle_dao.get_bundle_by_orderable_id(orderable_id)
            if not orderable.is_in_menu:
                raise ValueError("[OrderService] The item isn't available.")

            if not orderable.check_stock(quantity):
                raise ValueError(
                    f"[OrderService] Not enough stock for {orderable.bundle_name}"
                    f" (available: {orderable.get_stock()})."
                )
            for item, nb in orderable.bundle_items.items():
                update_data = {"item_stock": item.item_stock - nb * quantity}
                self.item_dao.update_item(item.item_id, update_data)

        return self.order_dao.add_orderable_to_order(order_id, orderable.orderable_id, quantity)

    @log
    def remove_orderable_from_order(
        self, orderable_id: int, order_id: int, quantity: int = 1
    ) -> Order:
        """
        Remove an orderable to a given order

        Parameters
        ----------
        orderable_id : int
            The id of the item to remove
        order_id : int
            The id of the order
        quantity : int
            Number of units to remove (default is 1)

        Returns
        -------
        Order
            The updated order object

        Raises
        ------
        ValueError
            If the orderable id isn't associated with any orderable
        ValueError
            If you try to remove more orderable than there is in the order

        """
        raw_orderable = self.orderable_dao.get_orderable_by_id(orderable_id)
        if raw_orderable is None:
            raise ValueError(f"[OrderService] Orderable with ID {orderable_id} not found.")
        quantity_in_order = self.order_dao.get_quantity_of_orderables(order_id, orderable_id)
        if quantity_in_order < quantity:
            raise ValueError(
                f"[OrderService] Trying to remove {quantity} of orderable {orderable_id} when "
                f"there is only {quantity_in_order} of it in the order !"
            )
        if raw_orderable["orderable_type"] == "item":
            orderable = self.item_dao.get_item_by_orderable_id(orderable_id)

            update_data = {"item_stock": orderable.item_stock + quantity}
            self.item_dao.update_item(orderable.item_id, update_data)

        if raw_orderable["orderable_type"] == "bundle":
            orderable = self.bundle_dao.get_bundle_by_orderable_id(orderable_id)

            for item, nb in orderable.bundle_items.items():
                update_data = {"item_stock": item.item_stock + nb * quantity}
                self.item_dao.update_item(item.item_id, update_data)

        return self.order_dao.remove_orderable_from_order(
            order_id, orderable.orderable_id, quantity
        )

    @log
    def get_benef(self) -> float:
        """
        Calculate the total earnings of Ub'EJR

        Returns
        -------
        float
            The sum of all the paid orders

        Raises
        ------
        Exception
            If any error happens
        """
        try:
            return self.order_dao.get_benef()
        except Exception as e:
            raise Exception(f"An error occured while calculating profits: {str(e)}") from e

    @log
    def get_number_orders_by_state(self) -> Dict[str, int]:
        """
        Get the number of orders that are beign cooked, and are ready for the driver to pick up

        Returns
        -------
        Dict[str, str]
            A dictionnary with the number of order for the states "preparing" and "ready_to_deliver'

        Raises
        ------
        Exception
            If any error happens
        """
        try:
            return self.order_dao.get_number_orders_by_state()
        except Exception as e:
            raise Exception(f"An error occured while fetchin orders: {str(e)}") from e
