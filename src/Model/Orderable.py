from abc import ABC, abstractmethod
from typing import Literal, Optional

from pydantic import BaseModel


class Orderable(BaseModel, ABC):
    orderable_id: int
    orderable_type: Literal["item", "bundle"]
    orderable_image_name: Optional[str] = None
    orderable_image_url: Optional[str] = None
    is_in_menu: bool = False

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def check_availability(self) -> bool:
        """
        Check that the orderable can be added to the menu

        Returns
        -------
        bool
            True if it can be added, else False
        """
        pass

    @abstractmethod
    def check_stock(self, quantity: int) -> bool:
        """
        Check that there is a sufficient stock to provide the quantity of orderables

        Parameters
        ----------
        quantity : int
            The number of orderables ordered

        Returns
        -------
        bool
            True if ther is enough stock, else False
        """
        pass

    @property
    @abstractmethod
    def price(self) -> float:
        pass
