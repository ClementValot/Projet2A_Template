from datetime import datetime

import pytest
from pydantic_core import ValidationError

from src.Model.User import User


def test_user_constructor_ok():
    user = User(
        id=1,
        first_name="John",
        last_name="Smith",
        created_at=datetime(2023, 1, 15, 10, 30, 0),
        password="hashed_password_123",
        salt="unique_salt_abc",
    )

    assert isinstance(user, User)
    assert user.id == 1
    assert user.first_name == "John"
    assert user.last_name == "Smith"
    assert user.created_at == datetime(2023, 1, 15, 10, 30, 0)
    assert user.password == "hashed_password_123"
    assert user.salt == "unique_salt_abc"
    assert user.user_role == "customer"


def test_user_constructor_throws_on_incorrect_id():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id="not_an_integer",
            first_name="John",
            last_name="Doe",
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            password="hashed_password_123",
            salt="unique_salt_abc",
        )
    assert "id" in str(exception_info.value) and "Input should be a valid integer" in str(
        exception_info.value
    )


def test_user_constructor_throws_on_incorrect_datetime():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            first_name="John",
            last_name="Doe",
            created_at="not_a_datetime",
            password="hashed_password_123",
            salt="unique_salt_abc",
        )
    assert "created_at" in str(exception_info.value) and "Input should be a valid datetime" in str(
        exception_info.value
    )


def test_user_constructor_throws_on_missing_required_field():
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            first_name="John",
            # Missing last_name
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            password="hashed_password_123",
            salt="unique_salt_abc",
        )
    assert "last_name" in str(exception_info.value) and "Field required" in str(
        exception_info.value
    )


def test_user_constructor_with_optional_fields_missing():
    # This test verifies that all fields are required (no optional fields in the class)
    with pytest.raises(ValidationError) as exception_info:
        User(
            id=1,
            first_name="John",
            last_name="Doe",
            created_at=datetime(2023, 1, 15, 10, 30, 0),
            # Missing password and salt
        )
    # Should complain about missing password and salt fields
    error_str = str(exception_info.value)
    assert "password" in error_str and "Field required" in error_str
    assert "salt" in error_str and "Field required" in error_str
