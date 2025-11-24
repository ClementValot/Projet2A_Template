from datetime import datetime
from unittest.mock import Mock

import pytest
from pydantic_core import ValidationError

from src.Model.Bundle import Bundle
from src.Model.Item import Item


def test_order_constructor_ok(sample_item):
    bundle_test = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={sample_item: 1},
    )

    assert isinstance(bundle_test, Bundle)
    assert bundle_test.bundle_id == 1
    assert bundle_test.orderable_id == 1
    assert bundle_test.orderable_type == "bundle"
    assert bundle_test.bundle_name == "Menu"
    assert bundle_test.bundle_reduction == 25
    assert bundle_test.bundle_description == "Menu classique"
    assert bundle_test.bundle_availability_start_date == datetime(2025, 10, 9, 12, 30, 0)
    assert bundle_test.bundle_availability_end_date == datetime(2025, 10, 9, 13, 0, 0)
    assert list(bundle_test.bundle_items)[0] == sample_item
    assert list(bundle_test.bundle_items.values())[0] == 1


def test_order_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        mock_item = Mock(spec=Item)

        Bundle(
            bundle_id="one",
            orderable_id=1,
            bundle_name="Menu",
            bundle_reduction=25,
            bundle_description="Menu classique",
            bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
            bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
            bundle_items={mock_item: 1},
        )
    assert "bundle_id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(
        exception_info.value
    )


def test_bundle_price(sample_item):
    bundle = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={sample_item: 1},
    )
    assert bundle.price == sample_item.price * (1 - bundle.bundle_reduction / 100)


@pytest.mark.parametrize(
    "params, response",
    [
        ((datetime(2025, 10, 9, 12, 30, 0), datetime(2026, 10, 9, 12, 30, 0)), True),
        ((datetime(2025, 10, 9, 12, 30, 0), datetime(2025, 10, 9, 13, 0, 0)), False),
    ],
)
def test_bundle_check_availability_true(params, response, sample_item):
    bundle = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=params[0],
        bundle_availability_end_date=params[1],
        bundle_items={sample_item: 1},
        is_in_menu=True,
    )

    assert bundle.check_availability() is response


@pytest.mark.parametrize(
    "test",
    [
        1,
        "Item",
        Bundle(
            bundle_id=1,
            orderable_id=2,
            bundle_name="Menu",
            bundle_reduction=25,
            bundle_description="Menu classique",
            bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
            bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
            bundle_items={},
        ),
    ],
)
def test_bundle_not_equal(test, sample_item):
    bundle1 = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={},
    )

    assert not bundle1 == test


def test_bundles_equal(sample_item):
    bundle1 = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={sample_item: 1},
    )
    bundle2 = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={sample_item: 1},
    )
    assert bundle1 == bundle2


def test_bundle_hash(sample_item):
    bundle = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={sample_item: 1},
    )

    assert hash(bundle) == hash(1)
    assert isinstance(hash(bundle), int)


def test_bundle_check_stock():
    # Create a fully configured mock item
    mock_item = Mock(spec=Item)
    mock_item.check_stock.return_value = True
    mock_item.check_availability.return_value = True
    mock_item.item_stock = 10  # Add the missing attribute

    bundle = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={mock_item: 2},
    )

    assert bundle.check_stock(1) is True
    mock_item.check_stock.assert_called_once_with(2)  # 1 * 2 = 2


def test_bundle_get_stock(sample_item):
    # Configure the item to have a specific stock
    sample_item.item_stock = 10

    bundle = Bundle(
        bundle_id=1,
        orderable_id=1,
        bundle_name="Menu",
        bundle_reduction=25,
        bundle_description="Menu classique",
        bundle_availability_start_date=datetime(2025, 10, 9, 12, 30, 0),
        bundle_availability_end_date=datetime(2025, 10, 9, 13, 0, 0),
        bundle_items={sample_item: 3},  # Each bundle requires 3 of this item
    )

    # 10 / 3 = 3.33, so bottleneck should be 3
    assert bundle.get_stock() == 3
