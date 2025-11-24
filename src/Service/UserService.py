import logging
from typing import Literal, Optional, Union

import phonenumbers as pn
from email_validator import EmailNotValidError, validate_email

from src.DAO.AdminDAO import AdminDAO
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DriverDAO import DriverDAO
from src.Model.Admin import Admin
from src.Model.Customer import Customer
from src.Model.Driver import Driver
from src.Service.PasswordService import (
    check_password_strength,
    hash_password,
    validate_password,
)
from src.utils.log_decorator import log


class UserService:
    def __init__(self, customer_dao: CustomerDAO, driver_dao: DriverDAO, admin_dao: AdminDAO):
        self.customer_dao = customer_dao
        self.driver_dao = driver_dao
        self.admin_dao = admin_dao

    @log
    def login(
        self, identifier: str, password: str, user_type: Literal["customer", "driver", "admin"]
    ) -> Union[Customer, Driver, Admin]:
        """
        Allows a user to login

        Parameters
        ----------
        identifier : str
            The user's identifier
            Phone number for customer and drivers, email for customers only
        password : str
            The user's password
        user_type : Literal["customer", "driver", "admin"]
            The user's role

        Returns
        -------
        Union[Customer, Driver, Admin]
            The corresponding user object

        Raises
        ------
        ValueError
            If the used identifier isn't valid
        ValueError
            If the used identifier is unknown
        """
        user = None
        if user_type == "admin":
            user = self.admin_dao.get_admin_by_username(identifier)
            if user is None:
                raise ValueError("[UserService] Invalid admin username")
        else:
            validated_identifier = self.identifier_validator(identifier)
            if not validated_identifier:
                logging.error(
                    f"[UserService] Login failed for user of type {user_type}:"
                    f" Identifier {identifier} invalid"
                )
                raise ValueError("Invalid identifier!")
            logging.info("[UserService] Identifier validated. Attempting to find the user... ")
            if user_type == "customer" and validated_identifier["type"] == "phone":
                user = self.customer_dao.get_customer_by_phone(validated_identifier["identifier"])
            elif user_type == "customer" and validated_identifier["type"] == "email":
                user = self.customer_dao.get_customer_by_email(validated_identifier["identifier"])
            elif user_type == "driver" and validated_identifier["type"] == "phone":
                user = self.driver_dao.get_driver_by_phone(validated_identifier["identifier"])
        if not user:
            logging.error(f"[UserService] Login failed for user with identifier: {identifier}")
            raise ValueError(f"[UserService] User not found with identifier: {identifier}")

        validate_password(user, password)

        return user

    @log
    def change_password(
        self,
        user_id: int,
        old_password: str,
        new_password: str,
        user_type: Literal["customer", "driver", "admin"],
    ) -> Union[Customer, Driver, Admin]:
        """
        Allows a user of any kind to change its password.
        The method requires knowledge of the old password,
        and performs checks (special character, number ...)
        on the new password.

        Parameters
        ----------
        user_id : int
            The id of the user updating its password
        old_password : str
            the user's password to be replaced
        new_password : str
            he new password chosen by the user
        user_type : Literal[customer, driver, admin]
            the user's type

        Returns
        -------
        Union[Customer, Driver, Admin]
            The corresponding user object
        """
        user = self._get_user_by_type(user_id, user_type)

        validate_password(user, old_password)

        check_password_strength(new_password)

        new_hashed = hash_password(new_password, user.salt)

        if user_type == "customer":
            return self.customer_dao.update_customer(
                user_id, {"customer_password_hash": new_hashed}
            )
        elif user_type == "driver":
            return self.driver_dao.update_driver(user_id, {"driver_password_hash": new_hashed})
        elif user_type == "admin":
            return self.admin_dao.update_admin_password(new_hashed)

    def _get_user_by_type(
        self, user_id: int, user_type: Literal["customer", "driver", "admin"]
    ) -> Union[Customer, Driver, Admin]:
        """
        Given a user id and a user type, retries the user by its id according to its type

        Parameters
        ----------
        user_id : int
            The user to be retrieved's id (unique by type)
        user_type : Literal[customer, driver, admin]
            The corresponding user object

        Returns
        -------
        Union[Customer, Driver, Admin]
            The user as identified by id and type
        """
        if user_type == "customer":
            return self.customer_dao.get_customer_by_id(user_id)
        elif user_type == "driver":
            return self.driver_dao.get_driver_by_id(user_id)
        elif user_type == "admin":
            return self.admin_dao.get_admin_by_id(user_id)

    @log
    def identifier_validator(self, identifier: str) -> Optional[dict]:
        """
        Atttempts to validate (check if real, and properly format) an identfier
        which is either a phone number (for both drivers and customers)
        or an email address (customers only)

        Phone numbers are formatted in the E164 format as it is globally unique

        in case it is not valid, it returns None instead of raising an error
        and lets the service function (register, login, update) raise the error

        Parameters
        ----------
        identifier : str
            either an email or a phone number

        Returns
        -------
        Optional[dict]
             A dictionary containing the type of identfier (either phone or email)
             and the formatted identifier
             Or None if the identifier is not valid
        """
        logging.info("[UserService] Parsing identifier as email...")
        try:
            emailinfo = validate_email(identifier, check_deliverability=True)
            return {"type": "email", "identifier": emailinfo.normalized}
        except EmailNotValidError:
            pass
        logging.info("[UserService] Parsing identifier as french phone...")
        try:
            phone_number = pn.parse(identifier, "FR")
            if pn.is_valid_number(phone_number) and pn.is_possible_number(phone_number):
                return {
                    "type": "phone",
                    "identifier": pn.format_number(phone_number, pn.PhoneNumberFormat.E164),
                }
        except pn.NumberParseException:
            pass
        logging.info("[UserService] Parsing identifier as international phone...")
        try:
            phone_number = pn.parse(identifier)
            if pn.is_valid_number(phone_number) and pn.is_possible_number(phone_number):
                return {
                    "type": "phone",
                    "identifier": pn.format_number(phone_number, pn.PhoneNumberFormat.E164),
                }
        except pn.NumberParseException:
            pass
        logging.warning("[UserService] Identifier could not be parsed. Register/Login will fail.")
        return None
