from abc import ABC
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, PrivateAttr


class AbstractUser(BaseModel, ABC):
    """
    Abstract base class for all bundles

    Attributes:
        id_user (Optional[int]): Unique identifier for the user.
        username (str): Username for authentification.
        _hash_password (str): Hash password for authentification. (private attribute)
        _salt (str): Salt for authentification with hash password. (private attribute)
        sign_up_date (Optional[datetime]): Date of last authentification.
    """

    id_user: Optional[int] = None
    username: str
    _hash_password: str = PrivateAttr()
    _salt: str = PrivateAttr()
    sign_up_date: Optional[datetime] = None
