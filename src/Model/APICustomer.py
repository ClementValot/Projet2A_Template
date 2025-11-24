from pydantic import BaseModel

from .Address import Address
from .Customer import Customer


class APICustomer(BaseModel):
    """
    Customer representation in the API
    """

    id: int
    first_name: str
    last_name: str
    address: Address
    customer_phone: str
    customer_mail: str

    @classmethod
    def from_customer(cls, customer: Customer):
        return cls(
            id=customer.id,
            first_name=customer.first_name,
            last_name=customer.last_name,
            address=customer.customer_address,
            customer_phone=customer.customer_phone,
            customer_mail=customer.customer_mail,
        )
