import logging
from typing import TYPE_CHECKING, Dict, List, Optional

if TYPE_CHECKING:
    from src.Model.bundle import Bundle

    from src.CLI.session import Session
    from src.Model.address import Address
    from src.Service.address_service import AddressService
    from src.Service.api_maps_service import ApiMapsService
    from src.Service.order_service import OrderService


class AddressCheckoutView:
    """
    CLI view for final checkout, address validation, and order creation.
    """

    def __init__(self, services: Dict, session: "Session", cart: List["Bundle"]) -> None:
        """
        Initialize the Address Checkout View.

        Args:
            services (Dict): Dictionary of services (expects 'address', 'order', 'api_maps').
            session (Session): Current user session.
            cart (List[Bundle]): Reference to customer's cart.
        """
        self.address_service: "AddressService" = services.get("address")
        self.api_maps_service: "ApiMapsService" = services.get("api_maps")
        self.order_service: "OrderService" = services.get("order")
        self.session = session
        self.cart: List["Bundle"] = cart

    def _get_address_input(self) -> Dict[str, Optional[str]]:
        """
        Prompt user to input delivery address components.

        Returns:
            Dict[str, Optional[str]]: Address data from user input.
        """
        print("\n📦 Enter delivery address:")
        street_number_input: str = input("Street number (if exists): ").strip()
        street_name: str = input("Street name: ").strip()
        city: str = input("City: ").strip()
        postal_code_input: str = input("Postal code: ").strip()

        return {
            "street_number_input": street_number_input,
            "street_name": street_name,
            "city": city,
            "postal_code_input": postal_code_input,
        }

    def _process_address_validation(self) -> Optional["Address"]:
        """
        Handle address input, validation via API, confirmation, and DB creation/retrieval.

        Returns:
            Optional[Address]: Final Address object if confirmed, None if cancelled.
        """
        final_address_obj: Optional["Address"] = None

        while final_address_obj is None:
            address_data: Dict[str, Optional[str]] = self._get_address_input()

            try:
                postal_code: int = int(address_data["postal_code_input"])
                street_number: Optional[str] = address_data["street_number_input"] or None

                validation_result = self.api_maps_service.validate_address_api(
                    street_name=address_data["street_name"],
                    city=address_data["city"],
                    postal_code=postal_code,
                    street_number=street_number,
                )

                status: str = validation_result.get("status")

                if status == "INVALID":
                    print(f"[ERROR] {validation_result.get('message')}. Veuillez réessayer.")
                    continue

                components: Dict[str, Optional[str]] = validation_result["components"]
                display_street_number: str = components["street_number"] or ""
                display_address: str = (
                    f"{display_street_number} {components['street_name']}, "
                    f"{components['postal_code']} {components['city']}"
                ).strip()

                if status == "AMBIGUOUS":
                    print(f"\n⚠️  Address is ambiguous (Google suggests: {validation_result.get('formatted_address')})")
                    confirm_ambiguous: str = (
                        input("   Do you want to use the address components entered? (Y/N): ").strip().lower()
                    )
                    if confirm_ambiguous != "y":
                        continue

                print(f"\n❓ Do you confirm the delivery address: **{display_address}**?")
                final_confirm: str = input("Confirm delivery address? (Y/N): ").strip().lower()
                if final_confirm != "y":
                    print("Delivery address confirmation cancelled.")
                    return None

                print("✅ Address confirmed.")

                final_address_obj = self.address_service.get_or_create_address(
                    street_name=components["street_name"],
                    city=components["city"],
                    postal_code=components["postal_code"],
                    street_number=components["street_number"],
                )

                if final_address_obj is None:
                    raise Exception("Failed to retrieve or create address in database.")

            except ValueError:
                print("[ERROR] Postal code must be a number. Please try again.")
                continue
            except Exception as e:
                logging.error(f"Address processing failed: {e}")
                print(f"[ERROR] An unexpected error occurred during address processing: {e}")
                return None

        return final_address_obj

    def validate_order(self) -> None:
        """
        Perform final checkout, including address validation, order creation,
        and clearing the cart upon success.
        """
        if not self.cart:
            print("🛒 Your cart is empty.")
            return

        total: float = sum(b.compute_price() for b in self.cart)
        print("\n=== 💳 Review Your Order ===")
        for b in self.cart:
            print(f"- {b.name}: {b.compute_price():.2f}€")
            if hasattr(b, "composition") and b.composition:
                for item in b.composition:
                    print(f"    • {item.name}")
        print(f"\n💰 Total to pay: {total:.2f}€")

        confirm: str = input("Proceed to checkout? (Y/N): ").strip().lower()
        if confirm != "y":
            print("Order cancelled.")
            return

        final_address_obj: Optional["Address"] = self._process_address_validation()
        if final_address_obj is None:
            return

        try:
            created_order = self.order_service.create_order(self.session.user_id, final_address_obj.id_address)
            for bundle in self.cart:
                self.order_service.add_bundle_to_order(created_order.id_order, bundle)

            print(f"\n🎉 Order #{created_order.id_order} confirmed!")

            delivery_address: str = (
                f"{final_address_obj.street_number or ''} {final_address_obj.street_name}, {final_address_obj.city}"
            ).strip()
            print(f"🧾 Total: {total:.2f}€ — {len(self.cart)} items delivered to {delivery_address}.")

            self.cart.clear()

        except Exception as e:
            logging.error(f"Order creation failed: {e}")
            print(f"[ERROR] Cannot confirm order: {e}")
            return
