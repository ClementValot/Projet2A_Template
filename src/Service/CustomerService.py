import logging
import re
from typing import List

from src.DAO.CustomerDAO import CustomerDAO
from src.Model.Address import Address
from src.Model.Customer import Customer
from src.Service.AddressService import AddressService
from src.Service.PasswordService import check_password_strength, create_salt, hash_password
from src.Service.UserService import UserService
from src.utils.log_decorator import log


class CustomerService:
    customer_dao: CustomerDAO
    address_service: AddressService
    user_service: UserService

    def __init__(
        self,
        customer_dao: CustomerDAO,
        address_service: AddressService,
        user_service: UserService,
    ):
        self.customer_dao = customer_dao
        self.address_service = address_service
        self.user_service = user_service
        self.pattern = r"^(?=.*[A-Za-zÀ-ÖØ-öø-ÿ])[-A-Za-zÀ-ÖØ-öø-ÿ ]+$"

    @log
    def get_customer_by_id(self, customer_id: int) -> Customer:
        """
        Retrieve the customer associated with a given id.

        Parameters
        ----------
        customer_id : int
            Unique identifier of the customer

        Returns
        -------
        Customer
            A Customer object if found in the database

        Raises
        ------
        ValueError
           Raised if the customer isn't found in the database
        """
        customer = self.customer_dao.get_customer_by_id(customer_id)
        if customer is None:
            raise ValueError(
                f"[CustomerService] Cannot find: customer with ID {customer_id} not found."
            )
        return customer

    @log
    def get_address_by_customer_id(self, customer_id: int) -> Address:
        """
        Retrieve the address associated with a customer

        Parameters
        ----------
        customer_id : int
            Unique identifier of the customer

        Returns
        -------
        Address
            An Address Object if the customer is found in the database
        """
        self.get_customer_by_id(customer_id)
        return self.address_service.get_address_by_customer_id(customer_id)

    @log
    def get_customer_by_email(self, customer_email: str) -> Customer:
        """
        Retrieve a customer via his email address

        Parameters
        ----------
        customer_email : str
            Unique email of the customer

        Returns
        -------
        Customer
            A Customer object if found in the database

        Raises
        ------
        ValueError
           Raised if the customer isn't found in the database
        """
        customer = self.customer_dao.get_customer_by_email(customer_email)
        if customer is None:
            raise ValueError(
                f"[CustomerService] Cannot find: customer with email {customer_email} not found."
            )
        return customer

    @log
    def get_customer_by_phone(self, customer_phone: int) -> Customer:
        """
        Retrive a customer by his phone number

        Parameters
        ----------
        customer_phone : int
            Unique phone number of a customer

        Returns
        -------
        Customer
            A Customer object if found in the database

        Raises
        ------
        ValueError
           Raised if the customer isn't found in the database
        """
        customer = self.customer_dao.get_customer_by_phone(customer_phone)
        if customer is None:
            logging.error(
                f"[CustomerService] Cannot find: customer with phone {customer_phone} not found."
            )
            raise ValueError(f"Customer with phone {customer_phone} not found.")
        return customer

    @log
    def get_all_customers(self, limit: int = 15) -> List[Customer]:
        """
        Fetch all customers of the database

        Returns
        -------
        List[Customer]
            A list of Customer object, an empty list if there is none
        """
        customers = self.customer_dao.get_all_customers(limit)
        return customers

    @log
    def create_customer(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        mail: str,
        password: str,
        address_string: str,
    ) -> Customer:
        """
        Create a customer (and his address) after checking and formatting infos
        Checking:
            - First and last name should only contains letters
            - Email is unique and valid
            - Phone number is unique and valid
            - Password meet all the requirements

        Formatting:
            - First name as snake-case
            - Last Name as uppercase
            - Format the phone number to E164
            - Normalize the email

        Parameters
        ----------
        first_name : str
            First name of the customer
        last_name : str
            Last name of the customer
        phone : str
            Phone number (will be formatted)
        mail : str
            An email
        password : str
            A password that meets the requirements (will be hashed)
        address_string : str
            A string containing all the infos of the address

        Returns
        -------
        Customer
            The customer if successfuly created

        Raises
        ------
        ValueError
            If the first or last name is invalid
        ValueError
            If the phone number is invalid
        ValueError
            If a customer with the same phone number already exists
        ValueError
            If the email is invalid
        ValueError
            If a customer with the same email already exists
        """
        # Check on first and last name
        if not re.match(self.pattern, first_name) or not re.match(self.pattern, last_name):
            logging.error("[CustomerService] First name and last name must only contain letters")
            raise ValueError("Your first name and last name must only contain letters!")
        validated_phone = self.user_service.identifier_validator(phone)
        if validated_phone is None or validated_phone["type"] != "phone":
            logging.error(f"[CustomerService] Cannot create: The phone {phone} is invalid.")
            raise ValueError("Please enter a valid phone number !")
        # Check that phone number is not already used
        existing_user = self.customer_dao.get_customer_by_phone(validated_phone["identifier"])
        if existing_user is not None:
            logging.error(
                "[CustomerService] Cannot create: customer "
                f"with phone {validated_phone['identifier']} "
                "already exists."
            )
            raise ValueError("This phone number is already associated with an account !")
        # Check email
        validated_email = self.user_service.identifier_validator(mail)
        if validated_email is None or validated_email["type"] != "email":
            logging.error(f"[CustomerService] Cannot create: The email {mail} is invalid.")
            raise ValueError("Please enter a valid email !")
        # check that email is not already used
        existing_user = self.customer_dao.get_customer_by_email(validated_email["identifier"])
        if existing_user is not None:
            logging.error("[CustomerService] Email already in use !")
            raise ValueError("This email is already associated with an account !")
        check_password_strength(password)

        address = self.address_service.create_address(address_string)
        formatted_first_name = first_name.strip().capitalize()
        formatted_last_name = last_name.strip().upper()
        valid_formatted_phone = validated_phone["identifier"]
        valid_formatted_email = validated_email["identifier"]
        salt = create_salt()
        password_hash = hash_password(password, salt)

        customer = self.customer_dao.create_customer(
            formatted_first_name,
            formatted_last_name,
            valid_formatted_phone,
            valid_formatted_email,
            password_hash,
            salt,
            address.address_id,
        )

        return customer

    @log
    def login_customer(self, identifier: str, password: str) -> Customer:
        """
        Allows the customer to login by calling the mutual user_service.login method,
        which also handles errors

        Parameters
        ----------
        identifier : str
            Either a phone number or an email address
        password : str
            The customer's password

        Returns
        -------
        Customer
            A Customer object in case of successful login
        """
        return self.user_service.login(identifier, password, "customer")

    @log
    def update_customer(self, customer_id: int, update: dict) -> Customer:  # noqa 901C
        """
        Update a customer personal informations after checking and formatting
        infos from the dictionnary

        Checking:
            - First and last name should only contains letters
            - Email is unique and valid
            - Phone number is unique and valid
            - Password meet all the requirements

        Formatting:
            - First name as snake-case
            - Last Name as uppercase
            - Format the phone number to E164
            - Normalize the email

        Parameters
        ----------
        customer_id : int
            Unique identifier of the customer
        update : dict
            A dictionnary with the name of the variable to update as key and the change as value

        Returns
        -------
        Customer
            The customer if successfuly updated

        Raises
        ------
        ValueError
            If the first or last name is invalid
        ValueError
            If the phone number is invalid
        ValueError
            If a customer with the same phone number already exists
        ValueError
            If the email is invalid
        ValueError
            If a customer with the same email already exists
        """
        self.get_customer_by_id(customer_id)

        if all([value is None for value in update.values()]):
            raise ValueError("You must change at least one field.")

        update = {key: value for key, value in update.items() if update[key]}

        if update.get("customer_first_name"):
            if not re.match(self.pattern, update.get("customer_first_name")):
                logging.error(
                    "[Customer Service] Cannot update customer: First name "
                    "must only contain letters"
                )
                raise ValueError("First name must only contain letters !")
            update["customer_first_name"] = update["customer_first_name"].strip().capitalize()

        if update.get("customer_last_name"):
            if not re.match(self.pattern, update.get("customer_last_name")):
                logging.error(
                    "[Customer Service] Cannot update customer: Last name "
                    "must only contains letters"
                )
                raise ValueError(" Last name must only contain letters!")

            update["customer_last_name"] = update["customer_last_name"].strip().upper()

        if update.get("customer_phone"):
            customer_phone = update["customer_phone"]
            validated_phone = self.user_service.identifier_validator(customer_phone)
            if validated_phone is None or validated_phone["type"] != "phone":
                logging.error(
                    "[CustomerService] Attempted to update with invalid "
                    f"phone number: {customer_phone}"
                )
                raise ValueError(f"The number {update['customer_phone']} is invalid.")

            existing_user = self.customer_dao.get_customer_by_phone(validated_phone["identifier"])
            if existing_user is not None:
                logging.error(
                    "[CustomerService] Cannot create: customer "
                    f"with phone {validated_phone['identifier']} "
                    "already exists."
                )
                raise ValueError("This phone number is already associated with an account !")
            update["customer_phone"] = validated_phone["identifier"]

        if update.get("customer_mail"):
            customer_mail = update["customer_mail"]
            validated_email = self.user_service.identifier_validator(customer_mail)
            if validated_email is None or validated_email["type"] != "email":
                logging.error(
                    f"[CustomerService] Attempted to upsdate with invalid email:{customer_mail}"
                )
                raise ValueError(f"The email {update['customer_mail']} is invalid.")

            existing_user = self.customer_dao.get_customer_by_email(validated_email["identifier"])
            if existing_user is not None:
                logging.error("[CustomerService] Attempted to update with email already in use !")
                raise ValueError("This email is already associated with an account !")

            update["customer_mail"] = validated_email["identifier"]

        updated_customer = self.customer_dao.update_customer(customer_id=customer_id, update=update)
        return updated_customer

    @log
    def update_address(self, customer_id: int, update: dict) -> Customer:
        """
        Allows a customer to update its address.

        Invalid address errors are handled by the AddressService

        Parameters
        ----------
        customer_id : int
            The id of the customer
        update : dict
             dict containg the elements of the address that are to be updated

        Returns
        -------
        Customer
            A Customer object with the new address

        Raises
        ------
        ValueError
            Raised if no fields of the address are changed
        """
        customer = self.get_customer_by_id(customer_id)

        if all([value is None for value in update.values()]):
            logging.error(
                "[CustomerService] Attempted to update address without changing any field"
            )
            raise ValueError("You must change at least one field.")

        address_id = customer.customer_address.address_id
        self.address_service.update_address(address_id, update)

        return self.get_customer_by_id(customer_id)

    @log
    def update_password(self, customer_id: int, old_password: str, new_password: str) -> Customer:
        """
        Allows a customer to update its password by calling the password change method
        from UserService, which also handles errors

        Parameters
        ----------
        customer_id : int
            ID of the customer
        old_password : str
            the old password
        new_password : str
            The new password (must be different from the old one)

        Returns
        -------
        Customer
            A Customer object
        """
        self.get_customer_by_id(customer_id)
        return self.user_service.change_password(
            customer_id, old_password, new_password, "customer"
        )

    @log
    def get_number_customers(self) -> int:
        try:
            return self.customer_dao.get_number_customers()
        except Exception as e:
            raise Exception(f"Error while getting number of customer: {str(e)}") from e

    @log
    def delete_customer(self, customer_id: int) -> None:
        """
        Deletes a customer from the database by its ID.

        Parameters
        ----------
        customer_id : int
            The ID of the customer to delete.
        """
        self.get_customer_by_id(customer_id)
        self.customer_dao.delete_customer(customer_id)
