from datetime import datetime

import pytest


class TestDriverDAO:
    def test_create_driver(self, driver_dao, clean_database):
        """Test create a driver"""
        driver = driver_dao.create_driver(
            first_name="Lewis",
            last_name="Hamilton",
            phone="0707070707",
            password_hash="hashed_driver_pass",
            salt="driver_salt",
        )

        assert driver is not None
        assert driver.id > 0
        assert driver.first_name == "Lewis"
        assert driver.last_name == "Hamilton"
        assert driver.driver_phone == "0707070707"
        assert driver.password == "hashed_driver_pass"
        assert driver.salt.strip() == "driver_salt"
        assert driver.driver_is_delivering is False
        assert isinstance(driver.created_at, datetime)

    def test_get_driver_by_id_exists(self, driver_dao, sample_driver, clean_database):
        """Test getting driver by id"""

        retrieved_driver = driver_dao.get_driver_by_id(sample_driver.id)

        assert retrieved_driver is not None
        assert retrieved_driver.id == sample_driver.id
        assert retrieved_driver.first_name == "Lewis"
        assert retrieved_driver.driver_phone == "0707"

    def test_get_driver_by_id_not_exists(self, driver_dao, clean_database):
        """Test getting driver by non-existing id"""
        retrieved_driver = driver_dao.get_driver_by_id(9999)

        assert retrieved_driver is None

    def test_get_all_drivers_empty(self, driver_dao, clean_database):
        """Test get_all_drivers when there are no drivers"""
        drivers = driver_dao.get_all_drivers()

        assert drivers is None or drivers == []

    def test_get_all_drivers_multiple(self, driver_dao, clean_database):
        """Test get all drivers"""
        driver_dao.create_driver("A", "A", "0701", "hash", "salt")
        driver_dao.create_driver("B", "B", "0702", "hash", "salt")
        driver_dao.create_driver("C", "C", "0703", "hash", "salt")

        drivers = driver_dao.get_all_drivers()

        assert drivers is not None
        assert len(drivers) == 3

    def test_update_driver_multiple_fields(self, driver_dao, sample_driver, clean_database):
        """Test updating multiple fields"""
        updated_driver = driver_dao.update_driver(
            sample_driver.id,
            {
                "driver_first_name": "Pierre",
                "driver_last_name": "Durand",
                "driver_phone": "0688888888",
            },
        )

        assert updated_driver.first_name == "Pierre"
        assert updated_driver.last_name == "Durand"
        assert updated_driver.driver_phone == "0688888888"

    def test_update_driver_invalid_field_raises_error(
        self, driver_dao, sample_driver, clean_database
    ):
        """Test invalid field raises error"""
        with pytest.raises(ValueError, match="not a parameter of Driver"):
            driver_dao.update_driver(sample_driver.id, {"invalid_field": "value"})

    def test_delete_driver(self, driver_dao, sample_driver, clean_database):
        """Test delete driver"""
        driver_dao.delete_driver(sample_driver.id)

        retrieved_driver = driver_dao.get_driver_by_id(sample_driver.id)
        assert retrieved_driver is None
