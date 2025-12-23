from typing import List, Optional, Union

from fastapi import APIRouter, Depends, Path, HTTPException, Query, status

from src.App.auth import admin_required
from src.App.init_app import admin_menu_service
from src.Model.discounted_bundle import DiscountedBundle
from src.Model.one_item_bundle import OneItemBundle
from src.Model.predefined_bundle import PredefinedBundle

AnyBundle = Union[PredefinedBundle, DiscountedBundle, OneItemBundle]


menu_bundle_router = APIRouter(tags=["Menu Bundle management"], dependencies=[Depends(admin_required)])


def get_service():
    return admin_menu_service


def get_item_dao():
    return admin_menu_service.item_dao


def get_bundle_dao():
    return admin_menu_service.bundle_dao


def handle_service_error(e: Exception):
    msg = str(e).lower()
    if "not found" in msg:
        raise HTTPException(status_code=404, detail=str(e)) from e
    if isinstance(e, ValueError):
        raise HTTPException(status_code=400, detail=str(e)) from e
    print(f"Unexpected error: {e}")
    raise HTTPException(status_code=500, detail=str(e)) from e


@menu_bundle_router.get("/bundles/{id_bundle}", response_model=AnyBundle)
def get_bundle(id_bundle: int, dao=Depends(get_bundle_dao)):
    bundle = dao.find_bundle_by_id(id_bundle)
    if not bundle:
        raise HTTPException(status_code=404, detail=f"Bundle {id_bundle} not found")
    return bundle


@menu_bundle_router.get("/bundles", response_model=List[AnyBundle])
def list_bundles(service=Depends(get_service)):
    try:
        return service.list_bundles()
    except Exception as e:
        handle_service_error(e)


@menu_bundle_router.post("/bundles/predefined", status_code=status.HTTP_201_CREATED)
def create_predefined_bundle(
    name: str = Query(..., description="Create a name"),
    price: float = Query(..., description="Put a price"),
    item_ids: List[int] = Query(..., description="Choose the items of the predifined bundle"),
    desc: Optional[str] = Query(None, alias="description"),
    service=Depends(get_service),
):
    try:
        service.create_predefined_bundle(
            name=name,
            description=desc,
            price=price,
            item_ids=item_ids,
        )
        return {"message": "Predefined bundle created"}
    except Exception as e:
        handle_service_error(e)


@menu_bundle_router.post("/bundles/discounted", status_code=status.HTTP_201_CREATED)
def create_discounted_bundle(
    name: str = Query(),
    required_item_types: List[str] = Query(),
    discount: float = Query(),
    desc: Optional[str] = Query(None, alias="description"),
    service=Depends(get_service),
):
    try:
        service.create_discounted_bundle(
            name=name,
            description=desc,
            discount=discount,
            required_item_types=required_item_types,
        )
        return {"message": "Predefined bundle created"}
    except Exception as e:
        handle_service_error(e)


@menu_bundle_router.put(
    "/bundles/predefined/{id_bundle}", status_code=status.HTTP_200_OK
)
def update_predefined_bundle(
    id_bundle: int = Path(..., description="ID of the predifined bundle to update"),
    name: Optional[str] = Query(None, description="New predifined bundle name"),
    desc: Optional[str] = Query(None, alias="description", description="New description"),
    price: Optional[float] = Query(None, description="New price"),
    item_ids: Optional[List[int]] = Query(None, description="New item list"),
    service=Depends(get_service),
):
    try:
        service.update_predefined_bundle(
            id=id_bundle,
            name=name,
            description=desc,
            price=price,
            item_ids=item_ids,
        )
        return {"message": f"Predefined bundle {id_bundle} updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        handle_service_error(e)


@menu_bundle_router.put("/bundles/discounted/{id_bundle}", status_code=status.HTTP_200_OK)
def update_discounted_bundle(
    id_bundle: int = Path(..., description="ID of the discounted bundle to update"),
    name: Optional[str] = Query(None, description="New name"),
    desc: Optional[str] = Query(None),
    discount: Optional[float] = Query(None, description="New promotion (ex: 0.10)."),
    required_item_types: Optional[List[str]] = Query(None),
    service=Depends(get_service),
):
    try:
        service.update_discounted_bundle(
            id=id_bundle,
            name=name,
            description=desc,
            discount=discount,
            required_item_types=required_item_types,
        )
        return {"message": f"Discounted bundle {id_bundle} updated successfully"}
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        handle_service_error(e)


@menu_bundle_router.delete("/bundles/{id_bundle}", status_code=status.HTTP_200_OK)
def delete_bundle(id_bundle: int, service=Depends(get_service)):
    try:
        service.delete_bundle(id_bundle)
        return {"message": f"Bundle {id_bundle} deleted successfully"}
    except Exception as e:
        handle_service_error(e)
