from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.App.init_app import order_service
from src.App.JWTBearer import AdminBearer
from src.Model.APIOrder import APIOrder

admin_orders_router = APIRouter(tags=["Orders"], dependencies=[Depends(AdminBearer())])


# ORDERS
@admin_orders_router.get(
    "/orders", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_all_orders(limit: int = Query(15, description="How many orders do you wanna show", gt=0)):
    """
    Fetch the most recents orders

    Parameters
    ----------
    limit: int
        The number of orders you want to display
    """
    try:
        if limit < 0:
            raise HTTPException(
                status_code=403, detail="You should choose a positive number of orders to see."
            )
        orders = order_service.get_all_orders(limit)
        return [APIOrder.from_order(order) for order in orders]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orders: {e}") from e


@admin_orders_router.get(
    "/orders/{order_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_order_by(order_id: int = Path(description="The id of the order you want")):
    """
    Get a specific order by its id

    Parameters
    ----------
    order_id: int
        The id of the order you want
    """
    try:
        order = order_service.get_order_by_id(order_id)
        if order is None:
            raise HTTPException(status_code=404, detail=f"Order with id [{order_id}] not found")
        return APIOrder.from_order(order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e


@admin_orders_router.put(
    "/orders/{order_id}/prepared",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminBearer())],
)
def mark_order_as_prepared(order_id: int = Path(description="The id of the prepared order")):
    """
    Flag an order as prepared, this order must be paid and not already delivered

    Parameters
    ----------
    order_id: int
        The id of the order you want to mark as prepared
    """
    try:
        updated_order = order_service.mark_as_prepared(order_id)
        return APIOrder.from_order(updated_order)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
