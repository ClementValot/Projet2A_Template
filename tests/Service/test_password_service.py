import pytest

from src.Service.password_service import PasswordService


@pytest.fixture
def service():
    """
    Provides a PasswordService instance.
    """
    return PasswordService()


def test_hash_password_with_known_salt(service: PasswordService):
    """
    Tests hashing a known password/salt pair yields a known hash.
    """
    password = "soleil1234"
    salt = "jambon"
    expected_hash = "7877d4860ef88458096f549b618667d860540db5d59b1d153557d5cdbe1221e7"

    hashed_password = service.hash_password(password, salt)

    assert hashed_password == expected_hash


def test_hash_password_requires_salt(service: PasswordService):
    """
    Tests that hash_password raises ValueError if no salt is provided (empty string).
    """
    password = "onepassword"

    with pytest.raises(ValueError) as e:
        service.hash_password(password, "")

    assert "Salt must be provided for secure hashing." in str(e.value)


def test_different_salts_produce_different_hashes(service: PasswordService):
    """
    Tests that the same password with different salts produces different hashes.
    """
    password = "mysecretpassword"
    salt1 = "salt_A"
    salt2 = "salt_B"

    hash1 = service.hash_password(password, salt1)
    hash2 = service.hash_password(password, salt2)

    assert hash1 != hash2


def test_hash_is_consistent(service: PasswordService):
    """
    Tests that hashing the same password and salt multiple times yields the same hash.
    """
    password = "consistent123"
    salt = "fixed_salt"

    hash1 = service.hash_password(password, salt)
    hash2 = service.hash_password(password, salt)

    assert hash1 == hash2


def test_create_salt_length(service: PasswordService):
    """
    Tests that create_salt returns a 64-character hex string (32 bytes).
    """
    salt = service.create_salt()
    assert len(salt) == 64
    assert all(c in "0123456789abcdef" for c in salt)


def test_strength_valid_password(service: PasswordService):
    """
    Tests that a valid password (length and 4/4 score) passes the check.
    """
    try:
        assert service.check_password_strength("MyStrongP@ss1") is True
        assert service.check_password_strength("P@ssw0rdA") is True
    except Exception as e:
        pytest.fail(f"check_password_strength raised an unexpected exception: {e}")


@pytest.mark.parametrize(
    "invalid_password, error_message_part",
    [
        ("short1!", "The password must be at least 8 characters long."),
        ("", "The password must be at least 8 characters long."),
        ("password", "The password is one of the most commonly used passwords and is prohibited."),
        ("12345678", "The password is one of the most commonly used passwords and is prohibited."),
        ("motdepasse", "The password is one of the most commonly used passwords and is prohibited."),
    ],
)
def test_strength_length_and_common_passwords(service: PasswordService, invalid_password, error_message_part):
    """
    Tests rules for minimum length and forbidden common passwords.
    """
    with pytest.raises(ValueError) as e:
        service.check_password_strength(invalid_password)

    assert error_message_part in str(e.value)


@pytest.mark.parametrize(
    "low_score_password, missing_char_type",
    [
        ("Password123", "special"),
        ("password123!", "capital letter"),
        ("Password!", "digit"),
        ("PASSWORD123!", "lower letter"),
        ("azertyuiop", "all character types"),
    ],
)
def test_strength_low_score(service: PasswordService, low_score_password, missing_char_type):
    """
    Tests that passwords failing the minimum score rule (4/4) raise a ValueError.
    """
    with pytest.raises(ValueError) as e:
        service.check_password_strength(low_score_password)

    assert "Your password must have all character types" in str(e.value)
    assert "You actually have" in str(e.value)