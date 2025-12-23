import os
from typing import List, Optional

import requests
from dotenv import load_dotenv

from src.DAO.addressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.Model.address import Address


class AddressService:
    def __init__(self, db_connector: DBConnector):
        """
        Initializes the service and injects the connector into the DAO.
        """
        load_dotenv()
        self.address_dao = AddressDAO(db_connector=db_connector)
        self.api_key = os.environ["GOOGLE_MAPS_API_KEY"]

    def get_or_create_address(
        self, street_name: str, city: str, postal_code: int, street_number: str = None
    ) -> Optional[Address]:
        """
        Retrieves an address from the database if it exists.
        If not found, creates a new address record.
        This assumes the address components have already been validated.
        """

        existing_address = self.address_dao.find_address_by_components(
            city=city, postal_code=postal_code, street_name=street_name, street_number=street_number
        )

        if existing_address:
            return existing_address

        try:
            new_address = Address(
                street_name=street_name,
                street_number=street_number,
                city=city,
                postal_code=postal_code,
            )

            created_address = self.address_dao.add_address(new_address)

            if not created_address:
                raise Exception("DAO failed to add new address.")

            return created_address

        except Exception as e:
            raise ValueError(f"Database error while saving address: {e}") from e

    def get_address_by_id(self, address_id: int) -> Optional[Address]:
        """
        Retrieves a specific address by its ID.
        """
        address = self.address_dao.find_address_by_id(address_id)
        if not address:
            raise ValueError(f"No address found with ID {address_id}.")
        return address

    def delete_address(self, address_id: int) -> bool:
        """
        Deletes an address by its ID.
        Checks if the address exists first.
        """
        address = self.address_dao.find_address_by_id(address_id)
        if not address:
            raise ValueError(f"No address found with ID {address_id}.")

        if not self.address_dao.delete_address(address_id):
            raise Exception(f"Failed to delete address {address_id}.")

        return True

    def list_all_addresses(self) -> List[Address]:
        """
        Returns a list of all registered addresses.
        """
        return self.address_dao.find_all_addresses()
