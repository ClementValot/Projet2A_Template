import logging
import re
from typing import Dict, List, Optional, Union

from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DriverDAO import DriverDAO
from src.DAO.OrderDAO import OrderDAO
from src.Model.Delivery import Delivery
from src.Model.Driver import Driver
from src.Model.Order import OrderState
from src.Service.UserService import UserService
from src.utils.log_decorator import log

from .PasswordService import check_password_strength, create_salt, hash_password


class DriverService:
    driver_dao: DriverDAO
    order_dao: OrderDAO
    delivery_dao: DeliveryDAO
    user_service: UserService

    def __init__(
        self,
        delivery_dao: DeliveryDAO,
        driver_dao: DriverDAO,
        order_dao: OrderDAO,
        user_service: UserService,
    ):
        self.driver_dao = driver_dao
        self.delivery_dao = delivery_dao
        self.user_service = user_service
        self.order_dao = order_dao
        self.pattern = r"^(?=.*[A-Za-zÀ-ÖØ-öø-ÿ])[-A-Za-zÀ-ÖØ-öø-ÿ ]+$"

    @log
    def get_driver_by_id(self, driver_id: int) -> Driver:
        """
        Fetch a driver by his id

        Parameters
        ----------
        driver_id : int
            The unique id of a driver

        Returns
        -------
        Driver
            A Driver object with all the informations about the retrieved driver

        Raises
        ------
        ValueError
            If the given id isn't associated with any driver
        """
        driver = self.driver_dao.get_driver_by_id(driver_id)
        if driver is None:
            logging.error(
                f"[DriverService] Cannot find driver: driver with ID {driver_id} not found."
            )
            raise ValueError(f"Driver with ID {driver_id} not found.")
        return driver

    @log
    def get_driver_by_phone(self, phone_number: str) -> Driver:
        """
        Get a driver thanks to his phone number

        Parameters
        ----------
        phone_number : str
            A phone number as a string in a valid format (E164)

        Returns
        -------
        Driver
            A Driver object with all the informations about the retrieved driver

        Raises
        ------
        ValueError
            If the phone number isn't associated with any driver
        """
        driver = self.driver_dao.get_driver_by_phone(phone_number.strip())
        if driver is None:
            logging.error(
                f"[DriverService] Cannot update driver: driver with phone {phone_number} not found."
            )
            raise ValueError(f"Driver with phone {phone_number} not found.")
        return driver

    @log
    def get_all_drivers(self, limit: int = 15) -> List[Driver]:
        """
        Fetch a certain amount of drivers in the database

        Parameters
        ----------
        limit : int
            The number of driver you want to fetch, by default 15

        Returns
        -------
        List[Driver]
            A list of Driver objects
        """
        return self.driver_dao.get_all_drivers(limit)

    @log
    def login(self, identifier: str, password: str) -> Driver:
        """
        Allows the driver to login by calling the mutual user_service.login method,
        which also handles errors

        Parameters
        ----------
        identifier : str
            a phone number
        password : str
            The driver's password

        Returns
        -------
        Driver
            A Driver object in case of successful login
        """
        return self.user_service.login(identifier, password)

    @log
    def get_driver_current_delivery(self, driver_id: int) -> Optional[Delivery]:
        """
        Retrieves the Order the driver is supposed to be handling

        Parameters
        ----------
        driver_id : int
            The id of the driver

        Returns
        -------
        Optional[Delivery]
            A Delivery, if the driver is delivering
        """
        delivery = self.delivery_dao.get_driver_current_delivery(driver_id)
        if delivery is None or delivery.delivery_state != 1:
            return None

        return delivery

    @log
    def create_driver(self, first_name: str, last_name: str, phone: str, password: str) -> Driver:
        """
        Add a driver personal informations after checking and formatting
        infos

        Checking:
            - First and last name should only contains letters
            - Phone number is unique and valid
            - Password meets all the requirements

        Formatting:
            - First name as snake-case
            - Last Name as uppercase
            - Format the phone number to E164


        Parameters
        ----------
        first_name: str
            First name of the driver
        last_name: str
            Last name of the driver
        phone: str
            Phone number of the driver
        password: str
            A password that meets all the requirements

        Returns
        -------
        Driver
            A newly created Driver object

        Raises
        ------
        ValueError
            If the phone number isn't valid
        ValueError
            If a driver with this phone number already exists
        ValueError
            If the first or last name isn't valid (for example contains numbers)
        """
        validated_phone = self.user_service.identifier_validator(phone)
        if validated_phone is None or validated_phone["type"] != "phone":
            logging.error("[DriverService] Cannot create: The phone {phone} is invalid.")
            raise ValueError("Please enter a valid phone number !")
        # Check that phone number is not already used
        existing_user = self.driver_dao.get_driver_by_phone(validated_phone["identifier"])
        if existing_user is not None:
            logging.error(
                "[DriverService] Cannot create: Driver "
                f"with phone {validated_phone['identifier']} "
                "already exists."
            )
            raise ValueError("This phone number is already associated with an account !")
        if not re.match(self.pattern, first_name) or not re.match(self.pattern, last_name):
            logging.error(
                "[Driver Service] Cannot create driver: First name and last name "
                "must only contain letters"
            )
            raise ValueError("First name and last name must only contain letters")

        check_password_strength(password)
        salt = create_salt()
        password_hash = hash_password(password, salt)

        formatted_first_name = first_name.strip().capitalize()
        formatted_last_name = last_name.strip().upper()
        valid_formatted_phone = validated_phone["identifier"]
        created_driver = self.driver_dao.create_driver(
            first_name=formatted_first_name,
            last_name=formatted_last_name,
            phone=valid_formatted_phone,
            password_hash=password_hash,
            salt=salt,
        )
        return created_driver

    @log
    def update_driver(self, driver_id: int, update: dict) -> Optional[Driver]:
        """
        Update a driver personal informations after checking and formatting
        infos from the dictionnary

        Checking:
            - First and last name should only contains letters
            - Phone number is unique and valid

        Formatting:
            - First name as snake-case
            - Last Name as uppercase
            - Format the phone number to E164

        Parameters
        ----------
        driver_id : int
            The id of the driver to update
        update : dict
            A dictionnary with all the updated informations

        Returns
        -------
        Driver
            A Driver object with the updated informations

        Raises
        ------
        ValueError
            If the update dictionnary is filled with None (no changes)
        ValueError
            First name is invalid
        ValueError
            Last name is invalid
        ValueError
            The driver's phone is invalid
        """
        self.get_driver_by_id(driver_id)

        if all([value is None for value in update.values()]):
            logging.error("[DriverService] Attempted to update driver without changing any fields")
            raise ValueError("You must change at least one field.")

        update = {key: value for key, value in update.items() if update[key]}

        if update.get("driver_first_name"):
            if not re.match(self.pattern, update.get("driver_first_name")):
                logging.error(
                    "[Driver Service] Cannot update driver: First name must only contain letters"
                )
                raise ValueError("First name must only contain letters")
            update["driver_first_name"] = update["driver_first_name"].strip().capitalize()

        if update.get("driver_last_name"):
            if not re.match(self.pattern, update.get("driver_last_name")):
                raise ValueError(
                    "[Driver Service] Cannot update driver: Last name must only contains letters"
                )

            update["driver_last_name"] = update["driver_last_name"].strip().upper()

        if update.get("driver_phone"):
            customer_phone = update["driver_phone"]
            validated_phone = self.user_service.identifier_validator(customer_phone)
            if validated_phone is None or validated_phone["type"] != "phone":
                logging.error(
                    "[DriverService] Attempted to update with "
                    f"invalid phone:{update['driver_phone']}"
                )
                raise ValueError(f"The number {update['driver_phone']} is invalid.")

            update["driver_phone"] = validated_phone["identifier"]

        updated_driver = self.driver_dao.update_driver(driver_id=driver_id, update=update)
        return updated_driver

    @log
    def start_delivery(self, order_id: int, driver_id: int) -> Delivery:
        """
        Allows a driver to start a delivery if it's possible. Set the order's state as 'delivering'
        and the driver's 'driver_is_delivering' as True. Create a delivery

        A driver can start a delivery if the order is prepared and if he's not currently delivering

        Parameters
        ----------
        order_id : int
            The order's id the driver want to handle
        driver_id : int
            The id of the driver

        Returns
        -------
        Delivery
            A Delivery object

        Raises
        ------
        ValueError
            If the order's state isn't "prepared"
        ValueError
            If the driver is already delivering an order
        """
        driver = self.get_driver_by_id(driver_id)
        order = self.order_dao.get_order_by_id(order_id)

        if order.order_state != OrderState.PREPARED:
            logging.error(
                "[DriverService] Cannot start delivery: "
                f"Order isn't prepared, current state: {order.order_state.name}"
            )
            raise ValueError(
                "Cannot start delivery: "
                f"Order isn't prepared, current state: {order.order_state.name}"
            )

        if driver.driver_is_delivering:
            logging.error(
                f"[DriverService] Cannot start delivery: Driver {driver_id} "
                "already has an active delivery"
            )
            raise ValueError(f"Driver {driver_id} already has an active delivery")

        self.delivery_dao.create_delivery(order_id, driver_id)
        self.driver_dao.update_driver(driver_id, update={"driver_is_delivering": True})
        self.order_dao.update_order_state(order_id, OrderState.DELIVERING.value)
        delivery = self.delivery_dao.update_delivery_state(order_id, 1)
        return delivery

    @log
    def end_delivery(self, order_id: int, driver_id: int) -> Delivery:
        """
        Allows a driver to end a delivery if it's possible. Set the order's state as 'delivered'
        and the driver's 'driver_is_delivering' as False. Close the delivery

        A driver can start a delivery if the order is "delivering"

        Parameters
        ----------
        order_id : int
            The order's id the driver is handling
        driver_id : int
            The id of the driver

        Returns
        -------
        Delivery
            A Delivery object

        Raises
        ------
        ValueError
            If the order's state isn't "delivering"
        """
        self.get_driver_by_id(driver_id)

        order = self.order_dao.get_order_by_id(order_id)

        if order.order_state != OrderState.DELIVERING:
            logging.error(
                "[DriverService] Cannot end delivery: Order must be delivering to complete, "
                f"current state: {order.order_state.name}"
            )
            raise ValueError(
                "Cannot end delivery: Order must be delivering to complete, "
                f"current state: {order.order_state.name}"
            )

        self.driver_dao.update_driver(driver_id, update={"driver_is_delivering": False})
        self.order_dao.update_order_state(order_id, OrderState.DELIVERED.value)
        delivery = self.delivery_dao.update_delivery_state(order_id, 2)
        return delivery

    @log
    def get_number_drivers(self) -> int:
        """
        Count the number of drivers in the database

        Returns
        -------
        int
            The number of driver

        Raises
        ------
        Exception
            If any error occured
        """
        try:
            return self.driver_dao.get_number_drivers()
        except Exception as e:
            raise Exception(f"Error while getting number of driver: {str(e)}") from e

    @log
    def delete_driver(self, driver_id: int) -> None:
        """
        Delete the driver from the database (this action cannot be undone)

        Parameters
        ----------
        driver_id : int
            The driver's id
        """
        self.get_driver_by_id(driver_id)
        self.driver_dao.delete_driver(driver_id)

    @log
    def get_driver_stats(self, driver_id: int) -> Dict[str, Union[int, float]]:
        """
        Get the number of deliveries made by the driver and the cumulated price of these orders

        Parameters
        ----------
        driver_id : int
            The driver's id you want to get

        Returns
        -------
        Dict[str, Union[int, float]]
            A dictionnary with the statistics
        """
        deliveries = self.delivery_dao.get_deliveries_by_driver(driver_id)

        nb_orders = len(deliveries)
        earnings = 0.0

        for delivery in deliveries:
            order = self.order_dao.get_order_by_id(delivery.delivery_order_id)
            earnings += order.order_price

        return {"nb_orders": nb_orders, "earnings": round(earnings, 2)}
