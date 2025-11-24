from datetime import datetime

import pytest


class TestBundleDAO:
    def test_create_bundle_simple(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {
            multiple_items[0]: 1,
            multiple_items[1]: 1,
        }

        bundle = bundle_dao.create_bundle(
            bundle_name="Menu Galette",
            bundle_reduction=10,
            bundle_description="Galette + Boisson",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        assert bundle is not None
        assert bundle.bundle_id > 0
        assert bundle.orderable_id > 0
        assert bundle.bundle_name == "Menu Galette"
        assert bundle.bundle_reduction == 10
        assert len(bundle.bundle_items) == 2

    def test_create_bundle_multiple_quantities(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {
            multiple_items[0]: 2,
            multiple_items[1]: 2,
            multiple_items[2]: 1,
        }

        bundle = bundle_dao.create_bundle(
            bundle_name="Menu Complet",
            bundle_reduction=25,
            bundle_description="Menu complet avec dessert",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        assert bundle is not None
        assert len(bundle.bundle_items) == 3

        item_quantities = {item.item_id: qty for item, qty in bundle.bundle_items.items()}
        assert item_quantities[multiple_items[0].item_id] == 2
        assert item_quantities[multiple_items[1].item_id] == 2
        assert item_quantities[multiple_items[2].item_id] == 1

    def test_get_bundle_by_id_exists(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {multiple_items[0]: 1}
        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=15,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        retrieved_bundle = bundle_dao.get_bundle_by_id(created_bundle.bundle_id)

        assert retrieved_bundle is not None
        assert retrieved_bundle.bundle_id == created_bundle.bundle_id
        assert retrieved_bundle.bundle_name == created_bundle.bundle_name
        assert len(retrieved_bundle.bundle_items) == 1

    def test_get_bundle_by_id_not_exists(self, bundle_dao, clean_database):
        retrieved_bundle = bundle_dao.get_bundle_by_id(9999)

        assert retrieved_bundle is None

    def test_get_bundle_by_orderable_id(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {multiple_items[0]: 1}
        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=15,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        retrieved_bundle = bundle_dao.get_bundle_by_orderable_id(created_bundle.orderable_id)

        assert retrieved_bundle is not None
        assert retrieved_bundle.bundle_id == created_bundle.bundle_id
        assert retrieved_bundle.orderable_id == created_bundle.orderable_id

    def test_get_bundle_by_orderable_id_not_exist(self, bundle_dao, clean_database):
        """test getting None when orderable id does not exist"""
        retrieved_bundle = bundle_dao.get_bundle_by_orderable_id(42316253)
        assert retrieved_bundle is None

    def test_get_all_bundles_empty(self, bundle_dao, clean_database):
        bundles = bundle_dao.get_all_bundle()

        assert bundles == []

    def test_get_all_bundles_multiple(self, bundle_dao, multiple_items, clean_database):
        bundle_items1 = {multiple_items[0]: 1, multiple_items[1]: 1}
        bundle_dao.create_bundle(
            bundle_name="Menu 1",
            bundle_reduction=10,
            bundle_description="Premier bundle",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items1,
        )

        bundle_items2 = {multiple_items[2]: 1}
        bundle_dao.create_bundle(
            bundle_name="Menu 2",
            bundle_reduction=20,
            bundle_description="Deuxième bundle",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items2,
        )

        bundles = bundle_dao.get_all_bundle()

        assert bundles is not None
        assert len(bundles) == 2

    def test_update_bundle(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {multiple_items[0]: 1}
        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu Original",
            bundle_reduction=10,
            bundle_description="Description originale",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 6, 30),
            bundle_items=bundle_items,
        )

        new_bundle_items = {multiple_items[1]: 2, multiple_items[2]: 1}
        updated_bundle = bundle_dao.update_bundle(
            bundle_id=created_bundle.bundle_id,
            update={
                "bundle_name": "Menu Modifié",
                "bundle_reduction": 25,
                "bundle_description": "Nouvelle description",
                "bundle_availability_start_date": datetime(2025, 2, 1),
                "bundle_availability_end_date": datetime(2025, 12, 31),
                "bundle_items": new_bundle_items,
            },
        )

        assert updated_bundle.bundle_name == "Menu Modifié"
        assert updated_bundle.bundle_reduction == 25
        assert updated_bundle.bundle_description == "Nouvelle description"
        assert len(updated_bundle.bundle_items) == 2

    def test_update_item_invalid_field_raises_error(
        self, bundle_dao, multiple_items, clean_database
    ):
        """Test updating with wrong field"""
        bundle_items = {multiple_items[0]: 1}
        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu Original",
            bundle_reduction=10,
            bundle_description="Description originale",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 6, 30),
            bundle_items=bundle_items,
        )

        with pytest.raises(ValueError, match="not a parameter of Bundle"):
            bundle_dao.update_bundle(created_bundle.bundle_id, {"invalid_field": "value"})

    def test_update_bundle_id_not_exist(self, bundle_dao):
        retrieved_bundle = bundle_dao.update_bundle(42316253, {})
        assert retrieved_bundle is None

    def test_delete_bundle(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {multiple_items[0]: 1}
        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu à supprimer",
            bundle_reduction=10,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        bundle_id = created_bundle.bundle_id

        bundle_dao.delete_bundle(bundle_id)

        retrieved_bundle = bundle_dao.get_bundle_by_id(bundle_id)
        assert retrieved_bundle is None

    def test_get_items_from_bundle(self, bundle_dao, multiple_items, clean_database):
        bundle_items = {multiple_items[0]: 2, multiple_items[1]: 1}

        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=15,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        items_dict = bundle_dao._get_items_from_bundle(created_bundle.bundle_id)

        assert len(items_dict) == 2
        assert any(item.item_id == multiple_items[0].item_id for item in items_dict.keys())

    def test_get_items_from_bundle_no_items(self, bundle_dao, clean_database):
        created_bundle = bundle_dao.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=15,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items={},
        )

        items_dict = bundle_dao._get_items_from_bundle(created_bundle.bundle_id)

        assert items_dict == {}
