from .User import User


class Driver(User):
    """
    Represents a driver in the system.

    Attributes
    ----------
        phone (str): Driver's phone number.
        is_delivering (bool, optional): Indicates if the driver is currently delivering.
                                        Default is False.
    """

    driver_phone: str
    driver_is_delivering: bool = False

    def __init__(self, **args):
        args["user_role"] = "driver"
        super().__init__(**args)
