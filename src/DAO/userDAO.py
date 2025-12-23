import logging
from datetime import date
from typing import List, Optional, Union

from src.Model.admin import Admin
from src.Model.customer import Customer
from src.Model.driver import Driver

from .DBConnector import DBConnector


class UserDAO:
    db_connector: DBConnector

    def __init__(self, db_connector: DBConnector):
        self.db_connector = db_connector

    def find_user_by_id(self, id_user: int) -> Optional[Union[Customer, Driver, Admin]]:
        try:
            raw_user = self.db_connector.sql_query(
                """
                SELECT
                    u.*,
                    c.name as customer_name,
                    c.phone_number as customer_phone,
                    d.name as driver_name,
                    d.phone_number as driver_phone,
                    d.vehicle_type,
                    d.availability,
                    a.name as admin_name,
                    a.phone_number as admin_phone
                FROM "user" u
                LEFT JOIN customer c USING (id_user)
                LEFT JOIN driver d USING (id_user)
                LEFT JOIN admin a USING (id_user)
                WHERE u.id_user = %(id_user)s
                """,
                {"id_user": id_user},
                "one",
            )

            if not raw_user:
                return None

            user_type = raw_user["user_type"]

            if user_type == "customer":
                user = Customer(
                    id_user=raw_user["id_user"],
                    username=raw_user["username"],
                    sign_up_date=raw_user["sign_up_date"],
                    name=raw_user["customer_name"],
                    phone_number=raw_user["customer_phone"],
                )

            elif user_type == "driver":
                user = Driver(
                    id_user=raw_user["id_user"],
                    username=raw_user["username"],
                    sign_up_date=raw_user["sign_up_date"],
                    name=raw_user["driver_name"],
                    phone_number=raw_user["driver_phone"],
                    vehicle_type=raw_user["vehicle_type"],
                    availability=raw_user["availability"],
                )

            elif user_type == "admin":
                user = Admin(
                    id_user=raw_user["id_user"],
                    username=raw_user["username"],
                    sign_up_date=raw_user["sign_up_date"],
                    name=raw_user["admin_name"],
                    phone_number=raw_user["admin_phone"],
                )

            else:
                return None

            # Inject private attributes
            user._hash_password = raw_user["hash_password"]
            user._salt = raw_user["salt"]

            return user

        except Exception as e:
            logging.error(f"Failed to fetch user {id_user}: {e}")
            return None

    def find_user_by_username(self, username: str) -> Optional[Union[Customer, Driver, Admin]]:
        try:
            raw_user = self.db_connector.sql_query(
                """
                SELECT u.*,
                    c.name as customer_name,
                    c.phone_number as customer_phone,
                    d.name as driver_name,
                    d.phone_number as driver_phone,
                    d.vehicle_type,
                    d.availability,
                    a.name as admin_name,
                    a.phone_number as admin_phone
                FROM "user" u
                LEFT JOIN customer c USING (id_user)
                LEFT JOIN driver d USING (id_user)
                LEFT JOIN admin a USING (id_user)
                WHERE u.username = %(username)s
                """,
                {"username": username},
                "one",
            )

            if not raw_user:
                return None

            user_type = raw_user["user_type"]

            if user_type == "customer":
                user = Customer(
                    id_user=raw_user["id_user"],
                    username=raw_user["username"],
                    sign_up_date=raw_user["sign_up_date"],
                    name=raw_user["customer_name"],
                    phone_number=raw_user["customer_phone"],
                )

            elif user_type == "driver":
                user = Driver(
                    id_user=raw_user["id_user"],
                    username=raw_user["username"],
                    sign_up_date=raw_user["sign_up_date"],
                    name=raw_user["driver_name"],
                    phone_number=raw_user["driver_phone"],
                    vehicle_type=raw_user["vehicle_type"],
                    availability=raw_user["availability"],
                )

            elif user_type == "admin":
                user = Admin(
                    id_user=raw_user["id_user"],
                    username=raw_user["username"],
                    sign_up_date=raw_user["sign_up_date"],
                    name=raw_user["admin_name"],
                    phone_number=raw_user["admin_phone"],
                )

            else:
                return None

            # Inject private attributes
            user._hash_password = raw_user["hash_password"]
            user._salt = raw_user["salt"]

            return user

        except Exception as e:
            logging.error(f"Failed to fetch user {username}: {e}")
            return None

    def find_all(self, user_type: Optional[str] = None) -> List[Union[Customer, Driver, Admin]]:
        try:
            query = """
                SELECT u.*,
                    c.name as customer_name,
                    c.phone_number as customer_phone,
                    d.name as driver_name,
                    d.phone_number as driver_phone,
                    d.vehicle_type,
                    d.availability,
                    a.name as admin_name,
                    a.phone_number as admin_phone
                FROM "user" u
                LEFT JOIN customer c USING (id_user)
                LEFT JOIN driver d USING (id_user)
                LEFT JOIN admin a USING (id_user)
            """
            params = {}

            if user_type:
                query += " WHERE u.user_type = %(user_type)s"
                params["user_type"] = user_type

            raw_users = self.db_connector.sql_query(query, params, "all")
            users = []

            for u in raw_users:
                if u["user_type"] == "customer":
                    obj = Customer(
                        id_user=u["id_user"],
                        username=u["username"],
                        sign_up_date=u["sign_up_date"],
                        name=u["customer_name"],
                        phone_number=u["customer_phone"],
                    )

                elif u["user_type"] == "driver":
                    obj = Driver(
                        id_user=u["id_user"],
                        username=u["username"],
                        sign_up_date=u["sign_up_date"],
                        name=u["driver_name"],
                        phone_number=u["driver_phone"],
                        vehicle_type=u["vehicle_type"],
                        availability=u["availability"],
                    )

                elif u["user_type"] == "admin":
                    obj = Admin(
                        id_user=u["id_user"],
                        username=u["username"],
                        sign_up_date=u["sign_up_date"],
                        name=u["admin_name"],
                        phone_number=u["admin_phone"],
                    )

                else:
                    continue

                # Inject private attributes
                obj._hash_password = u["hash_password"]
                obj._salt = u["salt"]

                users.append(obj)

            return users

        except Exception as e:
            logging.error(f"Failed to fetch users: {e}")
            return []

    def add_user(self, user: Union[Customer, Driver, Admin]) -> Optional[Union[Customer, Driver, Admin]]:
        if isinstance(user, Customer):
            user_type = "customer"
        elif isinstance(user, Driver):
            user_type = "driver"
        else:
            user_type = "admin"

        try:
            result = self.db_connector.sql_query(
                """
                INSERT INTO "user" (id_user, username, hash_password, salt, user_type, sign_up_date)
                VALUES (DEFAULT, %(username)s, %(hash_password)s, %(salt)s, %(user_type)s, %(sign_up_date)s)
                RETURNING id_user;
                """,
                {
                    "username": user.username,
                    "hash_password": user._hash_password,
                    "salt": user._salt,
                    "user_type": user_type,
                    "sign_up_date": date.today(),
                },
                "one",
            )

            id_user = result["id_user"]

            if user_type == "customer":
                self.db_connector.sql_query(
                    """
                    INSERT INTO customer (id_user, name, phone_number)
                    VALUES (%(id_user)s, %(name)s, %(phone_number)s)
                    """,
                    {"id_user": id_user, "name": user.name, "phone_number": user.phone_number},
                    None,
                )

            elif user_type == "driver":
                self.db_connector.sql_query(
                    """
                    INSERT INTO driver (id_user, name, phone_number, vehicle_type, availability)
                    VALUES (%(id_user)s, %(name)s, %(phone_number)s, %(vehicle_type)s, %(availability)s)
                    """,
                    {
                        "id_user": id_user,
                        "name": user.name,
                        "phone_number": user.phone_number,
                        "vehicle_type": user.vehicle_type,
                        "availability": user.availability,
                    },
                    None,
                )

            else:  # admin
                self.db_connector.sql_query(
                    """
                    INSERT INTO admin (id_user, name, phone_number)
                    VALUES (%(id_user)s, %(name)s, %(phone_number)s)
                    """,
                    {"id_user": id_user, "name": user.name, "phone_number": user.phone_number},
                    None,
                )

            return self.find_user_by_id(id_user)

        except Exception as e:
            logging.error(f"Failed to add user {user.username}: {e}")
            return None

    def update_user(self, user: Union[Customer, Driver, Admin]) -> Optional[Union[Customer, Driver, Admin]]:
        try:
            if isinstance(user, Customer):
                user_type = "customer"
            elif isinstance(user, Driver):
                user_type = "driver"
            else:
                user_type = "admin"

            self.db_connector.sql_query(
                """
                UPDATE "user"
                SET username = %(username)s,
                    hash_password = %(hash_password)s,
                    user_type = %(user_type)s
                WHERE id_user = %(id_user)s
                """,
                {
                    "id_user": user.id_user,
                    "username": user.username,
                    "hash_password": user._hash_password,
                    "user_type": user_type,
                },
                None,
            )

            if user_type == "customer":
                self.db_connector.sql_query(
                    """
                    UPDATE customer
                    SET name = %(name)s,
                        phone_number = %(phone_number)s
                    WHERE id_user = %(id_user)s
                    """,
                    {
                        "id_user": user.id_user,
                        "name": user.name,
                        "phone_number": user.phone_number,
                    },
                    None,
                )

            elif user_type == "driver":
                self.db_connector.sql_query(
                    """
                    UPDATE driver
                    SET name = %(name)s,
                        phone_number = %(phone_number)s,
                        vehicle_type = %(vehicle_type)s,
                        availability = %(availability)s
                    WHERE id_user = %(id_user)s
                    """,
                    {
                        "id_user": user.id_user,
                        "name": user.name,
                        "phone_number": user.phone_number,
                        "vehicle_type": user.vehicle_type,
                        "availability": user.availability,
                    },
                    None,
                )

            else:  # admin
                self.db_connector.sql_query(
                    """
                    UPDATE admin
                    SET name = %(name)s,
                        phone_number = %(phone_number)s
                    WHERE id_user = %(id_user)s
                    """,
                    {
                        "id_user": user.id_user,
                        "name": user.name,
                        "phone_number": user.phone_number,
                    },
                    None,
                )

            return self.find_user_by_id(user.id_user)

        except Exception as e:
            logging.error(f"Failed to update user {user.id_user}: {e}")
            return None

    def delete_user(self, id_user: int) -> bool:
        try:
            user = self.find_user_by_id(id_user)
            if not user:
                logging.warning(f"User {id_user} not found, cannot delete")
                return False

            if isinstance(user, Customer):
                self.db_connector.sql_query(
                    "DELETE FROM customer WHERE id_user = %(id_user)s",
                    {"id_user": id_user},
                    None,
                )

            elif isinstance(user, Driver):
                self.db_connector.sql_query(
                    "DELETE FROM driver WHERE id_user = %(id_user)s",
                    {"id_user": id_user},
                    None,
                )

            else:  # admin
                self.db_connector.sql_query(
                    "DELETE FROM admin WHERE id_user = %(id_user)s",
                    {"id_user": id_user},
                    None,
                )

            self.db_connector.sql_query(
                'DELETE FROM "user" WHERE id_user = %(id_user)s',
                {"id_user": id_user},
                None,
            )

            return True

        except Exception as e:
            logging.error(f"Failed to delete user {id_user}: {e}")
            return False
