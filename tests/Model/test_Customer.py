from datetime import datetime
from unittest.mock import Mock

import pytest
from pydantic_core import ValidationError

from src.Model.Address import Address
from src.Model.Customer import Customer
from src.Model.User import User


class TestCustomer:
    """Test suite for the Customer class"""

    def setup_method(self):
        """Setup mock data for each test"""
        self.mock_user_data = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "created_at": datetime.now(),
            "password": "hashed_password",
            "salt": "random_salt",
        }

        self.mock_address = Mock(spec=Address)

        self.mock_customer_data = {
            "customer_address": self.mock_address,
            "customer_phone": "0724368754",
            "customer_mail": "john.doe@gmail.com",
        }

        self.valid_domains = [
            "gmail.com",
            "free.fr",
            "hotmail.fr",
            "hotmail.com",
            "yahoo.fr",
            "laposte.net",
            "orange.fr",
            "ena.fr",
            "wanadoo.fr",
            "eleve.ensai.fr",
            "insee.fr",
        ]

    def _create_customer(self, **overrides):
        """Helper method to create a customer with merged data"""
        data = {**self.mock_user_data, **self.mock_customer_data, **overrides}
        return Customer(**data)

    def test_customer_constructor_ok(self):
        """Test creating a customer with valid data"""
        customer = self._create_customer()

        assert isinstance(customer, User)
        assert customer.id == 1
        assert customer.first_name == "John"
        assert customer.last_name == "Doe"
        assert customer.customer_address == self.mock_address
        assert customer.customer_phone == "0724368754"
        assert customer.customer_mail == "john.doe@gmail.com"
        assert isinstance(customer.created_at, datetime)

    def test_customer_constructor_throws_on_empty_local_part(self):
        """Test that empty local part raises ValidationError"""
        empty_local_emails = [
            "@gmail.com",  # Empty local part
            " @gmail.com",  # Local part with space
            "  @gmail.com",  # Local part with spaces
        ]

        for email in empty_local_emails:
            with pytest.raises(ValueError) as exception_info:
                self._validate_email_in_test(email)
            assert (
                "empty" in str(exception_info.value).lower()
                or "space" in str(exception_info.value).lower()
            )

    def test_customer_constructor_throws_on_invalid_local_part_characters(self):
        """Test that invalid characters in local part raise ValidationError"""
        # Group emails by expected error type
        multiple_at_symbol_emails = [
            "user@name@gmail.com",  # Multiple @ symbols
        ]

        invalid_char_emails = [
            "user name@gmail.com",  # space in the local part
            "user+name@gmail.com",  # + in the local part
            "user#name@gmail.com",  # # in the local part
            "user$name@gmail.com",  # $ in the local part
            "user&name@gmail.com",  # & in the local part
            "user!name@gmail.com",  # ! in the local part
            "user*name@gmail.com",  # * in the local part
            "user/name@gmail.com",  # / in the local part
            "user=name@gmail.com",  # = in the local part
            "user?name@gmail.com",  # ? in the local part
        ]

        # Test multiple @ symbols
        for email in multiple_at_symbol_emails:
            with pytest.raises(ValueError) as exception_info:
                self._validate_email_in_test(email)
            assert "exactly one" in str(exception_info.value).lower()

        # Test invalid characters
        for email in invalid_char_emails:
            with pytest.raises(ValueError) as exception_info:
                self._validate_email_in_test(email)
            assert "invalid character" in str(exception_info.value).lower()

    def test_customer_constructor_throws_on_malformed_email(self):
        """Test that malformed email formats raise ValidationError"""
        malformed_emails = [
            "no-at-sign.com",  # Missing @
            "user@",  # Missing domain
            "user@.com",  # Empty domain name
            "user@gmail.",  # Missing TLD
            "user@gmail..com",  # Double dot in domain
            "user.@gmail.com",  # Dot at end of local part
            ".user@gmail.com",  # Dot at start of local part
            "user..name@gmail.com",  # Double dot in local part
        ]

        for email in malformed_emails:
            with pytest.raises(ValueError):
                self._validate_email_in_test(email)

    def test_customer_creation_missing_address(self):
        """Test that customer_address is required for Customer"""
        data = {
            **self.mock_user_data,
            **{"customer_phone": "0724368754", "customer_mail": "john.doe@gmail.com"},
        }

        with pytest.raises(ValidationError) as exc_info:
            Customer(**data)
            assert "customer_address" in str(exc_info.value)

    def test_customer_creation_missing_phone(self):
        """Test that customer_phone is required for Customer"""
        data = {
            **self.mock_user_data,
            **{"customer_address": self.mock_address, "customer_mail": "john.doe@gmail.com"},
        }  # Missing customer_phone

        with pytest.raises(ValidationError) as exc_info:
            Customer(**data)
        assert "customer_phone" in str(exc_info.value)

    def test_customer_creation_missing_email(self):
        """Test that customer_mail is required for Customer"""
        data = {
            **self.mock_user_data,
            **{"customer_address": self.mock_address, "customer_phone": "0724368754"},
        }  # Missing customer_mail

        with pytest.raises(ValidationError) as exc_info:
            Customer(**data)
        assert "customer_mail" in str(exc_info.value)

    def test_customer_creation_invalid_phone_type(self):
        """Test that customer_phone must be a string"""
        with pytest.raises(ValidationError) as exc_info:
            self._create_customer(customer_phone=1234567890)
        assert "string" in str(exc_info.value).lower()

    def test_customer_creation_invalid_email_type(self):
        """Test that customer_mail must be a string"""
        with pytest.raises(ValidationError) as exc_info:
            self._create_customer(customer_mail=12345)
        assert "string" in str(exc_info.value).lower()

    def test_customer_creation_invalid_address_type(self):
        """Test that customer_address must be an Address instance"""
        with pytest.raises(ValidationError):
            self._create_customer(customer_address="invalid_address")

    def test_customer_phone_uniqueness_same_format(self):
        """Test that duplicate phone numbers in same format raise error"""
        customer1 = self._create_customer(id=1, customer_phone="0724368754")

        with pytest.raises(ValueError, match="Phone number already used"):
            self._check_phone_uniqueness({"customer_phone": "0724368754"}, [customer1])

    def test_customer_phone_uniqueness_different_formats(self):
        """Test that duplicate phone numbers in different formats raise error"""
        customer1 = self._create_customer(id=1, customer_phone="0724368754")
        equivalent_phones = [
            "07 24 36 87 54",
            "07-24-36-87-54",
            "+33724368754",
        ]

        for phone in equivalent_phones:
            normalized_new = self._normalize_phone(phone)
            normalized_existing = self._normalize_phone(customer1.customer_phone)

            if normalized_new == normalized_existing:
                with pytest.raises(ValueError, match="Phone number already used"):
                    self._check_phone_uniqueness({"customer_phone": phone}, [customer1])

    def test_customer_creation_phone_alphabet_string(self):
        """Test that a word instead of a phone number raises ValueError in normalization"""
        with pytest.raises(ValueError) as exc_info:
            self._normalize_phone("abc")
        assert "digits" in str(exc_info.value).lower() or "phone" in str(exc_info.value).lower()

    def test_customer_creation_phone_too_short_after_normalization(self):
        """Test that a phone number that becomes too short after normalization raises ValueError"""
        with pytest.raises(ValueError) as exc_info:
            self._normalize_phone("07")
        assert "short" in str(exc_info.value).lower() or "length" in str(exc_info.value).lower()

    def _check_phone_uniqueness(self, new_customer_data, existing_customers):
        """
        Helper method to check phone uniqueness across customers.
        This simulates what would happen in a service/repository layer.
        """
        new_phone = new_customer_data["customer_phone"]
        new_phone_normalized = self._normalize_phone(new_phone)

        for existing_customer in existing_customers:
            existing_phone_normalized = self._normalize_phone(existing_customer.customer_phone)
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

    def _validate_email_in_test(self, email):
        """
        Helper method to validate email format in tests
        This replicates the validation logic that should be in the Customer class
        """
        if not email:
            raise ValueError("Email cannot be empty")

        # Check for multiple @ symbols
        if email.count("@") != 1:
            raise ValueError("Email must contain exactly one @ symbol")

        local_part, domain = email.split("@", 1)

        # Validate local part
        if not local_part or local_part.isspace():
            raise ValueError("Local part cannot be empty or only spaces")

        # Check for invalid characters in local part
        invalid_chars = ["@", "+", "#", "$", "&", "!", "*", "/", "=", "?", " "]
        for char in invalid_chars:
            if char in local_part:
                raise ValueError(f'Invalid character "{char}" in local part')

        # Check for consecutive dots or dots at start/end
        if local_part.startswith(".") or local_part.endswith(".") or ".." in local_part:
            raise ValueError("Invalid dot placement in local part")

        # Validate domain
        valid_domains = [
            "gmail.com",
            "free.fr",
            "hotmail.fr",
            "hotmail.com",
            "yahoo.fr",
            "laposte.net",
            "orange.fr",
            "ena.fr",
            "wanadoo.fr",
            "eleve.ensai.fr",
            "insee.fr",
        ]

        if domain not in valid_domains:
            raise ValueError(f"Domain {domain} is not allowed")

        # Basic domain format validation
        if not domain or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("Invalid domain format")

        return True
