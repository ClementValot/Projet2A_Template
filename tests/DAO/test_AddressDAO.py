import pytest


class TestAddressDAO:
    def test_create_address(self, address_dao, clean_database):
        """Test creation of an address"""
        address = address_dao.create_address(51, "Rue Blaise Pascal", "Bruz", 35170, "France")

        assert address is not None
        assert address.address_id > 0
        assert address.address_number == 51
        assert address.address_street == "Rue Blaise Pascal"
        assert address.address_city == "Bruz"
        assert address.address_postal_code == 35170
        assert address.address_country == "France"

    def test_get_address_by_customer_id(self, address_dao, customer_dao, clean_database):
        """Test getting address by customer id"""
        address = address_dao.create_address(51, "Rue Blaise Pascal", "Bruz", 35170, "France")

        customer = customer_dao.create_customer(
            first_name="Test",
            last_name="User",
            phone="0600000000",
            mail="test@email.com",
            password_hash="hash",
            salt="salt",
            address_id=address.address_id,
        )

        retrieved_address = address_dao.get_address_by_customer_id(customer.id)

        assert retrieved_address is not None
        assert retrieved_address.address_id == address.address_id

    def test_get_address_by_customer_id_not_exist(self, address_dao, clean_database):
        """test getting None when the customer id does'nt exist"""
        retrieved_address = address_dao.get_address_by_customer_id(99999)
        assert retrieved_address is None

    def test_get_all_addresses_empty(self, address_dao, clean_database):
        """Test getting all addresses (empty)"""
        addresses = address_dao.get_all_addresses()

        assert addresses is None or addresses == []

    def test_get_all_addresses_multiple(self, address_dao, clean_database):
        """Test getting all addresses"""
        address_dao.create_address(1, "Rue A", "Rennes", 35000, "France")
        address_dao.create_address(2, "Rue B", "Bruz", 35170, "France")
        address_dao.create_address(3, "Rue C", "Chartres", 35131, "France")

        addresses = address_dao.get_all_addresses()

        assert addresses is not None
        assert len(addresses) == 3

    def test_update_address_single_field(self, address_dao, clean_database):
        """Test updating single field"""
        created_address = address_dao.create_address(
            51, "Rue Blaise Pascal", "Bruz", 35170, "France"
        )

        updated_address = address_dao.update_address(
            created_address.address_id, {"address_street": "Rue Modifiée"}
        )

        assert updated_address.address_street == "Rue Modifiée"
        assert updated_address.address_city == "Bruz"
        assert updated_address.address_number == 51

    def test_update_address_all_fields(self, address_dao, clean_database):
        """Test de mise à jour de tous les champs"""
        created_address = address_dao.create_address(
            51, "Rue Blaise Pascal", "Bruz", 35170, "France"
        )

        updated_address = address_dao.update_address(
            created_address.address_id,
            {
                "address_number": 42,
                "address_street": "Avenue des Champs",
                "address_city": "Paris",
                "address_postal_code": 75001,
                "address_country": "France",
            },
        )

        assert updated_address.address_number == 42
        assert updated_address.address_street == "Avenue des Champs"
        assert updated_address.address_city == "Paris"
        assert updated_address.address_postal_code == 75001
        assert updated_address.address_country == "France"

    def test_update_address_empty_dict_raises_error(self, address_dao, clean_database):
        """Test updating with empty dict"""
        created_address = address_dao.create_address(
            51, "Rue Blaise Pascal", "Bruz", 35170, "France"
        )

        with pytest.raises(ValueError, match="At least one value should be updated"):
            address_dao.update_address(created_address.address_id, {})

    def test_update_address_invalid_field_raises_error(self, address_dao, clean_database):
        """Test updating with wrong field"""
        created_address = address_dao.create_address(
            51, "Rue Blaise Pascal", "Bruz", 35170, "France"
        )

        with pytest.raises(ValueError, match="not a parameter of Address"):
            address_dao.update_address(created_address.address_id, {"invalid_field": "value"})

    def test_delete_address(self, address_dao, clean_database):
        """Test delmete address"""
        created_address = address_dao.create_address(
            51, "Rue Blaise Pascal", "Bruz", 35170, "France"
        )

        address_id = created_address.address_id

        address_dao.delete_address_by_id(address_id)

        retrieved_address = address_dao.get_address_by_customer_id(address_id)
        assert retrieved_address is None
