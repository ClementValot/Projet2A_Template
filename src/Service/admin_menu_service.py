from typing import List, Optional

from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.itemDAO import ItemDAO
from src.Model.abstract_bundle import AbstractBundle
from src.Model.discounted_bundle import DiscountedBundle
from src.Model.item import Item
from src.Model.one_item_bundle import OneItemBundle
from src.Model.predefined_bundle import PredefinedBundle


class AdminMenuService:
    def __init__(self, db_connector: DBConnector):
        """
        Initializes the service and injects dependencies into the DAOs.
        """
        self.item_dao = ItemDAO(db_connector=db_connector)
        self.bundle_dao = BundleDAO(db_connector=db_connector, item_dao=self.item_dao)

    def create_item(self, name: str, desc: str, price: float, stock: int, availability: bool, item_type: str) -> None:
        """
        Validates and creates a new item in the database.
        """
        existing_items = self.item_dao.find_all_items()
        if any(i.name.lower() == name.lower() for i in existing_items):
            raise ValueError(f"An item with the name '{name}' already exists.")

        if price < 0:
            raise ValueError("Price must be positive.")
        if stock < 0:
            raise ValueError("Stock cannot be negative.")
        if stock == 0 and availability:
            raise ValueError("Zero stock implies non-availability.")

        new_item = Item(
            name=name, description=desc, price=price, stock=stock, availability=availability, item_type=item_type
        )
        created_item = self.item_dao.add_item(new_item)
        if not created_item:
            raise Exception(f"Failed to create item: {name}")

    def update_item(
        self,
        id: int,
        name: Optional[str] = None,
        desc: Optional[str] = None,
        price: Optional[float] = None,
        stock: Optional[int] = None,
        availability: Optional[bool] = None,
        item_type: Optional[str] = None,
    ) -> None:
        """
        Finds an existing item by ID, validates new data, and updates it.
        """
        item = self.item_dao.find_item_by_id(id)
        if not item:
            raise ValueError(f"No item found with ID {id}.")

        if name is not None and name.lower() != item.name.lower():
            existing_items = self.item_dao.find_all_items()
            if any(i.name.lower() == name.lower() for i in existing_items):
                raise ValueError(f"An item with the name '{name}' already exists.")
            item.name = name

        if price is not None:
            if price < 0:
                raise ValueError("Price must be positive.")
            item.price = price

        if stock is not None:
            if stock < 0:
                raise ValueError("Stock cannot be negative.")
            item.stock = stock

        if availability is not None:
            item.availability = availability

        if item.stock == 0 and item.availability:
            raise ValueError("Zero stock implies non-availability.")

        if desc is not None:
            item.description = desc
        if item_type is not None:
            item.item_type = item_type

        updated_item = self.item_dao.update_item(item)
        if not updated_item:
            raise Exception(f"Failed to update item: {id}")

    def delete_item(self, id: int) -> None:
        """
        Finds an item by ID and deletes it from the database.
        """
        item = self.item_dao.find_item_by_id(id)
        if not item:
            raise ValueError(f"No item found with ID {id}.")

        if not self.item_dao.delete_item(id):
            raise Exception(f"Failed to delete item: {id}")

    def create_predefined_bundle(self, name: str, description: str, item_ids: list[int], price: float) -> None:
        """
        Validates and creates a new predefined (fixed-price) bundle.
        """
        if price <= 0:
            raise ValueError("Price must be positive.")
        if not item_ids:
            raise ValueError("Composition must contain at least 2 items.")

        composition: list = self.item_dao.get_items_by_ids(item_ids)
        if not composition or len(composition) != len(item_ids):
            raise ValueError("One or more item IDs provided in the composition were not found.")

        all_bundles = self.bundle_dao.find_all_bundles()

        if any(b.name.lower() == name.lower() for b in all_bundles):
            raise ValueError(f"A bundle with the name '{name}' already exists.")

        new_composition_ids = sorted(item_ids)

        for existing_bundle in all_bundles:
            if isinstance(existing_bundle, PredefinedBundle):
                existing_ids = sorted([i.id_item for i in existing_bundle.composition])
                if existing_ids == new_composition_ids:
                    raise ValueError("A predefined bundle with this exact composition already exists.")

        new_bundle = PredefinedBundle(name=name, description=description, composition=composition, price=price)

        created_bundle = self.bundle_dao.add_predefined_bundle(new_bundle)
        if not created_bundle:
            raise Exception(f"Failed to create predefined bundle: {name}")

    def create_discounted_bundle(
        self, name: str, description: str, required_item_types: list[str], discount: float
    ) -> None:
        """
        Validates and creates a new bundle that applies a discount.
        """
        if not (0 < discount < 1):
            raise ValueError("Discount must be between 0 and 1 (exclusive).")

        if not required_item_types:
            raise ValueError("Item types cannot be empty.")

        if not all(isinstance(t, str) and t.strip() for t in required_item_types):
            raise ValueError("All item types must be valid, non-empty strings.")

        required_item_types = [t.lower() for t in required_item_types]

        all_bundles = self.bundle_dao.find_all_bundles()

        if any(b.name.lower() == name.lower() for b in all_bundles):
            raise ValueError(f"A bundle with the name '{name}' already exists.")

        new_types_sorted = sorted(required_item_types)

        for existing_bundle in all_bundles:
            if isinstance(existing_bundle, DiscountedBundle):
                existing_types = sorted([t.lower() for t in existing_bundle.required_item_types])
                if existing_types == new_types_sorted:
                    raise ValueError("A discounted bundle with this exact configuration of item types already exists.")

        new_bundle = DiscountedBundle(
            name=name, description=description, required_item_types=required_item_types, discount=discount
        )

        created_bundle = self.bundle_dao.add_discounted_bundle(new_bundle)
        if not created_bundle:
            raise Exception(f"Failed to create discounted bundle: {name}")

    def delete_bundle(self, id: int) -> None:
        """
        Finds a bundle by ID and deletes it from the database.
        """
        if not self.bundle_dao.find_bundle_by_id(id):
            raise ValueError(f"No bundle found with ID {id}.")

        if not self.bundle_dao.delete_bundle(id):
            raise Exception(f"Failed to delete bundle: {id}")

    def list_items(self) -> list[Item]:
        """
        Retrieves a list of all items from the database.
        """
        return self.item_dao.find_all_items()

    def list_bundles(self) -> list[AbstractBundle]:
        """
        Retrieves a list of all bundles from the database.
        """
        return self.bundle_dao.find_all_bundles()

    def update_predefined_bundle(
        self,
        id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        item_ids: Optional[List[int]] = None,
        price: Optional[float] = None,
    ) -> None:
        """
        Validates and updates an existing predefined (fixed-price) bundle.
        """
        bundle = self.bundle_dao.find_bundle_by_id(id)
        if not bundle:
            raise ValueError(f"No bundle found with ID {id}.")

        if not isinstance(bundle, PredefinedBundle):
            raise TypeError(f"Bundle with ID {id} is not a predefined bundle.")

        if name is not None:
            if name.lower() != bundle.name.lower():
                all_bundles = self.bundle_dao.find_all_bundles()
                if any(b.name.lower() == name.lower() for b in all_bundles):
                    raise ValueError(f"A bundle with the name '{name}' already exists.")
            bundle.name = name

        if description is not None:
            bundle.description = description

        if not hasattr(bundle, "price") or bundle.price is None:
            raise Exception(f"Price is missing on existing bundle {id}. Check DAO loading.")

        if price is not None:
            if price <= 0:
                raise ValueError("Price must be positive.")
            bundle.price = price

        if bundle.description is None:
            bundle.description = ""

        if item_ids is not None:
            if not item_ids or len(item_ids) < 2:
                raise ValueError("Composition must contain at least 2 items.")

            composition: list = self.item_dao.get_items_by_ids(item_ids)
            if not composition or len(composition) != len(item_ids):
                raise ValueError("One or more item IDs provided in the composition were not found.")

            new_ids_sorted = sorted(item_ids)
            all_bundles = self.bundle_dao.find_all_bundles()
            for existing in all_bundles:
                if isinstance(existing, PredefinedBundle) and existing.id_bundle != id:
                    existing_ids = sorted([i.id_item for i in existing.composition])
                    if existing_ids == new_ids_sorted:
                        raise ValueError("Another predefined bundle with this exact composition already exists.")

            bundle.composition = composition

        updated_bundle = self.bundle_dao.update_bundle(bundle)
        if not updated_bundle:
            raise Exception(f"Failed to update predefined bundle: {id}")

    def update_discounted_bundle(
        self,
        id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        required_item_types: Optional[List[str]] = None,
        discount: Optional[float] = None,
    ) -> None:
        """
        Validates and updates an existing discounted bundle.
        """
        bundle = self.bundle_dao.find_bundle_by_id(id)
        if not bundle:
            raise ValueError(f"No bundle found with ID {id}.")

        if not isinstance(bundle, DiscountedBundle):
            raise TypeError(f"Bundle with ID {id} is not a discounted bundle.")

        if name is not None:
            if name.lower() != bundle.name.lower():
                all_bundles = self.bundle_dao.find_all_bundles()
                if any(b.name.lower() == name.lower() for b in all_bundles):
                    raise ValueError(f"A bundle with the name '{name}' already exists.")
            bundle.name = name

        if description is not None:
            bundle.description = description

        if discount is not None:
            if not (0 < discount < 1):
                raise ValueError("Discount must be between 0 and 1 (exclusive).")
            bundle.discount = discount

        if required_item_types is not None:
            if not required_item_types:
                raise ValueError("Item types cannot be empty.")

            if not all(isinstance(t, str) and t.strip() for t in required_item_types):
                raise ValueError("All item types must be valid, non-empty strings.")

            normalized_types = [t.lower() for t in required_item_types]

            new_types_sorted = sorted(normalized_types)
            all_bundles = self.bundle_dao.find_all_bundles()
            for existing in all_bundles:
                if isinstance(existing, DiscountedBundle) and existing.id_bundle != id:
                    existing_types = sorted([t.lower() for t in existing.required_item_types])
                    if existing_types == new_types_sorted:
                        raise ValueError(
                            "Another discounted bundle with this exact item types configuration already exists."
                        )

            bundle.required_item_types = normalized_types

        updated_bundle = self.bundle_dao.update_bundle(bundle)
        if not updated_bundle:
            raise Exception(f"Failed to update discounted bundle: {id}")
