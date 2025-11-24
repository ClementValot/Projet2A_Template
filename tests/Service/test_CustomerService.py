import re

import pytest


class TestCustomerService:
    def test_get_customer_by_id_exists(self, customer_service, sample_customer, clean_database):
        """Test getting a customer by id"""
        retrieved_customer = customer_service.get_customer_by_id(sample_customer.id)

        assert retrieved_customer is not None
        assert retrieved_customer.id == sample_customer.id
        assert retrieved_customer.first_name == sample_customer.first_name
        assert retrieved_customer.customer_mail == sample_customer.customer_mail

    def test_get_customer_by_id_not_exists(self, customer_service, clean_database):
        """Test getting customer by non-existing id raises error"""
        with pytest.raises(ValueError, match="Cannot find: customer with ID 9999 not found"):
            customer_service.get_customer_by_id(9999)

    def test_get_customer_by_email_exists(self, customer_service, sample_customer, clean_database):
        """Test getting a customer by email"""
        retrieved_customer = customer_service.get_customer_by_email(sample_customer.customer_mail)

        assert retrieved_customer is not None
        assert retrieved_customer.id == sample_customer.id
        assert retrieved_customer.customer_mail == sample_customer.customer_mail

    def test_get_customer_by_email_not_exists(self, customer_service, clean_database):
        """Test getting customer by non-existing email returns None"""
        with pytest.raises(ValueError, match="customer with email nonexistent@email.com not found"):
            customer_service.get_customer_by_email("nonexistent@email.com")

    def test_get_customer_by_phone_exists(self, customer_service, sample_customer, clean_database):
        """Test getting a customer by phone"""
        retrieved_customer = customer_service.get_customer_by_phone(sample_customer.customer_phone)

        assert retrieved_customer is not None
        assert retrieved_customer.id == sample_customer.id
        assert retrieved_customer.customer_phone == sample_customer.customer_phone

    def test_get_customer_by_phone_not_exists(self, customer_service, clean_database):
        """Test getting customer by non-existing phone returns None"""
        with pytest.raises(ValueError, match="not found"):
            customer_service.get_customer_by_phone("+33699999999")

    def test_get_all_customers_empty(self, customer_service, clean_database):
        """Test getting all customers when there are none"""
        customers = customer_service.get_all_customers()

        assert customers == []

    def test_get_all_customer_multiple(
        self, customer_service, address_dao, customer_dao, clean_database
    ):
        """Test getting all customers"""
        address = address_dao.create_address(1, "Rue Test", "Rennes", 35000, "France")
        address = address_dao.create_address(2, "Rue Test", "Rennes", 35000, "France")
        address = address_dao.create_address(3, "Rue Test", "Rennes", 35000, "France")

        customer_dao.create_customer(
            "A", "A", "0601", "a@test.com", "hash", "salt", address.address_id
        )
        customer_dao.create_customer(
            "B", "B", "0602", "b@test.com", "hash", "salt", address.address_id
        )
        customer_dao.create_customer(
            "C", "C", "0603", "c@test.com", "hash", "salt", address.address_id
        )

        customers = customer_service.get_all_customers()

        assert customers != []
        assert len(customers) == 3

    def test_create_customer_success(self, customer_service, clean_database):
        """Test creating a customer successfully"""
        created_customer = customer_service.create_customer(
            first_name="Test",
            last_name="User",
            phone="0612345678",
            mail="test@email.com",
            password="V4lidP@ssword",
            address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
        )

        assert created_customer is not None
        assert created_customer.id > 0
        assert created_customer.first_name == "Test"
        assert created_customer.last_name == "USER"
        assert created_customer.customer_phone == "+33612345678"
        assert created_customer.customer_mail == "test@email.com"
        assert created_customer.customer_address is not None

    def test_create_customer_duplicate_email_raises_error(
        self, customer_service, sample_customer, clean_database
    ):
        """Test creating customer with duplicate email raises error"""
        with pytest.raises(ValueError, match="already associated"):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone="+33698765432",
                mail=sample_customer.customer_mail,
                password="V4lidP@ssword",
                address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
            )

    @pytest.mark.parametrize(
        "customer_email",
        [
            "12enlesn345",
            "0653564432",
            "alras@notavaliddomain.notvalidending",
        ],
    )
    def test_create_customer_invalid_email_raises_error(
        self, customer_service, sample_customer, clean_database, customer_email
    ):
        """Test creating customer with invalid email raises error"""
        with pytest.raises(ValueError, match="Please enter a valid email !"):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone="+33698765432",
                mail=customer_email,
                password="V4lidP@ssword",
                address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
            )

    def test_create_customer_duplicate_phone_raises_error(
        self, customer_service, sample_customer, clean_database
    ):
        """Test creating customer with duplicate phone raises error"""
        with pytest.raises(ValueError, match="already associated"):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone=sample_customer.customer_phone,
                mail="newtest@email.com",
                password="V4lidP@ssword",
                address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
            )

    @pytest.mark.parametrize(
        "customer_phone",
        ["12345", "notaphone", "+33 6 12 34", "waluigi@gmail.com"],
    )
    def test_create_customer_invalid_phone_raises_error(
        self, customer_service, sample_customer, clean_database, customer_phone
    ):
        """Test creating customer with invalid phone raises error"""
        with pytest.raises(ValueError, match="invalid|valid|associated"):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone=customer_phone,
                mail="newtest@email.com",
                password="V4lidP@ssword",
                address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
            )

    @pytest.mark.parametrize(
        ("customer_first_name", "customer_last_name"),
        [
            ("12345", "User"),
            ("Test", "12345"),
            ("12345", "6789#"),
        ],
    )
    def test_create_customer_invalid_name_raises_error(
        self,
        customer_service,
        sample_customer,
        clean_database,
        customer_first_name,
        customer_last_name,
    ):
        """Test creating customer with invalid name raises error"""
        with pytest.raises(ValueError, match="only contain letters"):
            customer_service.create_customer(
                first_name=customer_first_name,
                last_name=customer_last_name,
                phone="+33698765432",
                mail="newtest@email.com",
                password="V4lidP@ssword",
                address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
            )

    def test_create_customer_weak_password_raises_error(self, customer_service, clean_database):
        """Test creating customer with weak password raises error"""
        with pytest.raises(ValueError):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone="0612345678",
                mail="test@email.com",
                password="weak",
                address_string="51 Rue Blaise Pascal, 35170 Bruz, France",
            )

    def test_create_customer_invalid_address_raises_error(self, customer_service, clean_database):
        """Test creating customer with invalid address raises error"""
        with pytest.raises(ValueError, match=re.escape("[GoogleMapService]: Invalid address.")):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone="0612345678",
                mail="test@email.com",
                password="V4lidP@ssword",
                address_string="Invalid Address XYZ",
            )

    def test_create_customer_address_too_far_raises_error(self, customer_service, clean_database):
        """Test creating customer with address too far raises error"""
        with pytest.raises(
            ValueError,
            match=re.escape("[GoogleMapService]: Destination is too far away."),
        ):
            customer_service.create_customer(
                first_name="Test",
                last_name="User",
                phone="0612345678",
                mail="test@email.com",
                password="V4lidP@ssword",
                address_string="5, avenue faubourg saint honoré, paris",
            )

    def test_update_customer(self, customer_service, sample_customer, clean_database):
        """Test updating a customer"""
        updated_customer = customer_service.update_customer(
            sample_customer.id,
            {
                "customer_first_name": "UpdatedName",
                "customer_last_name": "UpdatedLastName",
            },
        )

        assert updated_customer.first_name == "Updatedname"
        assert updated_customer.last_name == "UPDATEDLASTNAME"
        assert updated_customer.customer_mail == sample_customer.customer_mail

    def test_delete_customer(self, customer_service, sample_customer, clean_database):
        """Test deleting a customer"""
        customer_service.delete_customer(sample_customer.id)

        with pytest.raises(ValueError, match="Cannot find: customer with ID .* not found"):
            customer_service.get_customer_by_id(sample_customer.id)

    def test_delete_customer_not_exists_raises_error(self, customer_service, clean_database):
        """Test deleting non-existing customer raises error"""
        with pytest.raises(ValueError, match="Cannot find: customer with ID 9999 not found"):
            customer_service.delete_customer(9999)
