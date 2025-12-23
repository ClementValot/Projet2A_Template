from typing import TYPE_CHECKING

from fastapi import APIRouter, Depends, HTTPException, status

from src.App.auth import admin_required
from src.App.init_app import admin_user_service, password_service
from src.Model.APIUser import APIUser

if TYPE_CHECKING:
    from src.Model.User import User

user_router = APIRouter(prefix="/users", tags=["Users"])


def get_admin_user_service():
    return admin_user_service


def handle_service_error(e: Exception):
    msg = str(e).lower()
    if "not found" in msg:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if isinstance(e, ValueError):
        raise HTTPException(status_code=400, detail=str(e)) from e
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail=str(e)) from e


@user_router.get("/{id_user}", status_code=status.HTTP_200_OK)
def find_user_by_id(id_user: int, service=Depends(get_admin_user_service)):
    try:
        user = service.find_user_by_id(id_user)
        return user
    except Exception as e:
        handle_service_error(e)


@user_router.post("/", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_admin_user(
    username: str, password: str, name: str, phone_number: str, service=Depends(get_admin_user_service)
) -> APIUser:
    """
    Performs validation on the username and password
    """
    try:
        password_service.check_password_strength(password=password)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        newadmin = service.create_admin_account(
            username=username, password=password, name=name, phone_number=phone_number
        )
        return newadmin
    except Exception as e:
        handle_service_error(e)


@user_router.post("/driver", status_code=status.HTTP_201_CREATED, dependencies=[Depends(admin_required)])
def create_driver_user(
    username: str,
    password: str,
    name: str,
    phone_number: str,
    vehicle_type: str,
    service=Depends(get_admin_user_service),
) -> APIUser:
    """
    Performs validation and creates a new Driver account.
    This route requires an existing Admin to be authenticated.
    """
    try:
        password_service.check_password_strength(password=password)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e)) from e

    try:
        newdriver = service.create_driver_account(
            username=username,
            password=password,
            name=name,
            phone_number=phone_number,
            vehicle_type=vehicle_type,
        )
        return newdriver
    except Exception as e:
        handle_service_error(e)


@user_router.put("/{id_user}")
def update_driver_availability(id_user: int, availability: bool, service=Depends(get_admin_user_service)):
    try:
        service.update_driver_availability(id_user, availability)
        return {"message": "Availability was successfully updated"}
    except Exception as e:
        handle_service_error(e)


@user_router.delete("/{id_user}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(id_user: int, service=Depends(get_admin_user_service)):
    try:
        service.delete_user(id_user)
        return {"message": "Driver was successfully deleted"}
    except Exception as e:
        handle_service_error(e)
