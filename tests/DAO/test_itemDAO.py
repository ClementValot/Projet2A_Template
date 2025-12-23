from datetime import date
from typing import Any, Dict, List, Literal, Optional, Union

import pytest

from src.DAO.itemDAO import ItemDAO
from src.Model.item import Item


class MockDBConnector:
    def __init__(self):
        self.users = [{"id_user": 1, "username": "janjak", "user_type": "customer", "sign_up_date": date.today()}]

        self.items = [
            {
                "id_item": 1,
                "name": "Item Existant A",
                "item_type": "side",
                "price": 5.00,
                "description": "Un item de base",
                "stock": 50,
                "availability": True,
            },
            {
                "id_item": 2,
                "name": "Item Existant B",
                "item_type": "main",
                "price": 12.00,
                "description": "Un autre item de base",
                "stock": 25,
                "availability": True,
            },
        ]
        self.next_item_id = 3

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Optional[Union[Literal["one"], Literal["all"], None]] = "one",
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], bool, None]:
        q = " ".join(query.lower().split())

        if "insert into" in q and "item" in q and "returning" in q:
            if not isinstance(data, dict):
                return False

            new_id = self.next_item_id
            self.next_item_id += 1

            description_val = data.get("description")
            stock_val = data.get("stock")
            avail_val = data.get("availability")

            created_item = {
                "id_item": new_id,
                "name": data["name"],
                "item_type": data["item_type"],
                "price": data["price"],
                "description": description_val if description_val is not None else "Pas de description.",
                "stock": stock_val if stock_val is not None else 0,
                "availability": avail_val if avail_val is not None else True,
            }

            self.items.append(created_item)
            return created_item

        if "select * from item where id_item in" in q and return_type == "all":
            if isinstance(data, list):
                found_items = [item.copy() for item in self.items if item["id_item"] in data]
                return found_items
            return []

        if "select * from item" in q and return_type == "all":
            return list(self.items)

        if "from item" in q and "where id_item" in q and return_type == "one":
            item_id = None
            if isinstance(data, dict):
                item_id = data.get("id_item")
            elif isinstance(data, (list, tuple)):
                if data:
                    item_id = data[0]

            if item_id:
                for item in self.items:
                    if item["id_item"] == item_id:
                        return item.copy()
            return None

        if "update item" in q and "where id_item" in q:
            item_id_to_update = data.get("id_item")
            for item in self.items:
                if item["id_item"] == item_id_to_update:
                    for key, value in data.items():
                        if key != "id_item":
                            item[key] = value
                    return True
            return False

        if "delete from item" in q and "where id_item" in q:
            item_id_to_delete = None
            if isinstance(data, dict):
                item_id_to_delete = data.get("id_item")
            elif isinstance(data, (list, tuple)):
                if data:
                    item_id_to_delete = data[0]

            if item_id_to_delete is None:
                return False

            initial_count = len(self.items)
            self.items = [item for item in self.items if item["id_item"] != item_id_to_delete]
            return len(self.items) < initial_count

        return None


@pytest.fixture
def item_dao():
    mock_connector = MockDBConnector()
    return ItemDAO(mock_connector)


def test_find_all_items(item_dao):
    """Test finding all items."""
    items = item_dao.find_all_items()
    assert isinstance(items, list)
    assert len(items) == 2
    assert all(isinstance(item, Item) for item in items)


def test_find_item_by_id_existing(item_dao):
    """Test searching for an existing item."""
    item = item_dao.find_item_by_id(1)
    assert item is not None
    assert isinstance(item, Item)
    assert item.id_item == 1


def test_find_item_by_id_non_existing(item_dao):
    """Test searching for a non-existing item."""
    item = item_dao.find_item_by_id(9999)
    assert item is None


def test_add_item(item_dao):
    """Test adding a new item."""
    new_item = Item(id_item=None, name="Test Pizza", item_type="main", price=15.00)

    created_item = item_dao.add_item(new_item)

    assert created_item is not None
    assert created_item.id_item == 3
    assert created_item.name == "Test Pizza"
    assert created_item.price == 15.00

    item_dao.delete_item(created_item.id_item)


def test_update_item(item_dao):
    """Test updating an existing item."""
    item_to_update = item_dao.find_item_by_id(1)

    item_to_update.name = "Test Updated"
    item_to_update.price = 12.00
    success = item_dao.update_item(item_to_update)

    assert success is True

    updated_item = item_dao.find_item_by_id(1)
    assert updated_item.name == "Test Updated"
    assert updated_item.price == 12.00


def test_delete_item(item_dao):
    """Test deleting an item."""
    new_item = Item(id_item=None, name="Test Delete", item_type="main", price=10.00)
    created_item = item_dao.add_item(new_item)
    assert created_item.id_item == 3

    success = item_dao.delete_item(created_item.id_item)
    assert success is True

    deleted_item = item_dao.find_item_by_id(created_item.id_item)
    assert deleted_item is None


def test_add_item_minimal_data(item_dao):
    """Test adding an item with minimal data (checking defaults)."""
    new_item = Item(id_item=None, name="Minimal Side", item_type="side", price=3.50)
    created_item = item_dao.add_item(new_item)

    assert created_item is not None
    assert created_item.name == "Minimal Side"
    assert created_item.price == 3.50

    assert created_item.description == "Pas de description."
    assert created_item.stock == 0
    assert created_item.availability is True

    item_dao.delete_item(created_item.id_item)


def test_update_item_non_existing(item_dao):
    """Test updating a non-existing item."""
    non_existing_item = Item(id_item=9997, name="Should not exist", item_type="side", price=1.00)
    success = item_dao.update_item(non_existing_item)
    assert success is False


def test_delete_item_non_existing(item_dao):
    """Test deleting a non-existing item."""
    success = item_dao.delete_item(9998)
    assert success is False


def test_get_items_by_ids_success(item_dao):
    """Test retrieving multiple items by a list of IDs."""
    items = item_dao.get_items_by_ids([1, 2])

    assert isinstance(items, list)
    assert len(items) == 2
    assert items[0].id_item == 1
    assert items[1].id_item == 2


def test_get_items_by_ids_partial_match(item_dao):
    """Test retrieving items where some IDs exist and others do not."""
    items = item_dao.get_items_by_ids([1, 99])

    assert len(items) == 1
    assert items[0].id_item == 1


def test_get_items_by_ids_empty_input(item_dao):
    """Test retrieving items with an empty input list."""
    items = item_dao.get_items_by_ids([])
    assert items == []


def test_get_items_by_ids_none_found(item_dao):
    """Test retrieving items where no IDs match."""
    items = item_dao.get_items_by_ids([88, 99])
    assert items == []
