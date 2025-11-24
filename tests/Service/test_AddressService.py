from unittest.mock import patch

import pytest


class TestAddressService:
    def test_get_address_by_customer_id_found(
        self, address_service, sample_customer, sample_address
    ):
        """Test: Récupération d'une adresse par customer ID existant"""
        result = address_service.get_address_by_customer_id(sample_customer.id)

        assert result.address_id == sample_address.address_id
        assert result.address_number == sample_address.address_number
        assert result.address_street == sample_address.address_street

    def test_get_address_by_customer_id_not_found(self, address_service):
        """Test: Récupération d'une adresse par customer ID inexistant"""
        with pytest.raises(ValueError, match="Cannot find Address for customer ID 999 not found"):
            address_service.get_address_by_customer_id(999)

    def test_create_address_valid(self, address_service, clean_database):
        """Test: Création d'une adresse valide"""
        address_str = "7 Contour Antoine de Saint-Exupéry, 35170 Bruz, France"

        result = address_service.create_address(address_str)

        assert result is not None
        assert result.address_number == 7
        assert result.address_street == "Contour Antoine de Saint-Exupéry"
        assert result.address_city == "Bruz"
        assert result.address_postal_code == 35170
        assert result.address_country == "France"

    def test_create_address_invalid(self, address_service):
        """Test: Création d'une adresse invalide"""
        address_str = "Invalid Address, 00000 Invalid City, France"

        with pytest.raises(ValueError):
            address_service.create_address(address_str)

    def test_update_address_valid(self, address_service, sample_address):
        """Test: Mise à jour d'une adresse valide"""
        update_data = {
            "address_number": sample_address.address_number,  # Garder le même numéro
            "address_street": "Rue de Nemours",
            "address_city": "Rennes",
            "address_postal_code": 35000,
            "address_country": sample_address.address_country,  # Garder le même pays
        }

        result = address_service.update_address(sample_address.address_id, update_data)

        assert result is not None
        assert result.address_street == "Rue de Nemours"
        assert result.address_city == "Rennes"
        # Les champs non modifiés doivent rester inchangés
        assert result.address_number == sample_address.address_number
        assert result.address_postal_code == 35000

    def test_update_address_no_changes(self, address_service, sample_address):
        """Test: Mise à jour sans changement lève une erreur"""
        update_data = {"address_street": None, "address_city": None}

        with pytest.raises(
            ValueError, match="Cannot update address: You must change at least one field"
        ):
            address_service.update_address(sample_address.address_id, update_data)

    def test_update_address_not_found(self, address_service):
        """Test: Mise à jour d'une adresse inexistante"""
        update_data = {"address_street": "New Street"}

        with pytest.raises(
            ValueError, match="AddressService] Cannot find Address for customer ID 999 not found."
        ):
            address_service.update_address(999, update_data)

    def test_update_address_invalid_new_address(self, address_service, sample_address):
        """Test: Mise à jour avec une nouvelle adresse invalide"""
        # Mock temporairement la validation pour simuler une adresse invalide
        with patch.object(address_service.gm_service, "validate_address") as mock_validate:
            mock_validate.side_effect = ValueError("Invalid address")

            update_data = {
                "address_number": sample_address.address_number,
                "address_street": "Invalid Street",
                "address_city": sample_address.address_city,
                "address_postal_code": sample_address.address_postal_code,
                "address_country": sample_address.address_country,
            }

            with pytest.raises(ValueError, match="Invalid address"):
                address_service.update_address(sample_address.address_id, update_data)

    def test_delete_address_found(self, address_service, sample_address):
        """Test: Suppression d'une adresse existante"""
        address_id = sample_address.address_id

        # Vérifier que l'adresse existe avant suppression
        address_before = address_service.get_address_by_customer_id(address_id)
        assert address_before is not None

        # Supprimer l'adresse
        address_service.delete_address(address_id)

        # Vérifier que l'adresse n'existe plus
        with pytest.raises(
            ValueError, match="AddressService] Cannot find Address for customer ID 1 not found."
        ):
            address_service.get_address_by_customer_id(address_id)

    def test_delete_address_not_found(self, address_service):
        """Test: Suppression d'une adresse inexistante"""
        with pytest.raises(
            ValueError, match="AddressService] Cannot find Address for customer ID 999 not found."
        ):
            address_service.delete_address(999)
