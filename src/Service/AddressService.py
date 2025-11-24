import logging
from typing import List

from src.DAO.AddressDAO import AddressDAO
from src.Model.Address import Address
from src.utils.log_decorator import log

from .GoogleMapService import GoogleMapService


class AddressService:
    address_dao: AddressDAO
    gm_service: GoogleMapService

    def __init__(self, address_dao: AddressDAO, gm_service: GoogleMapService) -> None:
        self.address_dao = address_dao
        self.gm_service = gm_service

    @log
    def get_address_by_customer_id(self, customer_id: int) -> Address:
        """
        Fetch an address associated with a customer

        Parameters
        ----------
        customer_id : int
            The unique identifier of the customer

        Returns
        -------
        Address
            An Address Object

        Raises
        ------
        ValueError
            If the customer id is invalid
        """
        address = self.address_dao.get_address_by_customer_id(customer_id)
        if address is None:
            logging.error(
                f"[AddressService] Cannot find Address for customer ID {customer_id} not found."
            )
            raise ValueError(
                f"[AddressService] Cannot find Address for customer ID {customer_id} not found."
            )
        return address

    @log
    def get_all_address(self) -> List[Address]:
        """
        Fetch all the addresses in the database

        Returns
        -------
        List[Address]
            A list with all the addresses in the database

        """
        addresses = self.address_dao.get_all_address()
        return addresses

    @log
    def create_address(
        self,
        address: str,
    ) -> Address:
        """
        Create an address from a string, check that the address real and valid

        Parameters
        ----------
        address : str
            A string (ex: 51 rue Blaise Pascal, 35170 BRUZ)

        Returns
        -------
        Address
            The newly created address
        """
        self.gm_service.validate_address(address)

        components = self.gm_service.extract_components(address)
        return self.address_dao.create_address(**components)

    @log
    def update_address(self, address_id: int, update: dict) -> Address:
        """
        Update an address

        Parameters
        ----------
        address_id : int
            The id of the address to update
        update : dict
            A dictionnary that can contains:
                - address_number: int
                - address_street: str
                - address_postal_code: int
                - address_city: str
                - address_country: str

        Returns
        -------
        Address
            The updated address

        Raises
        ------
        ValueError
            If the update dictionnary is empty
        """
        current_address = self.get_address_by_customer_id(address_id)

        if all([value is None for value in update.values()]):
            raise ValueError(
                "[AddressService] Cannot update address: You must change at least one field."
            )

        for key, value in update.items():
            if not value:
                update[key] = getattr(current_address, key)

        address = (
            f"{update['address_number']} {update['address_street']},"
            f"{update['address_postal_code']} {update['address_city']}, {update['address_country']}"
        )
        self.gm_service.validate_address(address)
        components = self.gm_service.extract_components(address)
        return self.address_dao.update_address(address_id, components)

    @log
    def delete_address(self, address_id: int) -> None:
        """
        Deletes a given address

        Parameters
        ----------
        address_id : int
            The unique id of an address
        """
        self.get_address_by_customer_id(address_id)
        self.address_dao.delete_address_by_id(address_id)
