from pydantic import BaseModel

from .Driver import Driver


class APIDriver(BaseModel):
    """
    Driver representation in the API
    """

    id: int
    first_name: str
    last_name: str
    driver_phone: str
    driver_is_delivering: bool = False

    @classmethod
    def from_driver(cls, driver: Driver):
        return cls(
            id=driver.id,
            first_name=driver.first_name,
            last_name=driver.last_name,
            driver_phone=driver.driver_phone,
            driver_is_delivering=driver.driver_is_delivering,
        )
