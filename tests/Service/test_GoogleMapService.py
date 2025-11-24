from unittest.mock import Mock, patch

import pytest


class TestGoogleMapService:
    def test_validate_address_ok(self, google_map_service):
        """Test: Adresse valide dans la zone de livraison"""
        address = "51 Rue Blaise Pascal, 35170 Bruz, France"

        result = google_map_service.validate_address(address)

        assert result is True

    def test_validate_address_unknown(self, google_map_service):
        """Test: Adresse inexistante lève une erreur"""
        address = "Whisky vert : jugez cinq fox d'aplomb"

        with pytest.raises(ValueError, match="Invalid address"):
            google_map_service.validate_address(address)

    def test_validate_address_missing_fields(self, google_map_service):
        """Test: Adresse avec des champs manquants lève une erreur"""
        # Mock pour simuler une réponse avec des champs manquants
        with patch.object(google_map_service, "_GoogleMapService__gmaps") as mock_gmaps:
            # Simuler une réponse avec des composants incomplets (pas de 'route')
            mock_response = [
                {
                    "address_components": [
                        {"types": ["street_number"], "long_name": "51"},
                        {"types": ["locality"], "long_name": "Bruz"},
                        {"types": ["postal_code"], "long_name": "35170"},
                        {"types": ["country"], "long_name": "France"},
                    ],
                    "geometry": {
                        "location": {
                            "lat": google_map_service.coord_ensai["lat"],
                            "lng": google_map_service.coord_ensai["lng"],
                        }
                    },
                }
            ]
            mock_gmaps.geocode.return_value = mock_response

            with pytest.raises(ValueError, match="Address not found"):
                google_map_service.validate_address("Adresse incomplète")

    def test_validate_address_too_far(self, google_map_service):
        """Test: Adresse trop éloignée lève une erreur"""
        address = "44 Rue Pierre Maître, 51100 Reims, France"

        with pytest.raises(ValueError, match="too far away"):
            google_map_service.validate_address(address)

    def test_extract_components_complete_address(self, google_map_service):
        """Test: Extraction des composants d'une adresse complète"""
        address = "51 Rue Blaise Pascal, 35170 Bruz, France"

        components = google_map_service.extract_components(address)

        assert components["address_number"] == 51
        assert components["address_street"] == "Rue Blaise Pascal"
        assert components["address_city"] == "Bruz"
        assert components["address_postal_code"] == 35170
        assert components["address_country"] == "France"

    def test_get_path_to_rennes(self, google_map_service):
        """Test: Récupération d'un itinéraire vers Rennes"""
        destination = "Place de la Mairie, 35000 Rennes, France"

        result = google_map_service.get_path(destination)

        assert result is not None

    def test_get_path_to_invalid_destination(self, google_map_service):
        """Test: Destination invalide lève une exception"""
        destination = "Whisky vert : jugez cinq fox d'aplomb"

        with pytest.raises(Exception, match="Error while computing path"):
            google_map_service.get_path(destination)

    def test_initialization(self):
        """Test: Initialisation du service avec les bonnes coordonnées"""
        with patch.dict("os.environ", {"GOOGLE_MAPS_API_KEY": "test_key"}):
            with patch("googlemaps.Client") as mock_client:
                # Mock de la réponse geocode pour ENSAI
                mock_instance = Mock()
                mock_instance.geocode.return_value = [
                    {"geometry": {"location": {"lat": 48.0, "lng": -1.5}}}
                ]
                mock_client.return_value = mock_instance

                from src.Service.GoogleMapService import GoogleMapService

                service = GoogleMapService()

                # Vérifier que les coordonnées sont bien initialisées
                assert service.coord_ensai == {"lat": 48.0, "lng": -1.5}
                assert service.ensai_address == "51 Rue Blaise Pascal, 35170 Bruz, France"
                assert service.coord_rennes == (48.137922, -1.632842)
                # Vérifier que le rayon est calculé
                assert service.radius > 0

    def test_get_path_no_route_found(self, google_map_service):
        """Test: Aucun itinéraire trouvé lève une erreur"""
        destination = "51 Rue Blaise Pascal, 35170 Bruz, France"

        with patch.object(google_map_service, "_GoogleMapService__gmaps") as mock_gmaps:
            # Simuler une réponse vide (aucun itinéraire trouvé)
            mock_gmaps.directions.return_value = []

            with pytest.raises(Exception, match="Error while computing path: No route found"):
                google_map_service.get_path(destination)
