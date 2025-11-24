import re

import pytest


class TestDriverService:
    def test_get_driver_by_id_exists(self, driver_service, sample_driver, clean_database):
        """Test getting a driver by id"""
        retrieved_driver = driver_service.get_driver_by_id(sample_driver.id)

        assert retrieved_driver is not None
        assert retrieved_driver.id == sample_driver.id
        assert retrieved_driver.first_name == sample_driver.first_name

    def test_get_driver_by_phone(self, driver_service, sample_driver, clean_database):
        """Test getting a driver by phone"""
        retrieved_driver = driver_service.get_driver_by_phone(sample_driver.driver_phone)

        assert retrieved_driver is not None
        assert retrieved_driver.id == sample_driver.id
        assert retrieved_driver.first_name == sample_driver.first_name

    def test_get_driver_by_phone_not_exists(self, driver_service, sample_driver, clean_database):
        """Test getting a driver by non-existing phone"""
        with pytest.raises(
            ValueError,
            match=re.escape("Driver with phone mental breakdown not found."),
        ):
            driver_service.get_driver_by_phone("mental breakdown")

    def test_get_driver_by_id_not_exists(self, driver_service, clean_database):
        """Test getting driver by non-existing id raises error"""
        with pytest.raises(ValueError, match="Driver with ID 9999 not found"):
            driver_service.get_driver_by_id(9999)

    def test_get_all_drivers_empty(self, driver_service, clean_database):
        """Test getting all drivers when there are none"""
        drivers = driver_service.get_all_drivers()

        assert drivers == []

    def test_get_all_drivers_multiple(self, driver_service, driver_dao, clean_database):
        """Test getting all drivers"""
        driver_dao.create_driver("A", "A", "0701", "hash", "salt")
        driver_dao.create_driver("B", "B", "0702", "hash", "salt")
        driver_dao.create_driver("C", "C", "0703", "hash", "salt")

        drivers = driver_service.get_all_drivers()

        assert drivers is not None
        assert len(drivers) == 3

    def test_create_driver(self, driver_service, clean_database):
        """Test creating a driver"""
        created_driver = driver_service.create_driver(
            first_name="Test",
            last_name="Driver",
            phone="0612345678",
            password="V4lidP@ssword",
        )

        assert created_driver is not None
        assert created_driver.id == 1
        assert created_driver.first_name == "Test"
        assert created_driver.last_name == "DRIVER"
        assert created_driver.driver_is_delivering is False

    def test_update_driver(self, driver_service, sample_driver, clean_database):
        """Test updating a driver"""
        updated_driver = driver_service.update_driver(
            sample_driver.id, {"driver_first_name": "UpdatedName", "driver_is_delivering": True}
        )

        assert updated_driver.first_name == "Updatedname"
        assert updated_driver.driver_is_delivering is True

    def test_update_driver_not_exists(self, driver_service, clean_database):
        """Test updating non-existing driver raises error"""
        with pytest.raises(ValueError, match="Driver with ID 9999 not found"):
            driver_service.update_driver(9999, {"driver_first_name": "Test"})

    def test_delivery_start(
        self,
        driver_service,
        sample_order,
        sample_driver,
        clean_database,
        delivery_dao,
        order_service,
    ):
        """Test starting a delivery"""
        order_service.mark_as_paid(sample_order.order_id)
        order_service.mark_as_prepared(sample_order.order_id)

        updated_delivery = driver_service.start_delivery(sample_order.order_id, sample_driver.id)

        assert updated_delivery.delivery_state == 1

        updated_driver = driver_service.get_driver_by_id(sample_driver.id)
        assert updated_driver.driver_is_delivering is True

    def test_delivery_start_driver_not_exists(self, driver_service, sample_order, clean_database):
        """Test starting delivery with non-existing driver raises error"""
        with pytest.raises(ValueError, match="Driver with ID 9999 not found"):
            driver_service.start_delivery(sample_order.order_id, 9999)

    def test_delivery_end(
        self,
        driver_service,
        sample_order,
        sample_driver,
        clean_database,
        delivery_dao,
        order_service,
    ):
        """Test ending a delivery"""
        order_service.mark_as_paid(sample_order.order_id)
        order_service.mark_as_prepared(sample_order.order_id)
        driver_service.start_delivery(sample_order.order_id, sample_driver.id)

        updated_delivery = driver_service.end_delivery(sample_order.order_id, sample_driver.id)

        assert updated_delivery.delivery_state == 2

        updated_driver = driver_service.get_driver_by_id(sample_driver.id)
        assert updated_driver.driver_is_delivering is False

    def test_delivery_end_driver_not_exists(self, driver_service, sample_order, clean_database):
        """Test ending delivery with non-existing driver raises error"""
        with pytest.raises(ValueError, match="Driver with ID 9999 not found"):
            driver_service.end_delivery(sample_order.order_id, 9999)

    def test_delete_driver(self, driver_service, sample_driver, clean_database):
        """Test deleting a driver"""
        driver_service.delete_driver(sample_driver.id)

        with pytest.raises(ValueError, match="Driver with ID 1 not found"):
            driver_service.get_driver_by_id(sample_driver.id)

    def test_delete_driver_not_exists(self, driver_service, clean_database):
        """Test deleting non-existing driver raises error"""
        with pytest.raises(ValueError, match="Driver with ID 9999 not found"):
            driver_service.delete_driver(9999)
