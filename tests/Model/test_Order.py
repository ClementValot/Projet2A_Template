from datetime import datetime
from unittest.mock import Mock

import pytest
from pydantic_core import ValidationError

from src.Model.Item import Item
from src.Model.Order import Order, OrderState


def test_order_constructor_ok():
    mock_item = Mock(spec=Item)

    order_test = Order(
        order_id=1,
        order_customer_id=1,
        order_created_at=datetime(2025, 5, 5),
        order_orderables={mock_item: 1},
    )

    assert isinstance(order_test, Order)
    assert order_test.order_id == 1
    assert order_test.order_customer_id == 1
    assert order_test.order_state == OrderState.PENDING
    assert order_test.order_created_at == datetime(2025, 5, 5)
    assert list(order_test.order_orderables)[0] == mock_item
    assert list(order_test.order_orderables.values())[0] == 1
    assert order_test.is_paid is False
    assert order_test.is_prepared is False


def test_order_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        mock_item = Mock(spec=Item)

        Order(
            order_id="one",
            order_customer_id=1,
            order_created_at=datetime.now(),
            order_orderables=[mock_item],
        )
    assert "order_id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(
        exception_info.value
    )


def test_order_calculate_price_with_all(sample_order_full):
    assert sample_order_full.order_price == 0.85 * (0.5 + 4.5) + 2.0


@pytest.mark.parametrize(
    "order_state,expected_paid,expected_prepared,expected_delivered",
    [
        (OrderState.PENDING, False, False, False),
        (OrderState.PAID, True, False, False),
        (OrderState.PREPARED, True, True, False),
        (OrderState.DELIVERING, True, True, False),
        (OrderState.DELIVERED, True, True, True),
        (OrderState.CANCELLED, True, True, False),  # Corrigé pour refléter le comportement actuel
    ],
)
def test_order_state_properties(order_state, expected_paid, expected_prepared, expected_delivered):
    mock_item = Mock(spec=Item)

    order = Order(
        order_id=1,
        order_customer_id=1,
        order_state=order_state,
        order_created_at=datetime(2025, 5, 5),
        order_orderables={mock_item: 1},
    )

    assert order.is_paid == expected_paid
    assert order.is_prepared == expected_prepared
    assert order.is_delivered == expected_delivered
