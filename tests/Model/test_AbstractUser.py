from datetime import date

import pytest
from pydantic_core import ValidationError

from src.Model.abstract_user import AbstractUser


class DummyUser(AbstractUser):
    role: str = "tester"


def test_dummy_user_ok():
    user = DummyUser(
        id_user=1,
        username="u",
        hash_password="hashed",
        salt="xyz",
        sign_up_date=date.today(),
        role="tester",
    )
    assert user.id_user == 1
    assert user.username == "u"
    assert user.role == "tester"


def test_dummy_user_invalid_id():
    with pytest.raises(ValidationError):
        DummyUser(
            id_user="wrong",
            username="u",
            hash_password="hashed",
            salt="xyz",
            sign_up_date=date.today(),
            role="tester",
        )
