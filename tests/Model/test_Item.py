import pytest
from pydantic_core import ValidationError

from src.Model.Item import Item


#
def test_item_constructor_ok():
    item_test = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=10,
    )

    assert item_test.item_id == 1
    assert item_test.orderable_type == "item"
    assert item_test.orderable_id == 1
    assert item_test.item_name == "Coca"
    assert item_test.item_price == 1.5
    assert item_test.item_type == "Drink"
    assert item_test.item_description == "canette 33cl"
    assert item_test.item_stock == 10
    assert item_test.is_in_menu is False


def test_item_constructor_throws_on_incorrect_input():
    with pytest.raises(ValidationError) as exception_info:
        Item(
            item_id="one",
            orderable_id=1,
            item_name="Coca",
            item_price=1.5,
            item_type="Drink",
            item_description="canette 33cl",
            item_stock=10,
        )
    assert "item_id" in str(
        exception_info.value
    ) and "Input should be a valid integer, unable to parse string as an integer" in str(
        exception_info.value
    )


@pytest.mark.parametrize(
    "test",
    [
        1,
        "Item",
        Item(
            item_id=1,
            orderable_id=2,
            item_name="Coca",
            item_price=1.5,
            item_type="Drink",
            item_description="canette 33cl",
            item_stock=10,
        ),
    ],
)
def test_item_not_equal(test):
    item1 = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=10,
    )

    assert not item1 == test


def test_items_equal():
    item1 = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=10,
    )
    item2 = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=10,
    )

    assert item1 == item2


def test_item_hash():
    item = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=10,
    )

    assert hash(item) == hash(1)
    assert isinstance(hash(item), int)


def test_item_price_property():
    item = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=10,
    )

    assert item.price == 1.5


@pytest.mark.parametrize(
    "stock,is_in_menu,expected",
    [
        (10, True, True),  # Stock > 0 and in menu
        (0, True, False),  # Stock = 0 and in menu
        (0, False, False),  # Stock = 0 and not in menu
    ],
)
def test_item_check_availability(stock, is_in_menu, expected):
    item = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=stock,
        is_in_menu=is_in_menu,
    )

    assert item.check_availability() == expected


@pytest.mark.parametrize(
    "stock,quantity,expected",
    [
        (10, 5, True),  # 10 - 5 >= 0
        (10, 10, True),  # 10 - 10 >= 0
        (10, 11, False),  # 10 - 11 < 0
        (0, 1, False),  # 0 - 1 < 0
    ],
)
def test_item_check_stock(stock, quantity, expected):
    item = Item(
        item_id=1,
        orderable_id=1,
        item_name="Coca",
        item_price=1.5,
        item_type="Drink",
        item_description="canette 33cl",
        item_stock=stock,
    )

    assert item.check_stock(quantity) == expected
