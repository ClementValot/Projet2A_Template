from datetime import datetime

import pytest
from pydantic_core import ValidationError

from src.Model.Delivery import Delivery


def test_delivery_constructor_ok():
    delivery_test = Delivery(
        delivery_order_id=1,
        delivery_driver_id=1,
        delivery_state=0,
        delivery_created_at=datetime.now(),
    )

    assert isinstance(delivery_test, Delivery)
    assert delivery_test.delivery_order_id == 1
    assert delivery_test.delivery_driver_id == 1
    assert delivery_test.delivery_state == 0


def test_delivery_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        Delivery(delivery_order_id="one", delivery_driver_id=1, delivery_state=0)
    assert "delivery_order_id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(
        exception_info.value
    )
