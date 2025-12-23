from typing import Any, Dict, List, Literal, Optional, Union

import pytest

from src.DAO.addressDAO import AddressDAO
from src.DAO.DBConnector import DBConnector
from src.Model.address import Address


class MockDBConnector(DBConnector):
    def __init__(self):
        self.address = [
            {
                "id_address": 1,
                "city": "Lyon",
                "postal_code": 69000,
                "street_name": "Rue de la République",
                "street_number": "1",
            },
            {
                "id_address": 2,
                "city": "Auxerre",
                "postal_code": 89000,
                "street_name": "Rue des Boussicats",
                "street_number": "3 bis",
            },
        ]
        self.next_address_id = 3

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Optional[Union[Literal["one"], Literal["all"], None]] = "one",
    ) -> Union[Dict[str, Any], List[Dict[str, Any]], bool, None]:
        q = " ".join(query.lower().split())

        if "simulate_db_error" in q:
            raise Exception("Simulated Database Error")

        if "select * from address where id_address" in q and return_type == "one":
            if isinstance(data, dict) and "id_address" in data:
                address_id = data.get("id_address")
                for address in self.address:
                    if address["id_address"] == address_id:
                        return address.copy()
            return None

        if "select * from address where city =" in q and "street_name =" in q and return_type == "one":
            if isinstance(data, dict):
                target_city = data.get("city")
                target_zip = data.get("postal_code")
                target_street = data.get("street_name")
                target_num = data.get("street_number")

                for address in self.address:
                    if (
                        address["city"] == target_city
                        and str(address["postal_code"]) == str(target_zip)
                        and address["street_name"] == target_street
                    ):
                        current_num = address.get("street_number")

                        if target_num is not None:
                            if str(current_num) == str(target_num):
                                return address.copy()
                        elif current_num is None:
                            return address.copy()
            return None

        if "select * from address" in q and return_type == "all":
            return [addr.copy() for addr in self.address]

        if "insert into address" in q and "returning" in q and return_type == "one":
            if not isinstance(data, dict):
                return False

            new_id = self.next_address_id
            self.next_address_id += 1

            created_address = {
                "id_address": new_id,
                "city": data["city"],
                "postal_code": data["postal_code"],
                "street_name": data["street_name"],
                "street_number": data["street_number"],
            }

            self.address.append(created_address)
            return created_address

        if "update address" in q and "where id_address" in q and return_type == "one":
            if not isinstance(data, dict) or "id_address" not in data:
                return False
            address_id_to_update = data.get("id_address")
            for address in self.address:
                if address["id_address"] == address_id_to_update:
                    address["city"] = data.get("city", address["city"])
                    address["postal_code"] = data.get("postal_code", address["postal_code"])
                    address["street_name"] = data.get("street_name", address["street_name"])
                    address["street_number"] = data.get("street_number", address["street_number"])
                    return {"id_address": address_id_to_update}
            return None

        if "delete from address" in q and "where id_address" in q and return_type == "one":
            if isinstance(data, dict) and "id_address" in data:
                address_id_to_delete = data.get("id_address")
                initial_len = len(self.address)
                self.address = [addr for addr in self.address if addr["id_address"] != address_id_to_delete]
                if len(self.address) < initial_len:
                    return {"id_address": address_id_to_delete}
                else:
                    return None
            return None

        return None


@pytest.fixture
def mock_db_connector():
    return MockDBConnector()


@pytest.fixture
def address_dao(mock_db_connector) -> AddressDAO:
    return AddressDAO(db_connector=mock_db_connector)


def test_find_address_by_id_existing(address_dao: AddressDAO):
    """Tests retrieving an existing address by ID."""
    found_address = address_dao.find_address_by_id(1)
    assert found_address is not None
    assert isinstance(found_address, Address)
    assert found_address.id_address == 1
    assert found_address.city == "Lyon"


def test_find_address_by_id_non_existing(address_dao: AddressDAO):
    """Tests retrieving a non-existent address by ID."""
    found_address = address_dao.find_address_by_id(999)
    assert found_address is None


def test_find_all_addresses(address_dao: AddressDAO):
    """Tests retrieving all addresses."""
    all_addresses = address_dao.find_all_addresses()
    assert isinstance(all_addresses, list)
    assert len(all_addresses) == 2
    assert all(isinstance(a, Address) for a in all_addresses)
    assert all_addresses[0].id_address == 1


def test_add_address_success(address_dao: AddressDAO, mock_db_connector):
    """Tests successfully adding a new address."""
    new_address = Address(city="Paris", postal_code=75001, street_name="Rue de Rivoli", street_number="10")
    initial_count = len(mock_db_connector.address)

    created_address = address_dao.add_address(new_address)

    assert created_address is not None
    assert created_address.id_address == mock_db_connector.next_address_id - 1
    assert created_address.city == "Paris"
    assert len(mock_db_connector.address) == initial_count + 1


def test_update_address_success(address_dao: AddressDAO, mock_db_connector):
    """Tests successfully updating an existing address."""
    address_to_update = Address(
        id_address=1, city="Lyon", postal_code=69001, street_name="Rue de la République", street_number="1"
    )

    result = address_dao.update_address(address_to_update)

    assert result is True
    updated_mock_address = next(addr for addr in mock_db_connector.address if addr["id_address"] == 1)
    assert updated_mock_address["postal_code"] == 69001


def test_update_address_non_existing(address_dao: AddressDAO):
    """Tests updating a non-existent address."""
    non_existing_address = Address(
        id_address=999, city="Nowhere", postal_code=11111, street_name="Ghost Street", street_number="0"
    )
    result = address_dao.update_address(non_existing_address)
    assert result is False


def test_delete_address_success(address_dao: AddressDAO, mock_db_connector):
    """Tests successfully deleting an address."""
    id_to_delete = 2
    initial_count = len(mock_db_connector.address)

    result = address_dao.delete_address(id_to_delete)

    assert result is True
    assert len(mock_db_connector.address) == initial_count - 1
    assert not any(addr["id_address"] == id_to_delete for addr in mock_db_connector.address)


def test_delete_address_non_existing(address_dao: AddressDAO):
    """Tests deleting a non-existent address."""
    result = address_dao.delete_address(999)
    assert result is False


def test_find_address_by_id_error_handling(address_dao: AddressDAO, mock_db_connector):
    """Tests error handling when fetching address by ID."""
    mock_db_connector.sql_query = (
        lambda q, d, rt: exec('raise Exception("Simulated DB Error")') if "SELECT" in q else None
    )
    result = address_dao.find_address_by_id(1)
    assert result is None


def test_find_all_addresses_error_handling(address_dao: AddressDAO, mock_db_connector):
    """Tests error handling when fetching all addresses."""
    mock_db_connector.sql_query = (
        lambda q, d, rt: exec('raise Exception("Simulated DB Error")') if "SELECT" in q else None
    )
    result = address_dao.find_all_addresses()
    assert result == []


def test_add_address_error_handling(address_dao: AddressDAO, mock_db_connector):
    """Tests error handling when adding an address."""
    mock_db_connector.sql_query = (
        lambda q, d, rt: exec('raise Exception("Simulated DB Error")') if "INSERT" in q else None
    )
    new_address = Address(city="Test", postal_code=12345, street_name="Error", street_number="1")
    result = address_dao.add_address(new_address)
    assert result is None


def test_update_address_error_handling(address_dao: AddressDAO, mock_db_connector):
    """Tests error handling when updating an address."""
    mock_db_connector.sql_query = (
        lambda q, d, rt: exec('raise Exception("Simulated DB Error")') if "UPDATE" in q else None
    )
    address_to_update = Address(id_address=1, city="Lyon", postal_code=69000, street_name="Rue", street_number="1")
    result = address_dao.update_address(address_to_update)
    assert result is False


def test_delete_address_error_handling(address_dao: AddressDAO, mock_db_connector):
    """Tests error handling when deleting an address."""
    mock_db_connector.sql_query = (
        lambda q, d, rt: exec('raise Exception("Simulated DB Error")') if "DELETE" in q else None
    )
    result = address_dao.delete_address(1)
    assert result is False


def test_find_address_by_components_success(address_dao: AddressDAO):
    """Tests finding an address by exact components."""
    found_address = address_dao.find_address_by_components(
        city="Lyon", postal_code=69000, street_name="Rue de la République", street_number="1"
    )

    assert found_address is not None
    assert found_address.id_address == 1
    assert found_address.city == "Lyon"


def test_find_address_by_components_no_street_number(address_dao: AddressDAO, mock_db_connector):
    """Tests finding an address with no street number."""
    mock_db_connector.address.append(
        {"id_address": 3, "city": "Bordeaux", "postal_code": 33000, "street_name": "Grand Place", "street_number": None}
    )

    found_address = address_dao.find_address_by_components(
        city="Bordeaux", postal_code=33000, street_name="Grand Place", street_number=None
    )

    assert found_address is not None
    assert found_address.id_address == 3
    assert found_address.city == "Bordeaux"
    assert found_address.street_number is None


def test_find_address_by_components_not_found(address_dao: AddressDAO):
    """Tests that finding by components returns None if no match found."""
    found_address = address_dao.find_address_by_components(
        city="Mars", postal_code=99999, street_name="Rue Inconnue", street_number="0"
    )

    assert found_address is None


def test_find_address_by_components_error_handling(address_dao: AddressDAO, mock_db_connector):
    """Tests error handling when finding address by components."""
    mock_db_connector.sql_query = (
        lambda q, d, rt: exec('raise Exception("Simulated DB Error")') if "SELECT" in q else None
    )

    result = address_dao.find_address_by_components(
        city="Lyon", postal_code=69000, street_name="Rue", street_number="1"
    )

    assert result is None
