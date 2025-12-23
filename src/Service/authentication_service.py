import re

import phonenumbers

from src.DAO.DBConnector import DBConnector
from src.DAO.userDAO import UserDAO
from src.Model.customer import Customer
from src.Service.password_service import PasswordService


class AuthenticationService:
    def __init__(self, db_connector: DBConnector, password_service: PasswordService):
        """
        Secure authentication service.
        Injects UserDAO for data access and PasswordService for hashing/salting.
        """
        self.user_dao = UserDAO(db_connector=db_connector)
        self.password_service = password_service

    def login(self, username: str, password: str) -> Customer:
        """
        Authenticates a user with username/password using PasswordService helpers.
        """
        user = self.user_dao.find_user_by_username(username)
        if not user:
            raise ValueError("User not found.")

        if not self.password_service.verify_password(user, password):
            raise ValueError("Incorrect password.")

        return user

    def register_customer(self, username: str, password: str, name: str, phone_number: str) -> Customer:
        """
        Registers a new customer.
        Password is checked for strength and securely stored using PasswordService helpers.
        """
        if self.user_dao.find_user_by_username(username):
            raise ValueError(f"Username '{username}' already exists.")

        if len(username) < 6:
            raise ValueError("Username must contain at least 6 characters.")

        pattern = r"^[A-Za-z0-9._-]+$"
        if not re.match(pattern, username):
            raise ValueError(
                "Username may only contain letters (a-z, A-Z), digits (0-9), underscores (_), dots (.), or hyphens (-)."
            )

        # Clean and validate phone number
        phone_number_clean = re.sub(r"[^\d+]", "", phone_number)
        if phone_number_clean.startswith("+"):
            number = phonenumbers.parse(phone_number_clean, None)
        else:
            number = phonenumbers.parse(phone_number_clean, "FR")

        if not phonenumbers.is_valid_number(number):
            raise ValueError("Invalid phone number. Please enter the full international format if outside France.")

        phone_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

        # Create new Customer object
        new_customer = Customer(username=username, name=name, phone_number=phone_number)

        # Set password and salt securely
        self.password_service.set_password(new_customer, password)

        # Add to DB via DAO
        created_customer = self.user_dao.add_user(new_customer)
        return created_customer
