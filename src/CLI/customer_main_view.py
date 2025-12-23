from typing import TYPE_CHECKING, Dict, List

from src.CLI.customer_address_checkout_view import AddressCheckoutView
from src.CLI.customer_browse_menu_view import BrowseMenuView
from src.CLI.session import Session

if TYPE_CHECKING:
    from src.Model.bundle import Bundle


class CustomerMainView:
    """
    Main CLI view for the customer dashboard, managing session, cart,
    and delegating to sub-views.
    """

    def __init__(self, session: Session, services: Dict = None) -> None:
        """
        Initialize the Customer Main View and associated sub-views.

        Args:
            session (Session): The active user session.
            services (Dict, optional): Dictionary of available services.
        """
        self.session: Session = session
        self.services: Dict = services or {}
        self.cart: List["Bundle"] = []

        self.menu_view: BrowseMenuView = BrowseMenuView(self.services, self.cart)
        self.checkout_view: AddressCheckoutView = AddressCheckoutView(self.services, self.session, self.cart)

    def display(self) -> None:
        """
        Display the main customer dashboard and handle top-level user selection.
        """
        while True:
            print("\n=== 🛵 EJR Eats — Order Dashboard ===")
            print("1) 🍽️   Browse Menus")
            print("2) 🛒  View Cart")
            print("3) 💳  Validate Order")
            print("B) 🔚  Logout")

            choice: str = input("Select an option: ").strip().lower()
            if choice == "1":
                self.menu_view.display()
            elif choice == "2":
                self._check_order()
            elif choice == "3":
                self.checkout_view.validate_order()
            elif choice == "b":
                print("👋 Logging out...")
                break
            else:
                print("⚠️  Invalid choice, please try again.")

    def _check_order(self) -> None:
        """
        Display current cart contents and allow the user to remove items.
        """
        if not self.cart:
            print("🛒 Your cart is empty.")
            return

        total: float = sum(b.compute_price() for b in self.cart)
        print("\n=== 🧾 Your Current Cart ===")
        for idx, b in enumerate(self.cart, start=1):
            print(f"{idx}) {b.name} — {b.compute_price():.2f}€")

        print(f"\n💰 Total: {total:.2f}€")

        choice: str = input("Enter number to remove an item, or B to go back: ").strip().lower()
        if choice.isdigit():
            try:
                idx: int = int(choice) - 1
                if 0 <= idx < len(self.cart):
                    removed: "Bundle" = self.cart.pop(idx)
                    print(f"🗑️ Removed '{removed.name}' from cart.")
                else:
                    print("⚠️ Invalid item number.")
            except ValueError:
                print("⚠️ Invalid input.")
        elif choice == "b":
            return
