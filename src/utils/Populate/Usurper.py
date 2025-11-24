from datetime import timedelta
from random import randint
from typing import Dict, List

from faker import Faker

from src.DAO.DBConnector import DBConnector


class Usurper:
    fake: Faker
    db_connector: DBConnector

    def __init__(
        self,
        fake: Faker,
        db_connector: DBConnector,
        n_customers: int = 1000,
        n_drivers: int = 10,
        n_items: int = 30,
        n_bundles: int = 10,
        n_orders: int = 70,
        n_deliveries: int = 30,
        schema="project",
    ):
        self.fake = fake
        self.db_connector = db_connector
        self.n_customers = n_customers
        self.n_drivers = n_drivers
        self.n_items = n_items
        self.n_bundles = n_bundles
        self.n_orders = n_orders
        self.n_deliveries = n_deliveries
        self.schema = schema

    def create_addresses_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_customers + 1)
        data = {}
        data["address_number"] = [str(randint(1, 50)) for _ in n]
        data["address_street"] = [f"'{self.fake.street_name()}'" for _ in n]
        data["address_city"] = [f"'{self.fake.city()}'" for _ in n]
        data["address_postal_code"] = [f"'{str(self.fake.postcode())}'" for _ in n]
        data["address_country"] = ["'France'" for _ in n]

        return data

    def create_customers_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_customers + 1)
        data = {}
        first_names = [self.fake.first_name() for _ in n]
        data["customer_first_name"] = [f"'{name}'" for name in first_names]
        data["customer_last_name"] = [f"'{self.fake.last_name()}'" for _ in n]
        data["customer_created_at"] = [
            f"'{self.fake.date_time_between(start_date='-2y', end_date='now')}'" for _ in n
        ]
        data["customer_phone"] = [f"'{self.fake.phone_number().strip()[0:15]}'" for _ in n]
        data["customer_mail"] = [f"'{self.fake.email()}'" for _ in n]
        salts, pws = zip(
            *[self.fake.create_hash_password(name) for name in first_names], strict=False
        )
        data["customer_password_hash"] = [f"'{pw}'" for pw in pws]
        data["customer_salt"] = [f"'{salt}'" for salt in salts]
        data["customer_address_id"] = [str(i) for i in n]

        return data

    def create_orderables_data(self) -> Dict[str, List[str]]:
        n_total = self.n_items + self.n_bundles
        n = range(1, n_total + 1)
        data = {}
        orderable_types = ["'item'" for _ in range(self.n_items)] + [
            "'bundle'" for _ in range(self.n_bundles)
        ]
        data["orderable_type"] = orderable_types

        data["orderable_image_name"] = [f"'image_{i}'" for i in n]
        data["orderable_image_url"] = ["NULL" for _ in n]
        data["is_in_menu"] = ["TRUE" if randint(0, 100) > 30 else "FALSE" for _ in n]

        return data

    def create_items_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_items + 1)
        data = {}
        data["orderable_id"] = [str(i) for i in n]

        data["item_name"] = [
            f"'{self.fake.word().capitalize().replace("'", ' ')} {self.fake.item_name()}'"
            for _ in n
        ]
        data["item_price"] = [f"{round(randint(5, 50) + randint(0, 99) / 100, 2)}" for _ in n]
        data["item_type"] = [f"'{self.fake.item_type()}'" for _ in n]
        data["item_description"] = [f"'{self.fake.word().replace("'", ' ')}'" for _ in n]
        data["item_stock"] = [str(randint(0, 100)) for _ in n]

        return data

    def create_bundles_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_bundles + 1)
        data = {}
        data["orderable_id"] = [str(self.n_items + i) for i in n]

        data["bundle_name"] = [
            f"'{self.fake.bundle_name()} {self.fake.word().capitalize().replace("'", ' ')}'"
            for _ in n
        ]
        data["bundle_reduction"] = [str(randint(10, 40)) for _ in n]
        data["bundle_description"] = [f"'{self.fake.word().replace("'", ' ')}'" for _ in n]

        start_dates = [self.fake.date_between(start_date="-1y", end_date="today") for _ in n]
        data["bundle_availability_start_date"] = [f"'{date}'" for date in start_dates]
        data["bundle_availability_end_date"] = [
            f"'{date + timedelta(days=randint(30, 365))}'" for date in start_dates
        ]

        return data

    def create_bundle_items_data(self) -> Dict[str, List[str]]:
        data = {}
        bundle_ids = []
        item_ids = []
        quantities = []

        for bundle_id in range(1, self.n_bundles + 1):
            n_items_in_bundle = randint(2, min(5, self.n_items))
            selected_items = set()

            while len(selected_items) < n_items_in_bundle:
                item_id = randint(1, self.n_items)
                selected_items.add(item_id)

            for item_id in selected_items:
                bundle_ids.append(str(bundle_id))
                item_ids.append(str(item_id))
                quantities.append(str(randint(1, 3)))

        data["bundle_id"] = bundle_ids
        data["item_id"] = item_ids
        data["item_quantity"] = quantities

        return data

    def create_drivers_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_drivers + 1)
        data = {}

        first_names = [self.fake.first_name() for _ in n]
        data["driver_first_name"] = [f"'{name}'" for name in first_names]
        data["driver_last_name"] = [f"'{self.fake.last_name()}'" for _ in n]
        data["driver_created_at"] = [
            f"'{self.fake.date_time_between(start_date='-1y', end_date='now')}'" for _ in n
        ]
        salts, pws = zip(
            *[self.fake.create_hash_password(name) for name in first_names], strict=False
        )
        data["driver_password_hash"] = [f"'{pw}'" for pw in pws]
        data["driver_salt"] = [f"'{salt}'" for salt in salts]
        data["driver_is_delivering"] = [f"'{self.fake.boolean()}'" for _ in n]
        data["driver_phone"] = [f"'{self.fake.phone_number().strip()[0:15]}'" for _ in n]

        return data

    def create_orders_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_orders + 1)
        data = {}
        data["order_customer_id"] = [str(randint(1, self.n_customers)) for _ in n]
        data["order_state"] = [str(randint(0, 5)) for _ in n]

        created_dates = [self.fake.date_time_between(start_date="-6m", end_date="now") for _ in n]
        data["order_created_at"] = [f"'{date}'" for date in created_dates]

        data["order_paid_at"] = [
            f"'{date + timedelta(minutes=randint(1, 60))}'" if randint(0, 100) > 20 else "NULL"
            for date in created_dates
        ]

        return data

    def create_order_contents_data(self) -> Dict[str, List[str]]:
        data = {}
        order_ids = []
        orderable_ids = []
        quantities = []

        total_orderables = self.n_items + self.n_bundles

        for order_id in range(1, self.n_orders + 1):
            n_items_in_order = randint(1, 5)
            selected_orderables = set()

            while len(selected_orderables) < n_items_in_order:
                orderable_id = randint(1, total_orderables)
                selected_orderables.add(orderable_id)

            for orderable_id in selected_orderables:
                order_ids.append(str(order_id))
                orderable_ids.append(str(orderable_id))
                quantities.append(str(randint(1, 4)))

        data["order_id"] = order_ids
        data["orderable_id"] = orderable_ids
        data["orderable_quantity"] = quantities

        return data

    def create_deliveries_data(self) -> Dict[str, List[str]]:
        n = range(1, self.n_deliveries + 1)

        data = {}
        order_ids = list(set([randint(1, self.n_orders) for _ in range(self.n_deliveries * 2)]))[
            : self.n_deliveries
        ]
        data["delivery_order_id"] = [str(order_id) for order_id in order_ids]
        data["delivery_driver_id"] = [str(randint(1, self.n_drivers)) for _ in n]
        data["delivery_created_at"] = [
            f"'{self.fake.date_time_between(start_date='-3m', end_date='now')}'" for _ in n
        ]
        data["delivery_state"] = [str(randint(0, 2)) for _ in n]

        return data

    def dict_to_query(self, dict_table: Dict[str, List[str]], table_name: str) -> str:
        varnames = ", ".join(list(dict_table.keys()))
        query = f"INSERT INTO {self.schema}.{table_name} ({varnames})\nVALUES\n"

        n = len(list(dict_table.values())[0])
        for i in range(n):
            values = "(" + ", ".join([elem[i] for elem in dict_table.values()]) + ")"
            values += ",\n" if i != n - 1 else ";"
            query += values

        return query

    def populate_database(self) -> bool:
        try:
            print("Creating Addresses...")
            addresses_data = self.create_addresses_data()
            addresses_query = self.dict_to_query(addresses_data, "Addresses")
            self.db_connector.sql_query(addresses_query, return_type="none")

            print("Creating Customers...")
            customers_data = self.create_customers_data()
            customers_query = self.dict_to_query(customers_data, "Customers")
            self.db_connector.sql_query(customers_query, return_type="none")

            print("Creating Drivers...")
            drivers_data = self.create_drivers_data()
            drivers_query = self.dict_to_query(drivers_data, "Drivers")
            self.db_connector.sql_query(drivers_query, return_type="none")

            print("Creating Orderables...")
            orderables_data = self.create_orderables_data()
            orderables_query = self.dict_to_query(orderables_data, "Orderables")
            self.db_connector.sql_query(orderables_query, return_type="none")

            print("Creating Items...")
            items_data = self.create_items_data()
            items_query = self.dict_to_query(items_data, "Items")
            self.db_connector.sql_query(items_query, return_type="none")

            print("Creating Bundles...")
            bundles_data = self.create_bundles_data()
            bundles_query = self.dict_to_query(bundles_data, "Bundles")
            self.db_connector.sql_query(bundles_query, return_type="none")

            print("Creating Bundle_Items...")
            bundle_items_data = self.create_bundle_items_data()
            bundle_items_query = self.dict_to_query(bundle_items_data, "Bundle_Items")
            self.db_connector.sql_query(bundle_items_query, return_type="none")

            print("Creating Orders...")
            orders_data = self.create_orders_data()
            orders_query = self.dict_to_query(orders_data, "Orders")
            self.db_connector.sql_query(orders_query, return_type="none")

            print("Creating Order_contents...")
            order_contents_data = self.create_order_contents_data()
            order_contents_query = self.dict_to_query(order_contents_data, "Order_contents")
            self.db_connector.sql_query(order_contents_query, return_type="none")

            print("Creating Deliveries...")
            deliveries_data = self.create_deliveries_data()
            deliveries_query = self.dict_to_query(deliveries_data, "Deliveries")
            self.db_connector.sql_query(deliveries_query, return_type="none")

            print("Database populated successfully!")
            return True

        except Exception as e:
            print(f"Error populating database: {e}")
            return False
