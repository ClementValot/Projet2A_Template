from datetime import datetime

import pytest


class TestCustomerDAO:
    def test_create_customer(self, customer_dao, sample_address, clean_database):
        """Test create a customer"""
        customer = customer_dao.create_customer(
            first_name="Jean",
            last_name="Dupont",
            phone="0612345678",
            mail="jean.dupont@email.com",
            password_hash="hashed_password_123",
            salt="random_salt_456",
            address_id=sample_address.address_id,
        )

        assert customer is not None
        assert customer.id > 0
        assert customer.first_name == "Jean"
        assert customer.last_name == "Dupont"
        assert customer.customer_phone == "0612345678"
        assert customer.customer_mail == "jean.dupont@email.com"
        assert customer.password == "hashed_password_123"
        assert customer.salt.strip() == "random_salt_456"
        assert customer.customer_address is not None
        assert customer.customer_address.address_id == sample_address.address_id
        assert isinstance(customer.created_at, datetime)

    def test_get_customer_by_id_exists(self, customer_dao, sample_customer, clean_database):
        """Test getting a customer by his id"""
        retrieved_customer = customer_dao.get_customer_by_id(sample_customer.id)

        assert retrieved_customer is not None
        assert retrieved_customer.id == sample_customer.id
        assert retrieved_customer.first_name == sample_customer.first_name
        assert retrieved_customer.customer_phone == sample_customer.customer_phone

    def test_get_customer_by_id_not_exists(self, customer_dao, clean_database):
        """Test getting a customer with non-existing id"""
        retrieved_customer = customer_dao.get_customer_by_id(9999)

        assert retrieved_customer is None

    def test_get_customer_loads_address(self, customer_dao, sample_customer, clean_database):
        """Tests that fetching a customer gets his address"""
        retrieved_customer = customer_dao.get_customer_by_id(sample_customer.id)

        assert retrieved_customer.customer_address is not None
        assert (
            retrieved_customer.customer_address.address_id
            == sample_customer.customer_address.address_id
        )

    def test_get_customer_by_email_exists(self, customer_dao, sample_customer, clean_database):
        """Test getting a customer by his mail"""
        retrieved_customer = customer_dao.get_customer_by_email(sample_customer.customer_mail)

        assert retrieved_customer is not None
        assert retrieved_customer.id == sample_customer.id
        assert retrieved_customer.customer_mail == sample_customer.customer_mail

    def test_get_customer_by_email_not_exists(self, customer_dao, clean_database):
        """Test getting a customer by a non-existing mail"""
        retrieved_customer = customer_dao.get_customer_by_email("nonexistent@email.com")

        assert retrieved_customer is None

    def test_get_customer_by_phone_not_exist(self, customer_dao, clean_database):
        retrieved_customer = customer_dao.get_customer_by_phone("0668749528")

        assert retrieved_customer is None

    def test_get_customer_by_phone_exist(self, customer_dao, sample_customer, clean_database):
        retrieved_customer = customer_dao.get_customer_by_phone(sample_customer.customer_phone)
        assert retrieved_customer is not None
        assert retrieved_customer.id == sample_customer.id
        assert retrieved_customer.customer_phone == sample_customer.customer_phone

    def test_get_all_customers_empty(self, customer_dao, clean_database):
        """Test get_all_customer when there are no customers"""
        customers = customer_dao.get_all_customers()

        assert customers == []

    def test_update_customer_multiple_fields(self, customer_dao, sample_customer, clean_database):
        """Test updating multiple fields"""
        updated_customer = customer_dao.update_customer(
            sample_customer.id,
            {
                "customer_first_name": "Pierre",
                "customer_last_name": "Durand",
                "customer_phone": "0688888888",
            },
        )

        assert updated_customer.first_name == "Pierre"
        assert updated_customer.last_name == "Durand"
        assert updated_customer.customer_phone == "0688888888"
        assert updated_customer.customer_mail == sample_customer.customer_mail

    def test_update_customer_invalid_field_raises_error(
        self, customer_dao, sample_customer, clean_database
    ):
        """Test invalid field raises error"""
        with pytest.raises(ValueError, match="not a parameter of Customer"):
            customer_dao.update_customer(sample_customer.id, {"invalid_field": "value"})

    def test_delete_customer(self, customer_dao, sample_customer, clean_database):
        """Test deleting customer"""
        customer_id = sample_customer.id

        customer_dao.delete_customer(customer_id)

        retrieved_customer = customer_dao.get_customer_by_id(customer_id)
        assert retrieved_customer is None
