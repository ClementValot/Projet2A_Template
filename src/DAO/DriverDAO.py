from typing import Optional

from src.Model.Driver import Driver
from src.utils.log_decorator import log
from src.utils.singleton import Singleton

from .DBConnector import DBConnector


class DriverDAO(metaclass=Singleton):
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    # CREATE
    @log
    def create_driver(
        self, first_name: str, last_name: str, phone: str, password_hash: str, salt: str
    ) -> Driver:
        raw_driver = self.db_connector.sql_query(
            """
            INSERT INTO Drivers (driver_id, driver_first_name, driver_last_name,
                                driver_phone, driver_password_hash, driver_salt,
                                driver_is_delivering)
            VALUES (DEFAULT, %(first_name)s, %(last_name)s, %(phone)s,
                    %(password_hash)s, %(salt)s, FALSE)
            RETURNING *;
            """,
            {
                "first_name": first_name,
                "last_name": last_name,
                "phone": phone,
                "password_hash": password_hash,
                "salt": salt,
            },
            "one",
        )
        map_driver = self._map_db_to_model(raw_driver)
        return Driver(**map_driver)

    # READ
    @log
    def get_driver_by_id(self, driver_id: int) -> Optional[Driver]:
        raw_driver = self.db_connector.sql_query(
            "SELECT * FROM Drivers WHERE driver_id=%s", [driver_id], "one"
        )

        if raw_driver is None:
            return None

        map_driver = self._map_db_to_model(raw_driver)
        return Driver(**map_driver)

    @log
    def get_driver_by_phone(self, phone_number: str) -> Optional[Driver]:
        raw_driver = self.db_connector.sql_query(
            "SELECT * FROM Drivers WHERE driver_phone=%s", [phone_number], "one"
        )

        if raw_driver is None:
            return None

        map_driver = self._map_db_to_model(raw_driver)
        return Driver(**map_driver)

    @log
    def get_all_drivers(self, limit: int = 15) -> Optional[list[Driver]]:
        raw_drivers = self.db_connector.sql_query("SELECT * FROM Drivers LIMIT %s;", [limit], "all")
        if raw_drivers is None:
            return None
        return [Driver(**self._map_db_to_model(driver)) for driver in raw_drivers]

    # UPDATE
    @log
    def update_driver(self, driver_id: int, update: dict):
        parameters_update = [
            "driver_first_name",
            "driver_last_name",
            "driver_is_delivering",
            "driver_phone",
            "driver_password_hash",
        ]
        for key in update.keys():
            if key not in parameters_update:
                raise ValueError(f"{key} is not a parameter of Driver.")

        updated_fields = [f"{field} = %({field})s" for field in update.keys()]
        set_field = ", ".join(updated_fields)
        params = {**update, "driver_id": driver_id}

        self.db_connector.sql_query(
            f"""
            UPDATE Drivers
            SET {set_field}
            WHERE driver_id = %(driver_id)s;
            """,
            params,
            "none",
        )
        return self.get_driver_by_id(driver_id)

    # DELETE
    @log
    def delete_driver(self, driver_id: int) -> None:
        self.db_connector.sql_query("DELETE FROM Drivers WHERE driver_id=%s", [driver_id], "none")

    @log
    def get_number_drivers(self) -> int:
        number = self.db_connector.sql_query(
            """
            SELECT COUNT(*)
            FROM Drivers;
            """,
            return_type="one",
        )
        return number["count"]

    @staticmethod
    def _map_db_to_model(raw_driver: dict) -> dict:
        """
        Map the column name of the table into the correct name of the arguments
        to build a Driver instance (beacause it inherits from User)
        """
        return {
            "id": raw_driver["driver_id"],
            "first_name": raw_driver["driver_first_name"],
            "last_name": raw_driver["driver_last_name"],
            "password": raw_driver["driver_password_hash"],
            "salt": raw_driver["driver_salt"],
            "created_at": raw_driver["driver_created_at"],
            "driver_phone": raw_driver["driver_phone"],
            "driver_is_delivering": raw_driver["driver_is_delivering"],
        }
