import re
from datetime import datetime

import pytest

from src.Model.Order import OrderState


class TestOrderService:
    def test_get_order_exists(self, order_service, sample_order, clean_database):
        """Test getting an order by id"""
        retrieved_order = order_service.get_order_by_id(sample_order.order_id)

        assert retrieved_order is not None
        assert retrieved_order.order_id == sample_order.order_id
        assert retrieved_order.order_customer_id == sample_order.order_customer_id

    def test_get_order_not_exists(self, order_service, clean_database):
        """Test getting order by non-existing id raises error"""
        with pytest.raises(ValueError, match="Cannot find: order with ID 9999 not found"):
            order_service.get_order_by_id(9999)

    def test_get_all_orders_empty(self, order_service, clean_database):
        """Test getting all orders when there are none"""
        orders = order_service.get_all_orders(limit=10)

        assert orders == []

    def test_get_all_orders(self, order_service, sample_customer, clean_database):
        """Test getting all orders"""
        order_service.create_order(sample_customer.id)

        orders = order_service.get_all_orders(limit=5)

        assert orders != []
        assert len(orders) == 1

    def test_get_all_orders_by_customer(self, order_service, sample_customer, clean_database):
        """Test getting all orders by customer"""
        order_service.create_order(sample_customer.id)
        order_service.mark_as_paid(1)
        order_service.mark_as_prepared(1)
        order_service.update_order_state(1, OrderState.DELIVERING)
        order_service.update_order_state(1, OrderState.DELIVERED)
        order_service.create_order(sample_customer.id)

        orders = order_service.get_all_orders_by_customer(sample_customer.id)

        assert orders != []
        assert len(orders) == 2
        assert all(o.order_customer_id == sample_customer.id for o in orders)

    def test_get_all_orders_prepared(self, order_service, sample_customer, clean_database):
        """Test getting all prepared orders"""
        order_service.create_order(sample_customer.id)
        order_service.mark_as_paid(1)
        order_service.mark_as_prepared(1)

        prepared_orders = order_service.get_available_orders_for_drivers()

        assert prepared_orders != []
        assert len(prepared_orders) == 1
        assert all(o.is_prepared is True for o in prepared_orders)

    def test_create_order(self, order_service, sample_customer, clean_database):
        """Test creating an order"""
        created_order = order_service.create_order(sample_customer.id)

        assert created_order is not None
        assert created_order.order_id > 0
        assert created_order.order_customer_id == sample_customer.id
        assert created_order.order_state == OrderState.PENDING
        assert created_order.is_paid is False
        assert created_order.is_prepared is False

    def test_delete_order(self, order_service, sample_order, clean_database):
        """Test deleting an order"""
        order_service.delete_order(sample_order.order_id)

        with pytest.raises(ValueError, match="Cannot find: order with ID"):
            order_service.get_order_by_id(sample_order.order_id)

    def test_delete_order_not_exists(self, order_service, clean_database):
        """Test deleting non-existing order raises error"""
        with pytest.raises(ValueError, match="Cannot find: order with ID 9999 not found"):
            order_service.delete_order(9999)

    def test_add_item_to_order_success(
        self, order_service, sample_order, sample_item, clean_database, orderable_dao, item_service
    ):
        """Test adding an item to an order successfully"""
        initial_stock = sample_item.item_stock
        orderable_id = sample_item.orderable_id

        updated_order = order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 2)

        assert updated_order is not None
        assert len(updated_order.order_orderables) == 1

        updated_item = item_service.get_item_by_id(sample_item.item_id)
        assert updated_item.item_stock == initial_stock - 2

    def test_add_item_to_order_insufficient_stock(
        self, order_service, sample_order, sample_item, clean_database, orderable_dao
    ):
        """Test adding an item with insufficient stock raises error"""
        orderable_id = sample_item.orderable_id

        with pytest.raises(
            ValueError,
            match=re.escape(
                "[OrderService] Not enough stock for Galette-Saucisse (available: 50)."
            ),
        ):
            order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 100)

    def test_add_orderable_to_order_item_not_found(
        self, order_service, sample_order, clean_database, orderable_dao, sample_item
    ):
        """Test adding non-existing item raises error"""
        with pytest.raises(
            ValueError, match=re.escape("[OrderService] Orderable with ID 9999 not found.")
        ):
            order_service.add_orderable_to_order(9999, sample_order.order_id, 1)

    def test_add_item_to_order_multiple_times(
        self, order_service, sample_order, sample_item, clean_database, orderable_dao, item_service
    ):
        """Test adding the same item multiple times increments quantity"""
        initial_stock = sample_item.item_stock
        orderable_id = sample_item.orderable_id

        updated_order = order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 1)

        updated_order = order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 2)

        assert updated_order is not None

        updated_item = item_service.get_item_by_id(sample_item.item_id)
        assert updated_item.item_stock == initial_stock - 3

    def test_add_bundle_to_order_success(
        self,
        order_service,
        sample_order,
        sample_bundle,
        multiple_items,
        clean_database,
        orderable_dao,
        item_service,
    ):
        """Test adding a bundle to an order successfully"""
        orderable_id = sample_bundle.orderable_id

        initial_stocks = {item.item_id: item.item_stock for item in multiple_items[:2]}

        updated_order = order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 1)

        assert updated_order is not None
        assert len(updated_order.order_orderables) == 1

        for item, quantity_in_bundle in sample_bundle.bundle_items.items():
            updated_item = item_service.get_item_by_id(item.item_id)
            expected_stock = initial_stocks[item.item_id] - quantity_in_bundle
            assert updated_item.item_stock == expected_stock

    def test_add_bundle_to_order_insufficient_stock_one_item(
        self, order_service, sample_order, bundle_dao, multiple_items, clean_database, orderable_dao
    ):
        """Test adding a bundle when one item has insufficient stock"""

        bundle_items = {multiple_items[0]: 100}
        bundle = bundle_dao.create_bundle(
            bundle_name="Bundle Test",
            bundle_reduction=10,
            bundle_description="Test bundle",
            bundle_availability_start_date=datetime(2025, 1, 1),
            bundle_availability_end_date=datetime(2025, 12, 31),
            bundle_items=bundle_items,
        )

        with pytest.raises(
            ValueError,
            match=re.escape("[OrderService] Not enough stock for Bundle Test (available: 0)."),
        ):
            order_service.add_orderable_to_order(bundle.orderable_id, sample_order.order_id, 1)

    def test_add_bundle_to_order_multiple_times(
        self,
        order_service,
        sample_order,
        sample_bundle,
        multiple_items,
        clean_database,
        orderable_dao,
        item_service,
    ):
        """Test adding the same bundle multiple times"""
        orderable_id = sample_bundle.orderable_id

        initial_stocks = {item.item_id: item.item_stock for item in multiple_items[:2]}

        order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 1)
        updated_order = order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 2)

        assert updated_order is not None

        for item, quantity_in_bundle in sample_bundle.bundle_items.items():
            updated_item = item_service.get_item_by_id(item.item_id)
            expected_stock = initial_stocks[item.item_id] - (quantity_in_bundle * 3)
            assert updated_item.item_stock == expected_stock

    def test_remove_item_from_order_success(
        self, order_service, sample_order, sample_item, clean_database, orderable_dao, item_service
    ):
        """Test removing an item from an order successfully"""
        orderable_id = sample_item.orderable_id

        initial_stock = sample_item.item_stock
        order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 3)

        updated_order = order_service.remove_orderable_from_order(
            orderable_id, sample_order.order_id, 2
        )

        assert updated_order is not None

        updated_item = item_service.get_item_by_id(sample_item.item_id)
        assert updated_item.item_stock == initial_stock - 1

    def test_remove_item_from_order_completely(
        self, order_service, sample_order, sample_item, clean_database, orderable_dao, item_service
    ):
        """Test removing all units of an item from order"""
        orderable_id = sample_item.orderable_id

        initial_stock = sample_item.item_stock
        order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 3)

        updated_order = order_service.remove_orderable_from_order(
            orderable_id, sample_order.order_id, 3
        )

        assert updated_order is not None
        assert len(updated_order.order_orderables) == 0

        updated_item = item_service.get_item_by_id(sample_item.item_id)
        assert updated_item.item_stock == initial_stock

    def test_remove_item_not_found(
        self, order_service, sample_order, clean_database, orderable_dao
    ):
        """Test removing non-existing item raises error"""
        with pytest.raises(
            ValueError, match=re.escape("[OrderService] Orderable with ID 9999 not found.")
        ):
            order_service.remove_orderable_from_order(9999, sample_order.order_id, 1)

    def test_remove_bundle_from_order_success(
        self,
        order_service,
        sample_order,
        sample_bundle,
        multiple_items,
        clean_database,
        orderable_dao,
        item_service,
    ):
        """Test removing a bundle from an order successfully"""
        orderable_id = sample_bundle.orderable_id

        initial_stocks = {item.item_id: item.item_stock for item in multiple_items[:2]}

        order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 2)

        updated_order = order_service.remove_orderable_from_order(
            orderable_id, sample_order.order_id, 1
        )

        assert updated_order is not None

        for item, quantity_in_bundle in sample_bundle.bundle_items.items():
            updated_item = item_service.get_item_by_id(item.item_id)
            expected_stock = initial_stocks[item.item_id] - quantity_in_bundle
            assert updated_item.item_stock == expected_stock

    def test_remove_bundle_from_order_completely(
        self,
        order_service,
        sample_order,
        sample_bundle,
        multiple_items,
        clean_database,
        orderable_dao,
        item_service,
    ):
        """Test removing all bundles from order"""
        orderable_id = sample_bundle.orderable_id

        initial_stocks = {item.item_id: item.item_stock for item in multiple_items[:2]}

        order_service.add_orderable_to_order(orderable_id, sample_order.order_id, 2)

        updated_order = order_service.remove_orderable_from_order(
            orderable_id, sample_order.order_id, 2
        )

        assert updated_order is not None
        assert len(updated_order.order_orderables) == 0

        for item in sample_bundle.bundle_items.keys():
            updated_item = item_service.get_item_by_id(item.item_id)
            assert updated_item.item_stock == initial_stocks[item.item_id]
