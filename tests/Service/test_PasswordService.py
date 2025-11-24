from datetime import datetime
from typing import Optional

import pytest

from src.Model.User import User
from src.Service.PasswordService import (
    check_password_strength,
    create_salt,
    hash_password,
    validate_password,
)


def test_hash_password():
    password = "soleil1234"
    salt = "jambon"
    hashed_password = hash_password(password, salt)

    assert hashed_password == "56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a"


def test_create_salt():
    salt = create_salt()

    assert isinstance(salt, str)
    assert len(salt) == 256


def test_create_salt_is_unique():
    salt1 = create_salt()
    salt2 = create_salt()
    salt3 = create_salt()

    assert salt1 != salt2
    assert salt2 != salt3
    assert salt1 != salt3


def test_check_password_strength_ok():
    assert check_password_strength("Hieic54@") is True
    assert check_password_strength("M3rf654!!F") is True
    assert check_password_strength("GGGGjefonep0846bcb@") is True


def test_check_password_strength_too_short():
    with pytest.raises(ValueError, match="Length should be at least 6 characters"):
        check_password_strength("abc")


def test_check_password_strength_no_digit():
    with pytest.raises(ValueError, match="Password should have at least one numeral"):
        check_password_strength("Abcdef@")


def test_check_password_strength_no_uppercase():
    with pytest.raises(ValueError, match="Password should have at least one uppercase letter"):
        check_password_strength("abcd123@")


def test_check_password_strength_no_lowercase():
    with pytest.raises(ValueError, match="Password should have at least one lowercase letter"):
        check_password_strength("ABCD123@")


def test_check_password_strength_no_special_char():
    with pytest.raises(ValueError, match="Password should have at least one special symbol"):
        check_password_strength("M3rf654F")


class MockUserRepo:
    def get_by_id(self, user_id: int) -> Optional[User]:
        if user_id == 4:
            return User(
                id=4,
                first_name="janjak",
                last_name="jakjan",
                created_at=datetime.now(),
                password="56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a",
                salt="jambon",
            )
        elif user_id == 7:
            return User(
                id=7,
                first_name="janjak",
                last_name="jakjan",
                created_at=datetime.now(),
                password="56d25b0190eb6fcdab76f20550aa3e85a37ee48d520ac70385ae3615deb7d53a",
                salt="jambon",
            )
        else:
            return None


user_repo = MockUserRepo()


def test_validate_password_ok():
    janjak = validate_password(MockUserRepo.get_by_id(user_repo, 4), "soleil1234")
    assert janjak.id == 4


def test_validate_password_incorrect():
    with pytest.raises(ValueError, match="Incorrect password"):
        validate_password(MockUserRepo.get_by_id(user_repo, 4), "motdepassefaux")


def test_validate_password_user_not_found():
    with pytest.raises(ValueError, match="User not found"):
        validate_password(None, "soleil1234")
