from abc import ABC, abstractmethod
from typing import Any, Dict


class AbstractView(ABC):
    """
    Abstract base class for CLI views.
    Provides a common interface for displaying views, prompting input,
    and printing info/error messages.
    """

    def __init__(self, session: Any, services: Dict[str, Any]) -> None:
        """
        Initialize the abstract view with a session and services dictionary.

        Args:
            session (Any): The active user session object.
            services (Dict[str, Any]): Dictionary of available services.
        """
        self.session = session
        self.services: Dict[str, Any] = services

    @abstractmethod
    def display(self) -> None:
        """
        Display the view to the user.

        This method must be implemented by subclasses.
        """
        pass

    def prompt(self, message: str) -> str:
        """
        Prompt the user for input, safely handling keyboard interrupts.

        Args:
            message (str): Message to display to the user.

        Returns:
            str: User input, or empty string if interrupted.
        """
        try:
            return input(message)
        except (KeyboardInterrupt, EOFError):
            print()
            return ""

    def print_error(self, message: str) -> None:
        """
        Print an error message to the console.

        Args:
            message (str): Error message to display.
        """
        print(f"[ERROR] {message}")

    def print_info(self, message: str) -> None:
        """
        Print an informational message to the console.

        Args:
            message (str): Information message to display.
        """
        print(f"[INFO] {message}")
