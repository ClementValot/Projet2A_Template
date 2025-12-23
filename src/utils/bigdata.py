import random
import re

import phonenumbers
from dotenv import load_dotenv
from faker import Faker

from src.DAO.DBConnector import DBConnector
from src.Service.password_service import PasswordService

load_dotenv()


class ResetDatabase:
    """
    Resetting the database using DBConnector and SQL files and add 10 000 fake users.
    """

    def __init__(self):
        self.fake = Faker("fr_FR")
        self.db_connector = DBConnector()
        self.service = PasswordService()

    def generate_bulk_users(self, user_count=10000):
        next_id = 14
        user_sql_values = []
        customer_sql_values = []
        driver_sql_values = []

        target_drivers = 100
        target_customers = user_count - target_drivers
        user_types = ["driver"] * target_drivers + ["customer"] * target_customers
        random.shuffle(user_types)

        vehicle_types = ["car", "bike"]

        for i in range(user_count):
            id_user = next_id + i

            name = self.fake.name().replace("'", "''")
            username = self.fake.user_name().replace("'", "''")
            phone_number = self.fake.phone_number()

            phone_number_clean = re.sub(r"[^\d+]", "", phone_number)
            if phone_number_clean.startswith("+"):
                number = phonenumbers.parse(phone_number_clean, None)
            else:
                number = phonenumbers.parse(phone_number_clean, "FR")

            phone_number = phonenumbers.format_number(number, phonenumbers.PhoneNumberFormat.INTERNATIONAL)

            password = self.fake.password()
            salt = self.service.create_salt()
            hashed_password = self.service.hash_password(password, salt)
            user_type = user_types[i]
            sign_up_date = self.fake.date()

            user_sql_values.append(
                f"({id_user}, '{username}', '{hashed_password}', '{salt}', '{user_type}', '{sign_up_date}')"
            )
            if user_type == "customer":
                customer_sql_values.append(f"({id_user}, '{name}', '{phone_number}')")

            elif user_type == "driver":
                vehicle = random.choice(vehicle_types)
                availability = random.choice(["TRUE", "FALSE"])
                driver_sql_values.append(f"({id_user}, '{name}', '{phone_number}', '{vehicle}', {availability})")

        full_query_user = (
            "INSERT INTO fd.user (id_user, username, hash_password, salt, user_type, sign_up_date) VALUES "
        )
        full_query_user += ", ".join(user_sql_values) + ";"

        full_query_customer = "INSERT INTO fd.customer (id_user, name, phone_number) VALUES "
        full_query_customer += ", ".join(customer_sql_values) + ";"

        full_query_driver = "INSERT INTO fd.driver (id_user, name, phone_number, vehicle_type, availability) VALUES "
        full_query_driver += ", ".join(driver_sql_values) + ";"

        try:
            self.db_connector.sql_query(full_query_user, return_type=None)
            print(f"{user_count} users successfully added.")

            self.db_connector.sql_query(full_query_customer, return_type=None)
            print(f"{len(customer_sql_values)} customer added.")

            self.db_connector.sql_query(full_query_driver, return_type=None)
            print(f"{len(driver_sql_values)} drivers added.")

        except Exception as e:
            print(f"Error during mass insertion of users : {e}")
            raise

        self.db_connector.sql_query("SELECT setval('fd.user_id_user_seq', (SELECT MAX(id_user) FROM fd.user));"
            "SELECT setval('fd.address_id_address_seq', (SELECT MAX(id_address) FROM fd.address));"
            "SELECT setval('fd.item_id_item_seq', (SELECT MAX(id_item) FROM fd.item));"
            "SELECT setval('fd.bundle_id_bundle_seq', (SELECT MAX(id_bundle) FROM fd.bundle));"
            "SELECT setval('fd.order_id_order_seq', (SELECT MAX(id_order) FROM fd.order));"
            "SELECT setval('fd.delivery_id_delivery_seq', (SELECT MAX(id_delivery) FROM fd.delivery));")

    def generate_bulk_orders(self, order_count=1000):
        pass

    def lancer(self):
        print("Database reset")

        try:
            with open("data/init_db.sql", encoding="utf-8") as init_db:
                init_db_as_string = init_db.read()

            with open("data/pop_db.sql", encoding="utf-8") as pop_db:
                pop_db_as_string = pop_db.read()

            self.db_connector.sql_query(init_db_as_string, return_type=None)
            self.db_connector.sql_query(pop_db_as_string, return_type=None)

            self.generate_bulk_users()

            print("Database reset - Complete")
            return True

        except FileNotFoundError as e:
            print(f"Error: SQL file not found : {e}")
            raise
        except Exception as e:
            print(f"Error during reset : {e}")
            raise


if __name__ == "__main__":
    ResetDatabase().lancer()
