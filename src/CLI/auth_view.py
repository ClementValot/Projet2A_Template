import getpass
import logging
from typing import TYPE_CHECKING

from src.CLI.session import Session

if TYPE_CHECKING:
    from src.Model.abstract_user import AbstractUser
    from src.Service.authentication_service import AuthenticationService


class AuthView:
    def __init__(self, session: Session, services: dict = None) -> None:
        """
        CLI view for user authentication.

        Args:
            session (Session): Session object to track the current user state.
            services (dict, optional): Dictionary of service instances. Must include 'auth'.

        Raises:
            ValueError: If 'auth' service is not provided in services.
        """
        self.session: Session = session
        if services and "auth" in services:
            self.auth_service: "AuthenticationService" = services["auth"]
        else:
            raise ValueError("Auth service must be provided in services dictionary.")

    def display(self) -> bool:
        """
        Display the authentication menu and handle user choice.

        Returns:
            bool: True if a user successfully logs in or registers, False otherwise.
        """
        while True:
            print("\n=== EJR Eats — Authentication ===")
            print("1) Login")
            print("2) Create a Customer account")
            print("q) Back")

            choice: str = input("Choice: ").strip().lower()
            if choice == "1":
                if self._login():
                    return True
            elif choice == "2":
                if self._register():
                    return True
            elif choice == "q":
                return False
            else:
                print("Invalid choice.")

    def _login(self) -> bool:
        """
        Handle user login flow.

        Returns:
            bool: True if login succeeds, False otherwise.
        """
        username: str = input("Username: ").strip()
        password: str = getpass.getpass("Password: ").strip()

        try:
            user: "AbstractUser" = self.auth_service.login(username, password)
        except ValueError as e:
            print(f"[ERROR] {e}")
            return False
        except Exception as e:
            logging.exception("Unexpected error during login:")
            print(f"[ERROR] Unexpected error: {e}")
            return False

        if user.__class__.__name__.lower() == "admin":
            print("[INFO] Admins must use the web interface.")
            return False

        self.session.user_id = user.id_user
        self.session.username = user.username
        self.session.role = user.__class__.__name__.lower()
        self.session.user = user

        print(f"[SUCCESS] Logged in as {user.username} ({self.session.role})")
        return True

    def _register(self) -> bool:
        """
        Handle customer registration flow.

        Returns:
            bool: True if registration succeeds, False otherwise.
        """
        print("\n=== Registration ===")
        username: str = input("Username: ").strip()
        print(
            "Enter a password. Your password must be at least 8 characters long "
            "and include uppercase, lowercase, digits, and special characters."
        )
        password: str = getpass.getpass("Password: ").strip()
        print("Enter your name (First name and Last name)")
        name: str = input("Name: ")
        phone_number: str = input("Phone number: ").strip()

        try:
            user: "AbstractUser" = self.auth_service.register_customer(username, password, name, phone_number)
        except ValueError as e:
            print(f"[ERROR] {e}")
            return False
        except Exception as e:
            logging.exception("Unexpected error during registration:")
            print(f"[ERROR] Registration failed: {e}")
            return False

        self.session.user_id = user.id_user
        self.session.username = user.username
        self.session.role = user.__class__.__name__.lower()
        self.session.user = user

        print(f"[SUCCESS] Customer '{user.username}' registered successfully.")
        return True
