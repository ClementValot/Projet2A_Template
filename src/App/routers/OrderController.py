from fastapi import APIRouter, Depends, HTTPException, status

from src.App.auth import admin_required
from src.App.init_app import admin_order_service

order_router = APIRouter(prefix="/orders", tags=["Consulting orders"], dependencies=[Depends(admin_required)])


def get_admin_order_service():
    return admin_order_service


def get_order_dao():
    return admin_order_service.order_dao


@order_router.get("/{id_order}", status_code=status.HTTP_200_OK)
def find_order_by_id(id_order: int, dao=Depends(get_order_dao)):
    try:
        my_order = dao.find_order_by_id(id_order)
        return my_order
    except FileNotFoundError:
        raise HTTPException(
            status_code=404,
            detail="Order with id [{}] not found".format(id_order),
        ) from FileNotFoundError
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid request") from Exception


@order_router.get("/", status_code=status.HTTP_200_OK)
def get_pending_orders(admin_service=Depends(get_admin_order_service)):
    """
    Retrieves all orders with the status 'pending'.
    Includes item names in the response.
    """
    try:
        pending_orders = admin_service.list_waiting_orders()

        formatted = []
        for order in pending_orders:
            formatted_order = {
                    "id_order": order.id_order,
                    "status": order.status,
                    "address": {
                        "streetnumber": order.address.street_number,
                        "streetname": order.address.street_name,
                        "city": order.address.city,
                    }
                    if order.address
                    else None,
                    "Customer name": order.customer.name,
                    "Customer phone_number": order.customer.phone_number,
                    "items": [item.name for item in order.items],
                    "order_date": order.order_date,
                    "price": order.price,
                }
            formatted.append(formatted_order)

        return formatted

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred while fetching orders: {e}") from e
