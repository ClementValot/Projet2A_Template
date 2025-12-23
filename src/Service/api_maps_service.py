import os
import urllib
import urllib.parse

import requests
from dotenv import load_dotenv

from src.DAO.addressDAO import AddressDAO
from src.DAO.bundleDAO import BundleDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.deliveryDAO import DeliveryDAO
from src.DAO.itemDAO import ItemDAO
from src.DAO.orderDAO import OrderDAO
from src.DAO.userDAO import UserDAO

db = DBConnector()
user_dao = UserDAO(db_connector=db)
address_dao = AddressDAO(db_connector=db)
item_dao = ItemDAO(db_connector=db)
bundle_dao = BundleDAO(db_connector=db, item_dao=item_dao)
order_dao = OrderDAO(
    db_connector=db, user_dao=user_dao, address_dao=address_dao, bundle_dao=bundle_dao, item_dao=item_dao
)
delivery_dao = DeliveryDAO(db_connector=db, user_dao=user_dao, order_dao=order_dao)


class ApiMapsService:
    def __init__(self) -> None:
        env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".env")
        load_dotenv(env_path)

        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")

        if not self.api_key:
            raise ValueError(f"❌ GOOGLE_MAPS_API_KEY introuvable dans : {env_path}")

    def Driveritinerary(self, waypoints=list):
        """
        Give an itinerary that starts and finishes at ENSAI and goes through all the waypoints.
        """
        if not self.api_key:
            raise RuntimeError("Google Maps API key missing")
        origin = "51 Rue Blaise Pascal, Bruz, France"
        destination = "51 Rue Blaise Pascal, Bruz, France"

        encoded_origin = urllib.parse.quote_plus(origin)
        encoded_destination = urllib.parse.quote_plus(destination)
        encoded_waypoints = "%7C".join(urllib.parse.quote_plus(w) for w in waypoints)

        url = f"https://maps.googleapis.com/maps/api/directions/json?origin={encoded_origin}&destination={encoded_destination}&waypoints={encoded_waypoints}&key={self.api_key}"

        response = requests.get(url)
        data = response.json()
        if data["status"] == "OK":
            route = data["routes"][0]
            legs = route.get("legs", [])
            maps_url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&origin={encoded_origin}"
                f"&destination={encoded_destination}"
                f"&waypoints={encoded_waypoints}"
            )
            total_distance_m = sum(leg["distance"]["value"] for leg in legs)
            total_duration_s = sum(leg["duration"]["value"] for leg in legs)
            total_distance_km = total_distance_m / 1000
            hours, remainder = divmod(total_duration_s, 3600)
            minutes, seconds = divmod(remainder, 60)

            print(f"Distance totale : {total_distance_km:.2f} km")
            print(f"Durée totale : {hours}h {minutes}min {seconds}s")
            print("Lien Google Maps :", maps_url)
        else:
            print("Erreur :", data["status"])

    def validate_address_api(self, street_name: str, city: str, postal_code: int, street_number: str = None) -> dict:
        """
        Calls Google Maps API for validation WITHOUT saving to DB.
        Returns a dictionary with the check result.
        """
        if not street_name or not city or not postal_code:
            return {"status": "INVALID", "message": "Street name, city, and postal code are required."}

        full_address = f"{street_number or ''} {street_name}, {postal_code} {city}".strip()

        if not self.api_key:
            raise EnvironmentError("Missing Google Maps API key.")

        response = requests.get(
            "https://maps.googleapis.com/maps/api/geocode/json",
            params={"address": full_address, "key": self.api_key},
        )
        data = response.json()
        status = data.get("status")

        if status != "OK":
            return {"status": "INVALID", "message": f"Address not found by Google (Status: {status})"}

        result = data["results"][0]
        location_type = result["geometry"]["location_type"]
        formatted_address = result["formatted_address"]

        if location_type not in ["ROOFTOP", "RANGE_INTERPOLATED"]:
            return {
                "status": "AMBIGUOUS",
                "formatted_address": formatted_address,
                "components": {
                    "street_name": street_name,
                    "city": city,
                    "postal_code": postal_code,
                    "street_number": street_number,
                },
            }

        return {
            "status": "VALID",
            "formatted_address": formatted_address,
            "components": {
                "street_name": street_name,
                "city": city,
                "postal_code": postal_code,
                "street_number": street_number,
            },
        }
