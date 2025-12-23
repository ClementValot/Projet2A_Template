from typing import Dict

from src.CLI.auth_view import AuthView
from src.CLI.customer_main_view import CustomerMainView
from src.CLI.driver_main_view import DriverMainView
from src.CLI.session import Session


def _build_services() -> Dict:
    """Loads services src.init_app"""
    try:
        import importlib

        init_app = importlib.import_module("src.init_app")

        services = {
            "auth": getattr(init_app, "auth_service", None),
            "item": getattr(init_app, "item_service", None),
            "order": getattr(init_app, "order_service", None),
            "user": getattr(init_app, "admin_user_service", None),
            "jwt": getattr(init_app, "jwt_service", None),
            "address": getattr(init_app, "address_service", None),
            "driver": getattr(init_app, "driver_service", None),
            "api_maps": getattr(init_app, "api_maps_service", None),
        }

        missing = [k for k, v in services.items() if v is None]
        if missing:
            print(f"[WARN] Some services missing: {', '.join(missing)}")

        return services

    except Exception as e:
        print(f"[ERROR] Failed to import real services: {e}")
        raise


def run_cli():
    """Launch the full CLI (auth + menus)."""
    session = Session()
    services = _build_services()

    auth_view = AuthView(session, services)
    authenticated = auth_view.display()
    if not authenticated:
        print("Goodbye.")
        return

    if session.role == "customer":
        view = CustomerMainView(session, services)
        view.display()

    if session.role == "driver":
        view = DriverMainView(session, services)
        view.display()


if __name__ == "__main__":
    run_cli()
