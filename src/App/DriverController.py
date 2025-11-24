from typing import Annotated, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel

from src.Model.APIDriver import APIDriver
from src.Model.APIOrder import APIOrder
from src.Model.Bundle import Bundle
from src.Model.Item import Item
from src.Model.Order import OrderState

from .init_app import customer_service, driver_service, gm_service, jwt_service, order_service
from .JWTBearer import DriverBearer

driver_router = APIRouter(
    prefix="/drivers", tags=["Drivers"], dependencies=[Depends(DriverBearer())]
)


def get_driver_id_from_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(DriverBearer())],
) -> int:
    """
    Get the driver id

    Parameters
    ----------
    credentials : Annotated[HTTPAuthorizationCredentials, Depends
        The driver's credentials

    Returns
    -------
    int
        The id of the connected user
    """
    token = credentials.credentials
    driver_id = int(jwt_service.validate_user_jwt(token)["user_id"])
    return driver_id


# PROFILE
@driver_router.get("/me", status_code=status.HTTP_200_OK, dependencies=[Depends(DriverBearer())])
def get_profile(driver_id: int = Depends(get_driver_id_from_token)) -> APIDriver:
    """
    Returns the information about the current driver

    Parameters
    ----------
    driver_id : int
        The id of the logged driver

    Returns
    -------
    APIDriver
        A Driver without sensible informations like hash

    Raises
    ------
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        driver = driver_service.get_driver_by_id(driver_id)
        return APIDriver.from_driver(driver)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching profile: {e}") from e


@driver_router.get(
    "/me/current-delivery", status_code=status.HTTP_200_OK, dependencies=[Depends(DriverBearer())]
)
def get_current_order_id(driver_id: int = Depends(get_driver_id_from_token)) -> Optional[int]:
    delivery = driver_service.get_driver_current_delivery(driver_id)
    if delivery is None:
        return None
    return delivery.delivery_order_id


class DriverUpdate(BaseModel):
    driver_first_name: str = None
    driver_last_name: str = None
    driver_phone: str = None


@driver_router.put("/me", status_code=status.HTTP_200_OK, dependencies=[Depends(DriverBearer())])
def update_profile(
    driver_update: DriverUpdate,
    driver_id: int = Depends(get_driver_id_from_token),
) -> APIDriver:
    """
    Allows the driver to update his personal informations

    Parameters
    ----------
    driver_update: DriverUpdate
        A class containing all the informations a driver can update
    driver_id : int
        The id of the current driver

    Returns
    -------
    APIDriver
        A Driver without sensible informations like hash

    Raises
    ------
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        update_data = vars(driver_update)
        if driver_update.driver_phone and customer_service.get_customer_by_phone(
            driver_update.driver_phone
        ):
            raise HTTPException(
                status_code=403,
                detail="[DriverController] Cannot update driver: "
                "A customer already have this phone number.",
            )
        updated_driver = driver_service.update_driver(driver_id, update_data)
        return APIDriver.from_driver(updated_driver)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating profile: {e}") from e


# ORDERS
@driver_router.get(
    "/orders", status_code=status.HTTP_200_OK, dependencies=[Depends(DriverBearer())]
)
def get_available_orders() -> List:
    """
    Fetch all the orders a driver can choose from

    Returns
    -------
    List
        The list of available orders

    Raises
    ------
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        orders = order_service.get_available_orders_for_drivers()
        orders_infos = []

        for order in orders:
            orderables_list = []
            address = customer_service.get_address_by_customer_id(order.order_customer_id)

            for orderable, qty in order.order_orderables.items():
                if isinstance(orderable, Item):
                    orderables_list.append(
                        {
                            "item_name": orderable.item_name,
                            "item_price": orderable.price,
                            "item_type": orderable.item_type,
                            "image_url": orderable.orderable_image_url,
                            "quantity": qty,
                            "type": "item",
                        }
                    )

                elif isinstance(orderable, Bundle):
                    orderables_list.append(
                        {
                            "bundle_name": orderable.bundle_name,
                            "bundle_price": orderable.price,
                            "image_url": orderable.orderable_image_url,
                            "quantity": qty,
                            "type": "bundle",
                        }
                    )

            formatted_order = {
                "order_id": order.order_id,
                "order_timestamp": str(order.order_created_at),
                "order_price": round(order.order_price, 2),
                "items": orderables_list,
                "address": str(address),
            }
            orders_infos.append(formatted_order)

        return orders_infos
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {e}") from e


@driver_router.get(
    "/orders/{order_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(DriverBearer())]
)
def get_order_by_id(order_id: int) -> APIOrder:
    """
    Fetch an unique order by its id

    Parameters
    ----------
    order_id : int
        The id of the targeted order

    Returns
    -------
    APIOrder
        An Order with less informations (the orderables dictionnary is lighter)

    Raises
    ------
    HTTPException
        If the order isn't available
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        order = order_service.get_order_by_id(order_id)
        if order.order_state != OrderState.PREPARED:
            raise HTTPException(
                status_code=400,
                detail=f"This order cannot isn't available, current state : {order.order_state}",
            )

        return APIOrder.from_order(order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {e}") from e


# DELIVERIES
@driver_router.put(
    "/orders/{order_id}/start",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(DriverBearer())],
)
def start_delivery(order_id: int, driver_id: int = Depends(get_driver_id_from_token)) -> None:
    """
    Allows the driver to start a delivery, first check that the order is available

    Parameters
    ----------
    order_id : int
        The order selected by the driver
    driver_id : int
        The id of the current driver

    Raises
    ------
    HTTPException
        If the order isn't available
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        order = order_service.get_order_by_id(order_id)
        if order.order_state != OrderState.PREPARED:
            raise HTTPException(
                status_code=400,
                detail=f"This order isn't available, current state : {order.order_state}",
            )
        driver_service.start_delivery(order_id, driver_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting delivery: {e}") from e


@driver_router.get(
    "/orders/{order_id}/path",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(DriverBearer())],
)
def get_path(order_id: int) -> Dict:
    """
    Get the url of the route to the delivery address

    Parameters
    ----------
    order_id : int
        The order selected by the driver

    Returns
    -------
    Dict
        A dictionnary with the url and the delivery address string

    Raises
    ------
    HTTPException
        If the order wasn't chosen by any driver
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        order = order_service.get_order_by_id(order_id)
        if order.order_state != OrderState.DELIVERING:
            raise HTTPException(
                status_code=400,
                detail=f"This order isn't in delivery, current state : {order.order_state}",
            )
        address = customer_service.get_address_by_customer_id(order.order_customer_id)
        return {"url": gm_service.get_path(str(address)), "address": str(address)}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching path: {e}") from e


@driver_router.put(
    "/orders/{order_id}/end",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(DriverBearer())],
)
def end_delivery(
    order_id: int,
    driver_id: int = Depends(get_driver_id_from_token),
) -> None:
    """
    Allows the driver to end his delivery, first check that the order was indeed beng delivered

    Parameters
    ----------
    order_id : int
        The order selected by the driver
    driver_id : int
        The id of the current driver

    Raises
    ------
    HTTPException
        If the order isn't in delivery
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        order = order_service.get_order_by_id(order_id)
        if order.order_state != OrderState.DELIVERING:
            raise HTTPException(
                status_code=400,
                detail=f"This order isn't in delivery, current state : {order.order_state}",
            )
        driver_service.end_delivery(order_id, driver_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error finishing delivery: {e}") from e


class DeleteAccountForm(BaseModel):
    identifier: str
    password: str


@driver_router.delete(
    "/delete_account",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(DriverBearer())],
)
def delete_account(delete_account: DeleteAccountForm):
    """
    Allows a driver to delete his account (forever)

    Parameters
    ----------
    delete_account : DeleteAccountForm
        A class with the driver's identifier and password as attributes

    Raises
    ------
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        driver = driver_service.login_customer(delete_account.identifier, delete_account.password)
        return customer_service.delete_customer(driver.id)

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {e}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {e}") from e
