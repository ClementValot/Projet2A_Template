from .Address import Address
from .User import User


class Customer(User):
    """
    Represents a customer in the system.

    Attributes
    ----------
        id_user (int): Unique identifier for the customer (references User).
        customer_address (Address): Customer's physical address.
        customer_phone (str): Customer's phone number.
        customer_mail (str): Customer's email address.
    """

    customer_address: Address
    customer_phone: str
    customer_mail: str

    def __init__(self, **args):
        args["user_role"] = "customer"
        super().__init__(**args)
