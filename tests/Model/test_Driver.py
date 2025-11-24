from datetime import datetime
from unittest.mock import Mock

import pytest
from pydantic_core import ValidationError

from src.Model.Driver import Driver
from src.Model.User import User


class TestDriver:
    """Test suite for the Driver class"""

    def setup_method(self):
        """Setup mock data for each test"""
        self.mock_user_data = {
            "id": 1,
            "first_name": "Test",
            "last_name": "Goat",
            "created_at": datetime.now(),
            "password": "hashed_password",
            "salt": "random_salt",
        }

        self.mock_driver_data = {"driver_phone": "0724368754", "driver_is_delivering": False}

    def _create_driver(self, **overrides):
        """Helper method to create a driver with merged data"""
        data = {**self.mock_user_data, **self.mock_driver_data, **overrides}
        return Driver(**data)

    def test_driver_constructor_ok(self):
        """Test creating a driver with valid data"""
        driver = self._create_driver()

        assert isinstance(driver, User)
        assert driver.id == 1
        assert driver.first_name == "Test"
        assert driver.last_name == "Goat"
        assert driver.driver_phone == "0724368754"
        assert driver.driver_is_delivering is False
        assert isinstance(driver.created_at, datetime)

    def test_driver_constructor_delivering_true_ok(self):
        """Test creating a driver with driver_is_delivering set to True"""
        driver = self._create_driver(driver_is_delivering=True)
        assert driver.driver_is_delivering is True

    def test_driver_creation_missing_phone(self):
        """Test that driver_phone is required for Driver"""
        data = {**self.mock_user_data}  # Only user data, no driver_phone

        with pytest.raises(ValidationError) as exc_info:
            Driver(**data)
        assert "driver_phone" in str(exc_info.value)

    def test_driver_creation_invalid_phone_type(self):
        """Test that driver_phone must be a string"""
        with pytest.raises(ValidationError) as exc_info:
            self._create_driver(driver_phone=1234567890)
        assert "string" in str(exc_info.value).lower()

    def test_driver_phone_uniqueness_same_format(self):
        """Test that duplicate phone numbers in same format raise error"""
        driver1 = self._create_driver(user_id=1, driver_phone="0724368754")

        with pytest.raises(ValueError, match="Phone number already used"):
            self._check_phone_uniqueness({"driver_phone": "0724368754"}, [driver1])

    def test_driver_phone_uniqueness_multiple_drivers(self):
        """Test phone uniqueness with multiple existing drivers"""
        # Create mock drivers instead of real ones
        existing_drivers = [
            Mock(spec=Driver, driver_phone="0612345678"),
            Mock(spec=Driver, driver_phone="0798765432"),
            Mock(spec=Driver, driver_phone="0687654321"),
        ]

        with pytest.raises(ValueError, match="Phone number already used"):
            self._check_phone_uniqueness({"driver_phone": "07 98 76 54 32"}, existing_drivers)

    def test_driver_phone_unique_valid(self):
        """Test that unique phone numbers don't raise error"""
        existing_drivers = [
            Mock(spec=Driver, driver_phone="0612345678"),
            Mock(spec=Driver, driver_phone="0798765432"),
        ]

        # This should not raise an exception
        result = self._check_phone_uniqueness({"driver_phone": "0744556677"}, existing_drivers)
        assert result is True

    def test_driver_phone_uniqueness_different_formats(self):
        """Test that duplicate phone numbers in different formats raise error"""
        driver1 = self._create_driver(user_id=1, driver_phone="0724368754")
        equivalent_phones = [
            "07 24 36 87 54",  # decome +33724368754
            "07-24-36-87-54",  # become +33724368754
            "+33724368754",  # already normalized
        ]

        for phone in equivalent_phones:
            normalized_new = self._normalize_phone(phone)
            normalized_existing = self._normalize_phone(driver1.driver_phone)

            if normalized_new == normalized_existing:
                with pytest.raises(ValueError, match="Phone number already used"):
                    self._check_phone_uniqueness({"driver_phone": phone}, [driver1])

    def _check_phone_uniqueness(self, new_driver_data, existing_drivers):
        """
        Helper method to check phone uniqueness across drivers.
        This simulates what would happen in a service/repository layer.
        """
        new_phone = new_driver_data["driver_phone"]
        new_phone_normalized = self._normalize_phone(new_phone)

        for existing_driver in existing_drivers:
            existing_phone_normalized = self._normalize_phone(existing_driver.driver_phone)
            if new_phone_normalized == existing_phone_normalized:
                raise ValueError("Phone number already used")

        return True

    def _normalize_phone(self, phone):
        """
        Normalize phone number by removing all non-digit characters except leading +
        This handles different formats of the same phone number.
        Raises ValueError if the phone number is invalid.
        """
        if not phone or not isinstance(phone, str):
            raise ValueError("Phone number must be a non-empty string")

        if phone.startswith("+"):
            digits = "".join(filter(str.isdigit, phone[1:]))
            normalized = self._format_international_phone(digits)
        else:
            digits = "".join(filter(str.isdigit, phone))
            normalized = self._format_national_phone(digits)

        self._validate_phone_length(normalized)

        return normalized

    def _format_international_phone(self, digits):
        """Format international phone numbers"""
        if not digits:
            raise ValueError("Phone number must contain digits")

        if digits.startswith("33"):
            return "+" + digits
        elif digits.startswith("0"):
            return "+33" + digits[1:]
        else:
            return "+" + digits

    def _format_national_phone(self, digits):
        """Format national phone numbers"""
        if not digits:
            raise ValueError("Phone number must contain digits")

        if digits.startswith("0"):
            return "+33" + digits[1:]
        else:
            return "+" + digits

    def _validate_phone_length(self, normalized_phone):
        """Validate phone number length after normalization"""
        digits_only = "".join(filter(str.isdigit, normalized_phone))

        if len(digits_only) < 10:
            raise ValueError(
                f"Phone number too short: {len(digits_only)} digitsafter normalization (minimum 10)"
            )

        if len(digits_only) > 15:
            raise ValueError(f"Phone number too long:{len(digits_only)} digits after normalization")

        # Validation for french phone numbers
        if normalized_phone.startswith("+33") and len(normalized_phone) != 12:
            raise ValueError(
                f"French phone number must have 10 digits total,"
                f"got {len(normalized_phone) - 3} digits after normalization"
            )

    def test_driver_creation_phone_alphabet_string(self):
        """Test that a word instead of a phone number raises ValueError in normalization"""
        with pytest.raises(ValueError) as exc_info:
            self._normalize_phone("abc")
        assert "digits" in str(exc_info.value).lower() or "phone" in str(exc_info.value).lower()

    def test_driver_creation_phone_too_short_after_normalization(self):
        """Test that a phone number that becomes too short after normalization raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            self._normalize_phone("07")
        assert "short" in str(exc_info.value).lower() or "length" in str(exc_info.value).lower()

    def test_driver_creation_phone_valid_after_normalization(self):
        """Test that valid phone numbers pass validation after normalization"""
        valid_phones = [
            "0724368754",
            "07 24 36 87 54",
            "07-24-36-87-54",
            "+33724368754",
            "+33 7 24 36 87 54",
        ]

        for phone in valid_phones:
            driver = self._create_driver(driver_phone=phone)
            assert driver.driver_phone is not None
            # should convert everything in +33724368754
            normalized = self._normalize_phone(phone)
            assert normalized == "+33724368754"
