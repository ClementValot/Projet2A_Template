import logging
from typing import List, Optional

from pydantic import BaseModel, ConfigDict

from src.DAO.DBConnector import DBConnector
from src.Model.address import Address


class AddressDAO(BaseModel):
    db_connector: DBConnector

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def find_address_by_id(self, id_address: int) -> Optional[Address]:
        """Find an address by its ID.

        Args:
            id_address: The ID of the address to find.

        Returns:
            Address object if found, None otherwise.
        """
        try:
            raw_address = self.db_connector.sql_query(
                "SELECT * FROM address WHERE id_address = %(id_address)s", {"id_address": id_address}, "one"
            )
            if raw_address is None:
                return None

            return Address(**raw_address)
        except Exception as e:
            logging.error(f"Failed to fetch address {id_address}: {e}")
            return None

    def find_all_addresses(self) -> List[Address]:
        """Returns a list of all Address objects from the database.

        Returns:
            List[Address]: A list of Address objects (empty if no addresses exist).
        """
        try:
            raw_addresses = self.db_connector.sql_query("SELECT * FROM address", {}, "all")
            return [Address(**address) for address in raw_addresses]
        except Exception as e:
            logging.error(f"Failed to fetch all addresses: {e}")
            return []

    def add_address(self, address: Address) -> Optional[Address]:
        """Add a new address to the database.

        Args:
            address: The Address object to add.

        Returns:
            Address: The created address with its ID, or None if failed.
        """
        try:
            raw_created_address = self.db_connector.sql_query(
                """
                INSERT INTO address (city, postal_code, street_name, street_number)
                VALUES (%(city)s, %(postal_code)s, %(street_name)s, %(street_number)s)
                RETURNING *;
                """,
                {
                    "city": address.city,
                    "postal_code": address.postal_code,
                    "street_name": address.street_name,
                    "street_number": address.street_number,
                },
                "one",
            )
            return Address(**raw_created_address)
        except Exception as e:
            logging.error(f"Failed to add address: {e}")
            return None

    def update_address(self, address: Address) -> bool:
        """Update an existing address.

        Args:
            address: The Address object with updated information.

        Returns:
            bool: True if update succeeded, False otherwise.
        """
        try:
            res = self.db_connector.sql_query(
                """
                UPDATE address
                SET city = %(city)s,
                    postal_code = %(postal_code)s,
                    street_name = %(street_name)s,
                    street_number = %(street_number)s
                WHERE id_address = %(id_address)s
                RETURNING id_address;
                """,
                {
                    "id_address": address.id_address,
                    "city": address.city,
                    "postal_code": address.postal_code,
                    "street_name": address.street_name,
                    "street_number": address.street_number,
                },
                "one",
            )
            return res is not None
        except Exception as e:
            logging.error(f"Failed to update address {address.id_address}: {e}")
            return False

    def delete_address(self, id_address: int) -> bool:
        """Delete an address from the database.

        Args:
            id_address: The ID of the address to delete.

        Returns:
            bool: True if the deletion succeeded, False otherwise.
        """
        try:
            res = self.db_connector.sql_query(
                "DELETE FROM address WHERE id_address = %(id_address)s RETURNING id_address;",
                {"id_address": id_address},
                "one",
            )
            return res is not None
        except Exception as e:
            logging.error(f"Failed to delete address {id_address}: {e}")
            return False

    def find_address_by_components(
        self, city: str, postal_code: int, street_name: str, street_number: Optional[str] = None
    ) -> Optional[Address]:
        """
        Finds an address by its exact components.
        Handles null street numbers correctly.
        """
        try:
            query = """
                     SELECT * FROM address
                     WHERE city = %(city)s
                     AND postal_code = %(postal_code)s
                     AND street_name = %(street_name)s
                 """
            params = {
                "city": city,
                "postal_code": str(postal_code),
                "street_name": street_name,
            }

            if street_number:
                query += " AND street_number = %(street_number)s"
                params["street_number"] = street_number
            else:
                query += " AND street_number IS NULL"

            raw_address = self.db_connector.sql_query(query, params, "one")

            if raw_address is None:
                return None
            return Address(**raw_address)

        except Exception as e:
            logging.error(f"Failed to find address by components: {e}")
            return None
