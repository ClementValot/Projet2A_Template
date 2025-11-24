from datetime import datetime

import pytest


class TestItemService:
    def test_get_item_by_id_exists(self, item_service, sample_item, clean_database):
        """Test getting an item by id"""
        retrieved_item = item_service.get_item_by_id(sample_item.item_id)

        assert retrieved_item is not None
        assert retrieved_item.item_id == sample_item.item_id
        assert retrieved_item.item_name == sample_item.item_name

    def test_get_item_by_id_not_exists(self, item_service, clean_database):
        """Test getting item by non-existing id raises error"""
        with pytest.raises(ValueError, match="Cannot find: item with ID 9999 not found"):
            item_service.get_item_by_id(9999)

    def test_get_all_items_empty(self, item_service, clean_database):
        """Test getting all items when there are none"""
        items = item_service.get_all_items()

        assert items == []

    def test_get_all_items_multiple(self, item_service, multiple_items, clean_database):
        """Test getting all items"""
        items = item_service.get_all_items()

        assert items is not None
        assert len(items) == 3

    def test_create_item(self, item_service, sample_item_data, clean_database):
        """Test creating an item"""
        created_item = item_service.create_item(**sample_item_data)

        assert created_item is not None
        assert created_item.item_id > 0
        assert created_item.item_name == sample_item_data["item_name"]
        assert created_item.item_price == sample_item_data["item_price"]
        assert created_item.item_type == sample_item_data["item_type"]

    def test_update_item_multiple_fields(self, item_service, sample_item, clean_database):
        """Test updating multiple fields"""
        update_data = {
            "item_name": "Galette Complète",
            "item_price": 5.0,
            "item_stock": 30,
        }
        updated_item = item_service.update_item(sample_item.item_id, update_data)

        assert updated_item.item_name == "Galette Complète"
        assert updated_item.item_price == 5.0
        assert updated_item.item_stock == 30

    def test_update_item_not_exists(self, item_service, clean_database):
        """Test updating non-existing item raises error"""
        with pytest.raises(ValueError, match="Cannot find: item with ID 9999 not found"):
            item_service.update_item(9999, {"item_stock": 25})

    def test_delete_item_exists(self, item_service, sample_item, clean_database):
        """Test deleting an item"""
        item_service.delete_item(sample_item.item_id)

        with pytest.raises(ValueError, match="Cannot find: item with ID"):
            item_service.get_item_by_id(sample_item.item_id)

    def test_delete_item_not_exists(self, item_service, clean_database):
        """Test deleting non-existing item raises error"""
        with pytest.raises(ValueError, match="Cannot find: item with ID 9999 not found"):
            item_service.delete_item(9999)

    def test_delete_item_in_bundle_raises_error(
        self, item_service, bundle_dao, multiple_items, clean_database
    ):
        """Test deleting item in bundle raises error"""

        bundle_items = {multiple_items[0]: 1}
        bundle_dao.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=20,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        with pytest.raises(ValueError, match="item is in a bundle"):
            item_service.delete_item(multiple_items[0].item_id)

    def test_create_item_invalid_price(self, item_service, sample_item_data, clean_database):
        """Test creating an item with invalid price raises error"""
        sample_item_data["item_price"] = 0  # Doit être strictement positif

        with pytest.raises(ValueError, match="Price must be strictly positive"):
            item_service.create_item(**sample_item_data)

    def test_create_item_negative_price(self, item_service, sample_item_data, clean_database):
        """Test creating an item with negative price raises error"""
        sample_item_data["item_price"] = -5.0  # Doit être strictement positif

        with pytest.raises(ValueError, match="Price must be strictly positive"):
            item_service.create_item(**sample_item_data)

    def test_create_item_negative_stock(self, item_service, sample_item_data, clean_database):
        """Test creating an item with negative stock raises error"""
        sample_item_data["item_stock"] = -10  # Doit être positif

        with pytest.raises(ValueError, match="Stock must be positive"):
            item_service.create_item(**sample_item_data)

    def test_update_item_no_changes(self, item_service, sample_item, clean_database):
        """Test updating item with no changes raises error"""
        update_data = {
            "item_name": None,
            "item_price": None,
        }

        with pytest.raises(ValueError, match="At least one value should be updated"):
            item_service.update_item(sample_item.item_id, update_data)

    def test_update_item_invalid_price(self, item_service, sample_item, clean_database):
        """Test updating item with invalid price raises error"""
        update_data = {"item_price": 0.0}

        with pytest.raises(ValueError, match="Price must be strictly positive"):
            item_service.update_item(sample_item.item_id, update_data)

    def test_update_item_negative_price(self, item_service, sample_item, clean_database):
        """Test updating item with negative price raises error"""
        update_data = {
            "item_price": -5.0  # Doit être strictement positif
        }

        with pytest.raises(ValueError, match="Price must be strictly positive"):
            item_service.update_item(sample_item.item_id, update_data)

    def test_update_item_negative_stock(self, item_service, sample_item, clean_database):
        """Test updating item with negative stock raises error"""
        update_data = {
            "item_stock": -10  # Doit être positif
        }

        with pytest.raises(ValueError, match="Stock must be positive"):
            item_service.update_item(sample_item.item_id, update_data)

    def test_update_item_partial_fields(self, item_service, sample_item, clean_database):
        """Test updating only some fields of an item"""
        original_name = sample_item.item_name
        original_type = sample_item.item_type

        update_data = {
            "item_stock": 75  # Seul le stock est modifié
        }

        updated_item = item_service.update_item(sample_item.item_id, update_data)

        assert updated_item.item_stock == 75
        # Les autres champs doivent rester inchangés
        assert updated_item.item_name == original_name
        assert updated_item.item_type == original_type
        assert updated_item.item_price == sample_item.item_price
