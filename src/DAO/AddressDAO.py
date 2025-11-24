from typing import Optional

from src.Model.Address import Address
from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from .DBConnector import DBConnector


class AddressDAO(metaclass=Singleton):
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    # CREATE
    @log
    def create_address(
        self,
        address_number: int,
        address_street: str,
        address_city: str,
        address_postal_code: int,
        address_country: str,
    ) -> Address:
        raw_created_address = self.db_connector.sql_query(
            """
            INSERT INTO Addresses (address_id, address_number, address_street, address_city,
            address_postal_code, address_country)
            VALUES (DEFAULT, %(number)s, %(street)s, %(city)s, %(postal_code)s, %(country)s)
            RETURNING *;
            """,
            {
                "number": address_number,
                "street": address_street,
                "city": address_city,
                "postal_code": address_postal_code,
                "country": address_country,
            },
            "one",
        )
        return Address(**raw_created_address)

    # READ

    @log
    def get_address_by_customer_id(self, customer_id: int) -> Optional[Address]:
        raw_address = self.db_connector.sql_query(
            """SELECT *
               FROM Addresses
               WHERE address_id = %s;
            """,
            [customer_id],
            "one",
        )

        return Address(**raw_address) if raw_address else None

    @log
    def get_all_addresses(self) -> Optional[list[Address]]:
        raw_addresses = self.db_connector.sql_query("SELECT * FROM Addresses", return_type="all")

        return [Address(**raw_address) for raw_address in raw_addresses] if raw_addresses else []

    # UPDATE
    @log
    def update_address(self, address_id: int, update: dict):
        if not update:
            raise ValueError("At least one value should be updated")

        parameters_update = [
            "address_number",
            "address_street",
            "address_city",
            "address_postal_code",
            "address_country",
        ]
        for key in update.keys():
            if key not in parameters_update:
                raise ValueError(f"{key} is not a parameter of Address.")

        updated_fields = [f"{field} = %({field})s" for field in update.keys()]
        set_field = ", ".join(updated_fields)
        params = {**update, "address_id": address_id}

        self.db_connector.sql_query(
            f"""
            UPDATE Addresses
            SET {set_field}
            WHERE address_id = %(address_id)s;
            """,
            params,
            "none",
        )

        return self.get_address_by_customer_id(address_id)

    # DELETE
    @log
    def delete_address_by_id(self, address_id: int) -> None:
        self.db_connector.sql_query(
            "DELETE FROM Addresses WHERE address_id = %(address_id)s",
            {"address_id": address_id},
            None,
        )
