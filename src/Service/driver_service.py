import logging
from datetime import datetime
from typing import List, Optional

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.deliveryDAO import DeliveryDAO
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO
from src.Model.delivery import Delivery
from src.Model.driver import Driver
from src.Model.order import Order
from src.Service.api_maps_service import ApiMapsService


class DriverService:
    def __init__(self, db_connector: DBConnector):
        """
        Initializes the service and injects dependencies into the DAOs.
        """
        self.item_dao = ItemDAO(db_connector=db_connector)
        self.user_dao = UserDAO(db_connector=db_connector)
        self.address_dao = AddressDAO(db_connector=db_connector)
        self.bundle_dao = BundleDAO(db_connector=db_connector, item_dao=self.item_dao)

        self.order_dao = OrderDAO(
            db_connector=db_connector,
            user_dao=self.user_dao,
            address_dao=self.address_dao,
            bundle_dao=self.bundle_dao,
            item_dao=self.item_dao,
        )

        self.delivery_dao = DeliveryDAO(db_connector=db_connector, user_dao=self.user_dao, order_dao=self.order_dao)

    def create_and_assign_delivery(self, order_ids: List[int], user_id: int) -> Optional[Delivery]:
        """
        Creates a new delivery run from a list of 'validated' order IDs and
        immediately assigns it to the specified available driver.
        The delivery status is set directly to 'in_progress'.
        """
        if not order_ids:
            raise ValueError("Cannot create a delivery with no orders.")

        driver = self.user_dao.find_user_by_id(user_id)
        if not driver or not isinstance(driver, Driver):
            raise ValueError(f"No valid driver found with ID {user_id}")

        if not driver.availability:
            raise ValueError(f"Driver {driver.name} is not available to start a new delivery.")

        orders = []
        for order_id in order_ids:
            order = self.order_dao.find_order_by_id(order_id)
            if not order:
                raise ValueError(f"Order with ID {order_id} not found.")
            if order.status != "pending":
                raise ValueError(f"Order {order_id} has not the pending status. Current status: {order.status}")
            orders.append(order)

        for o in orders:
            o.status = "in_progress"
            self.order_dao.update_order(o)

        new_delivery = Delivery(
            driver=driver,
            orders=orders,
            status="in_progress",
            delivery_time=None,
        )

        created_delivery = self.delivery_dao.add_delivery(new_delivery)

        if not created_delivery:
            raise Exception("Failed to create and assign the delivery in the database.")

        driver.availability = False
        self.user_dao.update_user(driver)

        return created_delivery

    def get_assigned_delivery(self, user_id: int):
        delivery = self.delivery_dao.find_in_progress_deliveries_by_driver(user_id)
        return delivery

    def get_itinerary(self, user_id: int):
        """
        Retrieves the ongoing delivery for a given driver.
        """
        deliveries = self.delivery_dao.find_in_progress_deliveries_by_driver(user_id)
        if not deliveries:
            print("Aucune livraison en cours pour ce chauffeur.")
            return None
        delivery = deliveries[0]

        driver = self.user_dao.find_user_by_id(user_id)
        if not driver or not isinstance(driver, Driver):
            raise ValueError(f"No valid driver found with ID {user_id}")

        adresses = [
            f"{order.address.street_number} {order.address.street_name}, {order.address.city}, France"
            for order in delivery.orders
        ]
        service = ApiMapsService()
        return service.Driveritinerary(adresses)

    def complete_delivery(self, delivery_id: int) -> Optional[Delivery]:
        """
        Marks a delivery as 'delivered' and sets the delivery time.
        """
        delivery = self.delivery_dao.find_delivery_by_id(delivery_id)
        if not delivery:
            raise ValueError(f"No delivery found with ID {delivery_id}.")

        if delivery.status != "in_progress":
            raise ValueError(f"Only 'in_progress' deliveries can be completed. Current status: {delivery.status}")

        delivery.status = "delivered"
        delivery.delivery_time = datetime.now()

        try:
            for order in delivery.orders:
                order.status = "delivered"
                self.order_dao.update_order(order)
        except Exception as e:
            logging.warning(f"Could not update status for orders in delivery {delivery_id}: {e}")

        if not self.delivery_dao.update_delivery(delivery):
            raise Exception("Failed to update delivery status to completed.")

        return delivery

    def get_delivery_details(self, delivery_id: int) -> Optional[Delivery]:
        """
        Retrieves all details for a single delivery.
        """
        delivery = self.delivery_dao.find_delivery_by_id(delivery_id)
        if not delivery:
            raise ValueError(f"No delivery found with ID {delivery_id}.")
        addresses_list = {}
        customer_list = {}
        phone_list = {}
        for order in delivery.orders:
            addresses_list[order.id_order] = order.address
            customer_list[order.id_order] = order.customer.name
            phone_list[order.id_order] = order.customer.phone_number
        return addresses_list, customer_list, phone_list

    def list_pending_orders(self) -> List[Order]:
        """
        Returns a list of all orders with 'pending' status (awaiting a driver).
        """
        all_orders = self.order_dao.find_all_orders()
        return [o for o in all_orders if o.status == "pending"]