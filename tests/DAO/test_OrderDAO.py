from datetime import datetime, timedelta

from src.Model.Order import OrderState


class TestOrderDAO:
    def test_create_order(self, order_dao, sample_customer, clean_database):
        """Test creation of an order"""
        order = order_dao.create_order(sample_customer.id)

        assert order is not None
        assert order.order_id > 0
        assert order.order_customer_id == sample_customer.id
        assert order.order_state == OrderState.PENDING
        assert datetime.now() - timedelta(seconds=1) < order.order_created_at < datetime.now()
        assert order.order_orderables == {} or order.order_orderables is None

    def test_get_order_by_id_exists(self, order_dao, sample_customer, clean_database):
        """Test get an order by id"""
        created_order = order_dao.create_order(sample_customer.id)

        retrieved_order = order_dao.get_order_by_id(created_order.order_id)

        assert retrieved_order is not None
        assert retrieved_order.order_id == created_order.order_id
        assert retrieved_order.order_customer_id == sample_customer.id

    def test_get_order_by_id_not_exists(self, order_dao, clean_database):
        """Test get an order by id that doesn't exists"""
        retrieved_order = order_dao.get_order_by_id(9999)

        assert retrieved_order is None

    def test_get_all_orders_empty(self, order_dao, clean_database):
        """Tests that get_all_orders returns None"""
        orders = order_dao.get_all_orders(limit=10)

        assert orders == []

    def test_get_all_orders_multiple(self, order_dao, sample_customer, clean_database):
        """Tests that get_all_orders returns all the orders"""
        order_dao.create_order(sample_customer.id)
        order_dao.create_order(sample_customer.id)
        order_dao.create_order(sample_customer.id)

        orders = order_dao.get_all_orders(limit=10)

        assert orders is not None
        assert len(orders) == 3
        assert all(order.order_customer_id == sample_customer.id for order in orders)

    def test_get_all_orders_by_customer_exists(self, order_dao, sample_customer, clean_database):
        """Test fetching all orders of an existing customer"""
        order_dao.create_order(sample_customer.id)
        order_dao.create_order(sample_customer.id)

        orders = order_dao.get_all_orders_by_customer(sample_customer.id)

        assert orders is not None
        assert len(orders) == 2
        assert all(o.order_customer_id == sample_customer.id for o in orders)

    def test_get_all_orders_by_customer_not_exists(self, order_dao, clean_database):
        """Test fetching all orders of a non-existing customer"""
        orders = order_dao.get_all_orders_by_customer(9999)

        assert orders == []

    def test_get_all_orders_prepared(self, order_dao, sample_customer, clean_database):
        """Test fetching all prepared orders"""

        order1 = order_dao.create_order(sample_customer.id)
        order_dao.create_order(sample_customer.id)
        order3 = order_dao.create_order(sample_customer.id)

        order_dao.update_order_state(order1.order_id, OrderState.PREPARED.value)
        order_dao.update_order_state(order3.order_id, OrderState.PREPARED.value)

        prepared_orders = order_dao.get_orders_by_state(OrderState.PREPARED.value)

        assert prepared_orders is not None
        assert len(prepared_orders) == 2
        assert all(o.is_prepared is True for o in prepared_orders)

    def test_no_orders_prepared(self, order_dao, sample_customer, clean_database):
        """Test fetching orders prepared when there is no orders prepared"""

        order_dao.create_order(sample_customer.id)
        order_dao.create_order(sample_customer.id)
        order_dao.create_order(sample_customer.id)

        prepared_orders = order_dao.get_orders_by_state(OrderState.PREPARED.value)

        assert prepared_orders == []

    def test_update_order_payment_status(self, order_dao, sample_customer, clean_database):
        """Test updating payment status"""
        created_order = order_dao.create_order(sample_customer.id)

        updated_order = order_dao.update_order_state(created_order.order_id, OrderState.PAID.value)

        assert updated_order.is_paid is True
        assert updated_order.is_prepared is False

    def test_update_order_preparation_status(self, order_dao, sample_customer, clean_database):
        """Test updating preparation status"""
        created_order = order_dao.create_order(sample_customer.id)
        order_dao.update_order_state(created_order.order_id, OrderState.PAID.value)
        updated_order = order_dao.update_order_state(
            created_order.order_id, OrderState.PREPARED.value
        )

        assert updated_order.is_prepared is True
        assert updated_order.is_paid is True

    def test_delete_order(self, order_dao, sample_customer, clean_database):
        """Test deleting order"""
        created_order = order_dao.create_order(sample_customer.id)
        order_id = created_order.order_id

        order_dao.delete_order(order_id)

        retrieved_order = order_dao.get_order_by_id(order_id)
        assert retrieved_order is None

    def test_delete_order_cascade_order_contents(
        self, order_dao, sample_customer, item_dao, bundle_dao, orderable_dao, clean_database
    ):
        """Test that deleting order deletes it from Order_contents table"""
        order = order_dao.create_order(sample_customer.id)

        item = item_dao.create_item(
            item_name="Test Item",
            item_price=5.0,
            item_type="Drink",
            item_description="Item de test",
            item_stock=10,
        )
        order_dao.add_orderable_to_order(order.order_id, item.orderable_id)

        bundle = bundle_dao.create_bundle(
            bundle_name="Test Bundle",
            bundle_reduction=5,
            bundle_description="Drink",
            bundle_availability_start_date=datetime(2025, 10, 9),
            bundle_availability_end_date=datetime(2026, 10, 9),
            bundle_items={item: 2},
        )
        order_dao.add_orderable_to_order(order.order_id, bundle.orderable_id)

        order_dao.delete_order(order.order_id)

        retrieved_order = order_dao.get_order_by_id(order.order_id)
        assert retrieved_order is None

    def test_add_orderable_to_order_new(
        self, order_dao, item_dao, sample_customer, clean_database, orderable_dao
    ):
        """Test adding an item for the first time"""

        order = order_dao.create_order(sample_customer.id)

        item = item_dao.create_item(
            item_name="Test Item",
            item_price=5.0,
            item_type="Drink",
            item_description="Item de test",
            item_stock=10,
        )
        updated_order = order_dao.add_orderable_to_order(order.order_id, item.orderable_id)

        assert updated_order is not None
        assert len(updated_order.order_orderables) == 1

    def test_add_orderable_to_order_increment(
        self, order_dao, item_dao, sample_customer, clean_database, orderable_dao
    ):
        """Test adding an item multiple times"""

        order = order_dao.create_order(sample_customer.id)

        item = item_dao.create_item(
            item_name="Test Item",
            item_price=5.0,
            item_type="Drink",
            item_description="Item de test",
            item_stock=10,
        )
        order = order_dao.add_orderable_to_order(order.order_id, item.orderable_id)
        order = order_dao.add_orderable_to_order(order.order_id, item.orderable_id)

        quantity = order_dao.get_quantity_of_orderables(order.order_id, item.orderable_id)
        assert quantity == 2
        assert list(order.order_orderables.keys())[0] == item

    def test_remove_orderable_from_order_decrement(
        self, order_dao, item_dao, sample_customer, clean_database, orderable_dao
    ):
        """Test removing item"""

        order = order_dao.create_order(sample_customer.id)

        item = item_dao.create_item(
            item_name="Test Item",
            item_price=5.0,
            item_type="Drink",
            item_description="Item de test",
            item_stock=10,
        )

        order_dao.add_orderable_to_order(item.orderable_id, order.order_id)
        order_dao.add_orderable_to_order(item.orderable_id, order.order_id)

        updated_order = order_dao.remove_orderable_from_order(order.order_id, item.orderable_id)

        assert updated_order is not None

    def test_remove_orderable_from_order_delete(
        self, order_dao, item_dao, sample_customer, clean_database, orderable_dao
    ):
        """Test removing all occurences of an item"""
        order = order_dao.create_order(sample_customer.id)

        item = item_dao.create_item(
            item_name="Test Item",
            item_price=5.0,
            item_type="Drink",
            item_description="Item de test",
            item_stock=10,
        )
        order_dao.add_orderable_to_order(item.orderable_id, order.order_id)

        order_dao.remove_orderable_from_order(order.order_id, item.orderable_id)

        quantity = order_dao.get_quantity_of_orderables(order.order_id, item.orderable_id)
        assert quantity == 0
