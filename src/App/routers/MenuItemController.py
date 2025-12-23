from typing import List, Optional, Union

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status

from src.App.auth import admin_required
from src.App.init_app import admin_menu_service
from src.Model.discounted_bundle import DiscountedBundle
from src.Model.item import Item
from src.Model.one_item_bundle import OneItemBundle
from src.Model.predefined_bundle import PredefinedBundle

AnyBundle = Union[PredefinedBundle, DiscountedBundle, OneItemBundle]


menu_item_router = APIRouter(tags=["Menu Item management"], dependencies=[Depends(admin_required)])


def get_service():
    return admin_menu_service


def get_item_dao():
    return admin_menu_service.item_dao


def handle_service_error(e: Exception):
    msg = str(e).lower()
    if "not found" in msg:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if isinstance(e, ValueError):
        raise HTTPException(status_code=400, detail=str(e)) from e
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail="Internal Server Error") from e


@menu_item_router.get("/items/{id_item}")
def get_item(id_item: int, dao=Depends(get_item_dao)):
    item = dao.find_item_by_id(id_item)
    if not item:
        raise HTTPException(status_code=404, detail=f"Item {id_item} not found")
    return item


@menu_item_router.get("/items", response_model=List[Item])
def list_items(service=Depends(get_service)):
    try:
        return service.list_items()
    except Exception as e:
        handle_service_error(e)


@menu_item_router.post("/items", status_code=status.HTTP_201_CREATED)
def create_item(
    name: str,
    price: float,
    stock: int,
    availability: bool,
    item_type: str,
    service=Depends(get_service),
    desc: str = None,
):
    try:
        service.create_item(
            name=name,
            desc=desc,
            price=price,
            stock=stock,
            availability=availability,
            item_type=item_type,
        )
        return {"message": "Item created successfully"}
    except Exception as e:
        handle_service_error(e)


@menu_item_router.put("/items/{id_item}")
def update_item(
    id_item: int = Path(),
    name: Optional[str] = Query(None),
    price: Optional[float] = Query(None),
    stock: Optional[int] = Query(None),
    availability: Optional[bool] = Query(None),
    item_type: Optional[str] = Query(None),
    desc: Optional[str] = Query(None, alias="description"),
    service=Depends(get_service),
):
    try:
        service.update_item(
            id=id_item,
            name=name,
            desc=desc,
            price=price,
            stock=stock,
            availability=availability,
            item_type=item_type,
        )
        return {"message": "Item updated successfully"}
    except Exception as e:
        handle_service_error(e)


@menu_item_router.delete("/items/{id_item}", status_code=status.HTTP_200_OK)
def delete_item(id_item: int, service=Depends(get_service)):
    try:
        service.delete_item(id_item)
        return {"message": f"Item {id_item} deleted successfully"}
    except Exception as e:
        handle_service_error(e)
