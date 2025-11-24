from datetime import datetime

import pytest


class TestItemDAO:
    def test_create_item(self, item_dao, clean_database, sample_item_data):
        item = item_dao.create_item(**sample_item_data)

        assert item is not None
        assert item.item_id > 0
        assert item.orderable_id > 0
        assert item.item_name == sample_item_data["item_name"]
        assert item.item_price == sample_item_data["item_price"]
        assert item.item_type == sample_item_data["item_type"]
        assert item.item_description == sample_item_data["item_description"]
        assert item.item_stock == sample_item_data["item_stock"]
        assert item.is_in_menu is True

    def test_get_item_by_id_exists(self, item_dao, sample_item, clean_database):
        retrieved_item = item_dao.get_item_by_id(sample_item.item_id)

        assert retrieved_item is not None
        assert retrieved_item.item_id == sample_item.item_id
        assert retrieved_item.item_name == sample_item.item_name
        assert retrieved_item.item_price == sample_item.item_price

    def test_get_item_by_id_not_exists(self, item_dao, clean_database):
        retrieved_item = item_dao.get_item_by_id(9999)

        assert retrieved_item is None

    def test_get_item_by_orderable_id(self, item_dao, sample_item, clean_database):
        retrieved_item = item_dao.get_item_by_orderable_id(sample_item.orderable_id)

        assert retrieved_item is not None
        assert retrieved_item.item_id == sample_item.item_id
        assert retrieved_item.orderable_id == sample_item.orderable_id

    def test_get_all_items_empty(self, item_dao, clean_database):
        items = item_dao.get_all_items()

        assert items == []

    def test_get_all_items_multiple(self, item_dao, multiple_items, clean_database):
        items = item_dao.get_all_items()

        assert items is not None
        assert len(items) == 3

    def test_update_item_single_field(self, item_dao, sample_item, clean_database):
        update_data = {"item_stock": 25}
        updated_item = item_dao.update_item(sample_item.item_id, update_data)

        assert updated_item.item_stock == 25
        assert updated_item.item_name == sample_item.item_name
        assert updated_item.item_price == sample_item.item_price

    def test_update_item_multiple_fields(self, item_dao, sample_item, clean_database):
        update_data = {
            "item_name": "Galette Complète",
            "item_price": 5.0,
            "item_stock": 30,
        }
        updated_item = item_dao.update_item(sample_item.item_id, update_data)

        assert updated_item.item_name == "Galette Complète"
        assert updated_item.item_price == 5.0
        assert updated_item.item_stock == 30

    def test_update_item_empty_dict_raises_error(self, item_dao, sample_item, clean_database):
        with pytest.raises(ValueError, match="At least one value should be updated"):
            item_dao.update_item(sample_item.item_id, {})

    def test_update_item_invalid_field_raises_error(
        self, item_dao, sample_item_data, clean_database
    ):
        """Test updating with wrong field"""
        created_item = item_dao.create_item(**sample_item_data)

        with pytest.raises(ValueError, match="not a parameter of Item"):
            item_dao.update_item(created_item.item_id, {"invalid_field": "value"})

    def test_delete_item_not_in_bundle(self, item_dao, sample_item, clean_database):
        item_id = sample_item.item_id

        item_dao.delete_item_by_id(item_id)

        retrieved_item = item_dao.get_item_by_id(item_id)
        assert retrieved_item is None

    def test_delete_item_in_bundle_raises_error(
        self, item_dao, bundle_dao, multiple_items, clean_database
    ):
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
            item_dao.delete_item_by_id(multiple_items[0].item_id)

    def test_item_is_in_bundle_false(self, item_dao, sample_item, clean_database):
        is_in_bundle = item_dao._item_is_in_bundle(sample_item.item_id)

        assert is_in_bundle is False

    def test_item_is_in_bundle_true(self, item_dao, bundle_dao, multiple_items, clean_database):
        bundle_items = {multiple_items[0]: 1}

        bundle_dao.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=20,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        is_in_bundle = item_dao._item_is_in_bundle(multiple_items[0].item_id)

        assert is_in_bundle is True
