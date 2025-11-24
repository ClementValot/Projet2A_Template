from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.App.init_app import (
    customer_service,
    driver_service,
)
from src.App.JWTBearer import AdminBearer
from src.Model.APICustomer import APICustomer
from src.Model.APIDriver import APIDriver

admin_users_router = APIRouter(tags=["Customers / Drivers"], dependencies=[Depends(AdminBearer())])


# CUSTOMERS
@admin_users_router.get(
    "/customers", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_all_customers(limit: int = Query(15, description="The number of customers you want")):
    """
    Fetch a certain number of customers

    Parameters
    ----------
    limit: int
        The number of customers you want to display
    """
    try:
        if limit < 0:
            raise HTTPException(
                status_code=403, detail="You should choose a positive number of orders to see."
            )
        customers = customer_service.get_all_customers(limit)
        return [APICustomer.from_customer(customer) for customer in customers]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_users_router.get(
    "/customers/{customer_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminBearer())],
)
def get_customer_by_id(customer_id: int = Path(description="The id of the customer you want")):
    """
    Get a specific customer of the database by his id

    Parameters
    ----------
        customer_id: int
            The id of the customer you want
    """
    try:
        customer = customer_service.get_customer_by_id(customer_id)
        if customer is None:
            raise HTTPException(
                status_code=404, detail=f"Customer with id [{customer_id}] not found"
            )
        return APICustomer.from_customer(customer)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_users_router.delete(
    "/customers/{customer_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminBearer())],
)
def delete_customer(
    customer_id: int = Path(description="The id of the customer you want to delete"),
):
    """
    Remove a customer from the database (this action cannot be undone)

    Parameters
    ----------
        customer_id: int
            The id of the customer you want to remove from the database
    """
    try:
        return customer_service.delete_customer(customer_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_users_router.put(
    "/customers/{customer_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminBearer())],
)
def update_profile(
    customer_id: int = Path(description="The od of the customer you want to update"),
    customer_first_name: Optional[str] = Query(None, description="First name of the customer"),
    customer_last_name: Optional[str] = Query(None, description="Last name of the customer"),
    customer_mail: Optional[str] = Query(None, description="Email of the customer"),
    customer_phone: Optional[str] = Query(None, description="Phone number of the customer"),
):
    """
    Update an existing user

    Parameters
    ----------
    customer_id: int
        The id of the customer you want to update

    customer_first_name: str | None
        The first name of the customer

    customer_last_name: str | None
        The last name of the customer

    customer_mail: str | None
        A valid mail address

    customer_phone: str | None
        A phone number with a valid format

    """
    try:
        update_data = locals()
        update_data.pop("customer_id")
        updated_customer = customer_service.update_customer(customer_id, update_data)
        return updated_customer

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {e}") from e


# DRIVERS
@admin_users_router.post(
    "/drivers", status_code=status.HTTP_201_CREATED, dependencies=[Depends(AdminBearer())]
)
def create_driver(
    first_name: str = Query(description="First name of the driver"),
    last_name: str = Query(description="Last name of the driver"),
    phone: str = Query(description="Phone number of the driver"),
    password: str = Query(description="Password for the driver"),
    confirm_password: str = Query(description="Confirm the password"),
):
    """
    Allow the admin to create a new driver

    Parameters
    ----------
    first_name: str
        The first name of the driver

    last_name: str
        The last name of the driver

    phone: str
        A valid phone number

    password: str
        The password of the driver

    confirm_password: str
        An identical password to confirm the creation
    """
    try:
        if confirm_password != password:
            raise HTTPException(status_code=400, detail="The two password don't match.")
        if customer_service.get_customer_by_phone(phone):
            raise HTTPException(
                status_code=403,
                detail="[AdminController] Cannot update driver: "
                "A customer already have this phone number.",
            )
        return driver_service.create_driver(first_name, last_name, phone, password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}") from e


@admin_users_router.get(
    "/drivers", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_all_drivers(limit: int = Query(15, description="The number of drivers you want")):
    """
    Fetch a certain number of drivers

    Parameters
    ----------
    limit: int
        The number of drivers you want to display
    """
    try:
        drivers = driver_service.get_all_drivers()
        return [APIDriver.from_driver(driver) for driver in drivers]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_users_router.get(
    "/drivers/{driver_id}",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminBearer())],
)
def get_driver_by_id(driver_id: int = Path(description="The id of the driver you want")):
    """
    Get a specific driver of the database by his id

    Parameters
    ----------
        driver_id: int
            The id of the driver you want
    """
    try:
        driver = driver_service.get_driver_by_id(driver_id)
        if driver is None:
            raise HTTPException(status_code=404, detail=f"Driver with id [{driver_id}] not found")
        return driver
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_users_router.delete(
    "/drivers/{driver_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminBearer())],
)
def delete_driver(driver_id: int = Path(description="The id of the driver you want to delete")):
    """
    Remove a driver from the database (this action cannot be undone)

    Parameters
    ----------
        driver_id: int
            The id of the driver you want to remove from the database
    """
    try:
        return driver_service.delete_driver(driver_id)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_users_router.put(
    "/drivers/{driver_id}",
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(AdminBearer())],
)
def update_driver(
    driver_id: int = Path(description="The id of the driver you want to update"),
    driver_first_name: Optional[str] = Query(None, description="First name of the driver"),
    driver_last_name: Optional[str] = Query(None, description="Last name of the driver"),
    driver_phone: Optional[str] = Query(None, description="Phone number of the driver"),
):
    """
    Update an existing driver

    Parameters
    ----------
    driver_id: int
        The id of the driver you want to update

    driver_first_name: str | None
        The updated first name of the driver

    driver_last_name: str | None
        The updated lest name of the driver

    driver_phone_name: str | None
        The updated phone number (in a valid format) of the driver
    """
    try:
        update_data = locals()
        update_data.pop("driver_id")
        if update_data.get("driver_phone") and customer_service.get_customer_by_phone(driver_phone):
            raise HTTPException(
                status_code=403,
                detail="[AdminController] Cannot update driver: "
                "A customer already have this phone number.",
            )
        updated_driver = driver_service.update_driver(driver_id, update_data)
        return updated_driver

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {e}") from e
