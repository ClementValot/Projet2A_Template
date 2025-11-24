import re
from datetime import datetime

import pytest


class TestBundleService:
    def test_get_bundle_by_id_exists(self, bundle_service, sample_bundle, clean_database):
        """Test getting a bundle by id"""
        retrieved_bundle = bundle_service.get_bundle_by_id(sample_bundle.bundle_id)

        assert retrieved_bundle is not None
        assert retrieved_bundle.bundle_id == sample_bundle.bundle_id
        assert retrieved_bundle.bundle_name == sample_bundle.bundle_name

    def test_get_bundle_by_id_not_exists(self, bundle_service, clean_database):
        """Test getting bundle by non-existing id raises error"""
        with pytest.raises(ValueError, match="Cannot get: bundle with ID 9999 not found"):
            bundle_service.get_bundle_by_id(9999)

    def test_get_bundle_by_orderable_id_exists(self, bundle_service, sample_bundle, clean_database):
        """Test getting a bundle by orderable id"""
        retrieved_bundle = bundle_service.get_bundle_by_orderable_id(sample_bundle.orderable_id)

        assert retrieved_bundle is not None
        assert retrieved_bundle.orderable_id == sample_bundle.orderable_id

    def test_get_bundle_by_orderable_id_not_exists(self, bundle_service, clean_database):
        """Test getting bundle by non-existing orderable id raises error"""
        with pytest.raises(ValueError, match="Cannot get: bundle with ID 9999 not found"):
            bundle_service.get_bundle_by_orderable_id(9999)

    def test_get_all_bundles_empty(self, bundle_service, clean_database):
        """Test getting all bundles when there are none"""
        bundles = bundle_service.get_all_bundles()

        assert bundles == []

    def test_get_all_bundles_multiple(self, bundle_service, multiple_items, clean_database):
        """Test getting all bundles"""
        bundle_items1 = {multiple_items[0]: 1, multiple_items[1]: 1}
        bundle_service.create_bundle(
            bundle_name="Menu 1",
            bundle_reduction=10,
            bundle_description="Premier bundle",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items1,
        )

        bundle_items2 = {multiple_items[2]: 1}
        bundle_service.create_bundle(
            bundle_name="Menu 2",
            bundle_reduction=20,
            bundle_description="Deuxième bundle",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items2,
        )

        bundles = bundle_service.get_all_bundles()

        assert bundles != []
        assert len(bundles) == 2

    def test_create_bundle(self, bundle_service, multiple_items, clean_database):
        """Test creating a bundle"""
        bundle_items = {multiple_items[0]: 1, multiple_items[1]: 1}

        created_bundle = bundle_service.create_bundle(
            bundle_name="Menu Test",
            bundle_reduction=15,
            bundle_description="Bundle de test",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        assert created_bundle is not None
        assert created_bundle.bundle_id > 0
        assert created_bundle.bundle_name == "Menu Test"
        assert created_bundle.bundle_reduction == 15
        assert len(created_bundle.bundle_items) == 2

    def test_update_bundle(self, bundle_service, sample_bundle, multiple_items, clean_database):
        """Test updating a bundle"""
        new_bundle_items = {multiple_items[2]: 1}
        updated_bundle = bundle_service.update_bundle(
            bundle_id=sample_bundle.bundle_id,
            update={
                "bundle_name": "Menu Modifié",
                "bundle_reduction": 25,
                "bundle_items": new_bundle_items,
            },
        )

        assert updated_bundle.bundle_name == "Menu Modifié"
        assert updated_bundle.bundle_reduction == 25
        assert list(updated_bundle.bundle_items.keys())[0] == multiple_items[2]

    def test_create_bundle_invalid_reduction_too_low(
        self, bundle_service, multiple_items, clean_database
    ):
        """Test creating a bundle with reduction < 0"""
        bundle_items = {multiple_items[0]: 1}

        with pytest.raises(ValueError, match="Bundle reduction must be between 0 and 100"):
            bundle_service.create_bundle(
                bundle_name="Menu Test",
                bundle_reduction=-5,
                bundle_description="Bundle de test",
                bundle_availability_start_date=datetime(2025, 1, 1),
                bundle_availability_end_date=datetime(2025, 12, 31),
                bundle_items=bundle_items,
            )

    def test_create_bundle_invalid_reduction_too_high(
        self, bundle_service, multiple_items, clean_database
    ):
        """Test creating a bundle with reduction > 100"""
        bundle_items = {multiple_items[0]: 1}

        with pytest.raises(ValueError, match="Bundle reduction must be between 0 and 100"):
            bundle_service.create_bundle(
                bundle_name="Menu Test",
                bundle_reduction=150,
                bundle_description="Bundle de test",
                bundle_availability_start_date=datetime(2025, 1, 1),
                bundle_availability_end_date=datetime(2025, 12, 31),
                bundle_items=bundle_items,
            )

    def test_create_bundle_invalid_dates_start_after_end(
        self, bundle_service, multiple_items, clean_database
    ):
        """Test creating a bundle with start date after end date"""
        bundle_items = {multiple_items[0]: 1}

        with pytest.raises(ValueError, match="Bundle end date must later than the start date"):
            bundle_service.create_bundle(
                bundle_name="Menu Test",
                bundle_reduction=15,
                bundle_description="Bundle de test",
                bundle_availability_start_date=datetime(2025, 12, 31),
                bundle_availability_end_date=datetime(2025, 1, 1),
                bundle_items=bundle_items,
            )

    def test_create_bundle_end_date_in_past(self, bundle_service, multiple_items, clean_database):
        """Test creating a bundle with end date in the past"""
        bundle_items = {multiple_items[0]: 1}

        with pytest.raises(ValueError, match="Start date cannot be in the past"):
            bundle_service.create_bundle(
                bundle_name="Menu Test",
                bundle_reduction=15,
                bundle_description="Bundle de test",
                bundle_availability_start_date=datetime(2020, 1, 1),
                bundle_availability_end_date=datetime(2020, 12, 31),
                bundle_items=bundle_items,
            )

    def test_update_bundle_not_exists(self, bundle_service, clean_database):
        """Test updating non-existing bundle raises error"""
        with pytest.raises(
            ValueError,
            match=re.escape("[BundleService] Cannot get: bundle with ID 9999 not found."),
        ):
            bundle_service.update_bundle(9999, {"bundle_name": "Test"})

    def test_delete_bundle(self, bundle_service, sample_bundle, clean_database):
        """Test deleting a bundle"""
        bundle_service.delete_bundle(sample_bundle.bundle_id)

        with pytest.raises(ValueError, match="Cannot get: bundle with ID"):
            bundle_service.get_bundle_by_id(sample_bundle.bundle_id)

    def test_delete_bundle_not_exists(self, bundle_service, clean_database):
        """Test deleting non-existing bundle raises error"""
        with pytest.raises(
            ValueError,
            match=re.escape("[BundleService] Cannot get: bundle with ID 9999 not found."),
        ):
            bundle_service.delete_bundle(9999)

    def test_update_bundle_no_changes(self, bundle_service, sample_bundle, clean_database):
        """Test updating bundle with no changes raises error"""
        with pytest.raises(
            ValueError, match="Cannot update bundle: You must change at least one field"
        ):
            bundle_service.update_bundle(
                bundle_id=sample_bundle.bundle_id,
                update={"bundle_name": None, "bundle_reduction": None},
            )

    def test_update_bundle_invalid_start_date_format(
        self, bundle_service, sample_bundle, clean_database
    ):
        """Test updating bundle with invalid start date format"""
        with pytest.raises(
            ValueError, match="Invalid start date format. Expected format: DD/MM/YYYY"
        ):
            bundle_service.update_bundle(
                bundle_id=sample_bundle.bundle_id,
                update={"bundle_availability_start_date": "invalid-date"},
            )

    def test_update_bundle_invalid_end_date_format(
        self, bundle_service, sample_bundle, clean_database
    ):
        """Test updating bundle with invalid end date format"""
        with pytest.raises(
            ValueError, match="Invalid end date format. Expected format: DD/MM/YYYY"
        ):
            bundle_service.update_bundle(
                bundle_id=sample_bundle.bundle_id,
                update={"bundle_availability_end_date": "invalid-date"},
            )

    def test_update_bundle_end_date_before_start_date(
        self, bundle_service, sample_bundle, clean_database
    ):
        """Test updating bundle with end date before start date"""
        with pytest.raises(ValueError, match="End date.*must be after start date"):
            bundle_service.update_bundle(
                bundle_id=sample_bundle.bundle_id,
                update={
                    "bundle_availability_start_date": "01/01/2025",
                    "bundle_availability_end_date": "01/01/2024",
                },
            )

    def test_update_bundle_end_date_in_past(self, bundle_service, sample_bundle, clean_database):
        """Test updating bundle with end date in the past"""
        with pytest.raises(ValueError, match="Start date cannot be in the past"):
            bundle_service.update_bundle(
                bundle_id=sample_bundle.bundle_id,
                update={
                    "bundle_availability_start_date": "01/01/2020",
                    "bundle_availability_end_date": "01/01/2021",
                },
            )

    def test_update_bundle_invalid_reduction(self, bundle_service, sample_bundle, clean_database):
        """Test updating bundle with invalid reduction"""
        with pytest.raises(ValueError, match="Bundle reduction must be between 0 and 100"):
            bundle_service.update_bundle(
                bundle_id=sample_bundle.bundle_id, update={"bundle_reduction": 150}
            )
