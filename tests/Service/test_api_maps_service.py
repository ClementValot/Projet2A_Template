from unittest.mock import ANY, MagicMock, patch

import pytest
import requests

from src.Service.api_maps_service import ApiMapsService

@pytest.fixture
def mock_os_getenv_with_key(mocker):
    """
    Patches os.getenv to return a fake API key.
    """
    mocker.patch("os.getenv", return_value="FAKE_API_KEY_123")


@pytest.fixture
def mock_os_getenv_missing_key(mocker):
    """
    Patches os.getenv to simulate a missing API key.
    """
    mocker.patch("os.getenv", return_value=None)


@pytest.fixture
def mock_load_dotenv(mocker):
    """
    Patches load_dotenv to prevent reading the actual .env file.
    """
    mocker.patch("src.Service.api_maps_service.load_dotenv")


@pytest.fixture
def service_with_key(mock_load_dotenv, mock_os_getenv_with_key):
    """
    Provides an ApiMapsService instance with a mocked valid API key.
    """
    return ApiMapsService()



@pytest.fixture
def mock_directions_response_ok():
    """Simulates a successful API response (status OK) for Driveritinerary."""
    return {
        "status": "OK",
        "routes": [
            {
                "legs": [
                    {"distance": {"value": 5000}, "duration": {"value": 300}},
                    {"distance": {"value": 1000}, "duration": {"value": 60}},
                ]
            }
        ],
    }


@pytest.fixture
def mock_geocode_response_valid():
    """Simulates a successful and precise geocoding API response (VALID)."""
    return {
        "status": "OK",
        "results": [
            {
                "formatted_address": "123 Test St, 69001 Lyon, France",
                "geometry": {"location_type": "ROOFTOP"},
            }
        ],
    }


@pytest.fixture
def mock_geocode_response_ambiguous():
    """Simulates an ambiguous geocoding API response (AMBIGUOUS)."""
    return {
        "status": "OK",
        "results": [
            {
                "formatted_address": "Test City, France",
                "geometry": {"location_type": "APPROXIMATE"},
            }
        ],
    }


@pytest.fixture
def mock_geocode_response_not_found():
    """Simulates a geocoding API response where the address is not found (INVALID)."""
    return {"status": "ZERO_RESULTS", "results": []}



def test_init_success(service_with_key):
    """Tests successful initialization when the API key is found."""
    assert service_with_key.api_key == "FAKE_API_KEY_123"


def test_init_api_key_missing(mock_load_dotenv, mock_os_getenv_missing_key):
    """Tests that a ValueError is raised if the API key is missing."""
    with pytest.raises(ValueError, match="GOOGLE_MAPS_API_KEY introuvable"):
        ApiMapsService()


def test_driver_itinerary_api_key_missing(service_with_key):
    """Tests that a RuntimeError is raised if the key is lost before the call."""
    service_with_key.api_key = None
    with pytest.raises(RuntimeError, match="Google Maps API key missing"):
        service_with_key.Driveritinerary(["B"])


@patch("requests.get")
def test_driver_itinerary_success(mock_get, service_with_key: ApiMapsService, mock_directions_response_ok, capsys):
    """
    Tests successful calculation and display of an itinerary,
    including checking the generated URL.
    """
    mock_get.return_value = MagicMock(json=lambda: mock_directions_response_ok)

    waypoints = ["Avenue de la Paix, Rennes", "Rue du Test, Bruz"]
    service_with_key.Driveritinerary(waypoints)

    mock_get.assert_called_once()
    call_url = mock_get.call_args[0][0]

    assert "https://maps.googleapis.com/maps/api/directions/json" in call_url
    assert "waypoints=Avenue+de+la+Paix%2C+Rennes%7CRue+du+Test%2C+Bruz" in call_url
    assert "key=FAKE_API_KEY_123" in call_url

    captured = capsys.readouterr()
    assert "Distance totale : 6.00 km" in captured.out
    assert "Durée totale : 0h 6min 0s" in captured.out


@patch("requests.get")
def test_driver_itinerary_api_error(mock_get, service_with_key: ApiMapsService, capsys):
    """
    Tests handling an API error (e.g., status NOT_FOUND).
    """
    mock_get.return_value = MagicMock(json=lambda: {"status": "NOT_FOUND"})

    service_with_key.Driveritinerary(["Invalid Address"])

    captured = capsys.readouterr()
    assert "Erreur : NOT_FOUND" in captured.out



@patch("requests.get")
def test_validate_address_api_success_valid(mock_get, service_with_key: ApiMapsService, mock_geocode_response_valid):
    """
    Tests the validation of a precise address (ROOFTOP).
    """
    mock_get.return_value = MagicMock(json=lambda: mock_geocode_response_valid)

    result = service_with_key.validate_address_api(
        street_name="Test St", city="Lyon", postal_code=69001, street_number="123"
    )

    mock_get.assert_called_once()

    assert result["status"] == "VALID"
    assert "123 Test St, 69001 Lyon, France" in result["formatted_address"]
    assert result["components"]["postal_code"] == 69001


@patch("requests.get")
def test_validate_address_api_ambiguous(mock_get, service_with_key: ApiMapsService, mock_geocode_response_ambiguous):
    """
    Tests the case where the API finds the address but the precision is low (AMBIGUOUS).
    """
    mock_get.return_value = MagicMock(json=lambda: mock_geocode_response_ambiguous)

    result = service_with_key.validate_address_api(street_name="Vague St", city="Test City", postal_code=10000)

    assert result["status"] == "AMBIGUOUS"
    assert result["formatted_address"] == "Test City, France"
    assert result["components"]["city"] == "Test City"


@patch("requests.get")
def test_validate_address_api_not_found(mock_get, service_with_key: ApiMapsService, mock_geocode_response_not_found):
    """
    Tests the case where the API returns ZERO_RESULTS.
    """
    mock_get.return_value = MagicMock(json=lambda: mock_geocode_response_not_found)

    result = service_with_key.validate_address_api(
        street_name="Invalid Street", city="Nowhere", postal_code=1, street_number="1"
    )

    assert result["status"] == "INVALID"
    assert "Status: ZERO_RESULTS" in result["message"]


def test_validate_address_api_missing_required_fields(service_with_key: ApiMapsService):
    """
    Tests client-side validation for missing required fields.
    """
    with patch("requests.get") as mock_get:
        result1 = service_with_key.validate_address_api(street_name="Rue", city="", postal_code=35000)
        assert result1["status"] == "INVALID"
        assert "required" in result1["message"]

        mock_get.assert_not_called()


def test_validate_address_api_environment_error(service_with_key: ApiMapsService):
    """
    Tests that an EnvironmentError is raised if the API key is missing at call time.
    """
    service_with_key.api_key = None
    with pytest.raises(EnvironmentError, match="Missing Google Maps API key"):
        service_with_key.validate_address_api("St", "C", 1, "1")


@patch("requests.get")
def test_validate_address_api_google_error_status(mock_get, service_with_key: ApiMapsService):
    """
    Tests the case where Google returns an error status (e.g., REQUEST_DENIED).
    """
    mock_get.return_value = MagicMock(json=lambda: {"status": "REQUEST_DENIED"})

    result = service_with_key.validate_address_api("St", "C", 1, "1")

    assert result["status"] == "INVALID"
    assert "Status: REQUEST_DENIED" in result["message"]
