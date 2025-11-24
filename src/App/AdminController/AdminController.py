from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from src.App.init_app import (
    customer_service,
    driver_service,
    menu_service,
    order_service,
)
from src.App.JWTBearer import AdminBearer

templates = Jinja2Templates(directory="templates")
admin_router = APIRouter(tags=["General"], dependencies=[Depends(AdminBearer())])


# OVERVIEW
@admin_router.get(
    "/overview", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_overview():
    """
    Get diffrent useful informations about the status of Ub'EJR

    - The number of customers registered
    - The number of drivers
    - The number of orderables
    - The number of orders that can be picked up by the drivers
    - The number of orders currently in the kitchen
    - The total earnings of Ub'EJR
    """
    try:
        customers = customer_service.get_number_customers()
        drivers = driver_service.get_number_drivers()

        benef = order_service.get_benef()
        orders_count = order_service.get_number_orders_by_state()

        nb_items = menu_service.get_number_orderables()

        return {
            "total_customers": customers,
            "total_drivers": drivers,
            "total_orderables_in_menu": nb_items,
            "total_orders_ready": orders_count["ready_to_deliver"],
            "total_orders_in_kitchen": orders_count["preparing"],
            "benefice": f"{benef} €",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching datas: {e}") from e


@admin_router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    """
    Logout of the admin page
    """
    response = RedirectResponse("/login", status_code=302)
    response.delete_cookie(key="access_token")
    return
