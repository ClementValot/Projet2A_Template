import pytest


class TestDeliveryDAO:
    def test_create_delivery(self, delivery_dao, sample_order, sample_driver, clean_database):
        """Test create delivery"""
        delivery = delivery_dao.create_delivery(
            order_id=sample_order.order_id, driver_id=sample_driver.id
        )

        assert delivery is not None
        assert delivery.delivery_order_id == sample_order.order_id
        assert delivery.delivery_driver_id == sample_driver.id
        assert delivery.delivery_state == 0

    def test_get_deliveries_by_driver_exists(
        self, delivery_dao, sample_order, sample_driver, clean_database
    ):
        """Test getting delivery by driver id"""
        delivery_dao.create_delivery(order_id=sample_order.order_id, driver_id=sample_driver.id)
        delivery_dao.update_delivery_state(sample_order.order_id, 1)
        retrieved_delivery = delivery_dao.get_driver_current_delivery(sample_driver.id)

        assert retrieved_delivery is not None
        assert retrieved_delivery.delivery_driver_id == sample_driver.id
        assert retrieved_delivery.delivery_order_id == sample_order.order_id

    def test_get_deliveries_by_driver_not_exists(self, delivery_dao, clean_database):
        """Test getting delivery by non-existant driver id"""
        retrieved_delivery = delivery_dao.get_deliveries_by_driver(9999)

        assert retrieved_delivery == []

    def test_get_driver_current_delivery_exist(
        self, delivery_dao, sample_order, sample_driver, clean_database
    ):
        """Should return a Delivery when at least one exists"""
        delivery_dao.create_delivery(order_id=sample_order.order_id, driver_id=sample_driver.id)
        delivery_dao.update_delivery_state(sample_order.order_id, 1)

        retrieved = delivery_dao.get_driver_current_delivery(sample_driver.id)

        assert retrieved is not None
        assert retrieved.delivery_driver_id == sample_driver.id

    def test_get_driver_current_delivery_not_exist(self, delivery_dao, clean_database):
        """Test getting delivery by non-existant driver id"""
        retrieved_delivery = delivery_dao.get_driver_current_delivery(9999)

        assert retrieved_delivery is None

    def test_get_delivery_by_user(
        self, delivery_dao, sample_order, sample_driver, sample_customer, clean_database
    ):
        """Test get delivery by user"""
        delivery_dao.create_delivery(order_id=sample_order.order_id, driver_id=sample_driver.id)

        retrieved_delivery = delivery_dao.get_delivery_by_user(sample_customer.id)

        assert retrieved_delivery is not None

    def test_get_delivery_by_order_id_exist(
        self, delivery_dao, sample_order, sample_driver, clean_database
    ):
        """Test getting delivery by order id"""
        delivery_dao.create_delivery(order_id=sample_order.order_id, driver_id=sample_driver.id)
        retrieved_delivery = delivery_dao.get_delivery_by_order_id(sample_order.order_id)
        assert retrieved_delivery is not None
        assert retrieved_delivery.delivery_driver_id == sample_driver.id
        assert retrieved_delivery.delivery_order_id == sample_order.order_id

    def test_get_delivery_by_order_id_not_exist(self, delivery_dao, clean_database):
        retrieved_delivery = delivery_dao.get_delivery_by_order_id(9999)

        assert retrieved_delivery is None

    def test_update_delivery_state(self, delivery_dao, sample_order, sample_driver, clean_database):
        """Test updating delivery state"""
        delivery = delivery_dao.create_delivery(
            order_id=sample_order.order_id, driver_id=sample_driver.id
        )

        updated_delivery = delivery_dao.update_delivery_state(
            delivery_id=delivery.delivery_order_id, state=1
        )

        assert updated_delivery.delivery_state == 1

    def test_update_delivery_state_invalid_raises_error(
        self, delivery_dao, sample_order, sample_driver, clean_database
    ):
        """Test invalid delivery state"""
        delivery = delivery_dao.create_delivery(
            order_id=sample_order.order_id, driver_id=sample_driver.id
        )

        with pytest.raises(ValueError, match="State can only take"):
            delivery_dao.update_delivery_state(delivery_id=delivery.delivery_order_id, state=5)

    def test_change_driver(
        self, delivery_dao, driver_dao, sample_order, sample_driver, clean_database
    ):
        """Test switch driver"""
        delivery = delivery_dao.create_delivery(
            order_id=sample_order.order_id, driver_id=sample_driver.id
        )

        new_driver = driver_dao.create_driver("New", "Driver", "0800", "hash", "salt")

        updated_delivery = delivery_dao.change_driver(
            delivery_id=delivery.delivery_order_id, driver_id=new_driver.id
        )

        assert updated_delivery.delivery_driver_id == new_driver.id
        assert updated_delivery.delivery_order_id == sample_order.order_id

    def test_delete_delivery(self, delivery_dao, sample_order, sample_driver, clean_database):
        """Test de suppression d'une livraison"""
        # Créer une livraison
        delivery = delivery_dao.create_delivery(
            order_id=sample_order.order_id, driver_id=sample_driver.id
        )

        delivery_id = delivery.delivery_order_id

        delivery_dao.delete_delivery(delivery_id)

        retrieved_delivery = delivery_dao.get_delivery_by_order_id(sample_order.order_id)

        if retrieved_delivery is not None:
            assert retrieved_delivery.delivery_order_id != delivery_id
