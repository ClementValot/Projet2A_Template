from datetime import datetime
from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, status

from src.App.init_app import (
    bundle_service,
    item_service,
    menu_service,
)
from src.App.JWTBearer import AdminBearer
from src.Model.APIBundle import APIBundle
from src.Model.APIItem import APIItem
from src.Model.Item import Item

admin_orderables_router = APIRouter(
    tags=["Menu / Orderables"], dependencies=[Depends(AdminBearer())]
)


# MENU
@admin_orderables_router.get(
    "/orderables", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_all_orderables(
    in_menu: bool = Query(
        False, description="Do you only want the orderables available for customers ?"
    ),
):
    """
    Fetch all the orderables that are in the menu if "in_menu" is True,
    else fetch all the orderables

    Parameters
    ----------
    in_menu: bool
       If True only returns the orderables in the menu, else returns all the orderables,
       by default False
    """
    try:
        menu = menu_service.get_all_orderables(in_menu=in_menu)
        api_menu = []
        for orderable in menu:
            if isinstance(orderable, Item):
                api_menu.append(APIItem.from_item(orderable))
            else:
                api_menu.append(APIBundle.from_item(orderable))

        return menu

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orderables: {e}") from e


@admin_orderables_router.post(
    "/orderables/add",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminBearer())],
)
def add_orderable_to_menu(
    orderable_id: int = Query(None, description="The id of the orderable to add"),
):
    """
    Add an item on the menu if it's available :
     - For items, it means that its stock is greater than 0
     - For a bundle, it means that all of the items it's composed with are available,
       and that the dateare valid
     - For both, it has to be off the menu

    Parameters
    ----------
        orderable_id: int
            The id of the orderable you want to add to the menu
    """
    try:
        menu_service.add_orderable_to_menu(orderable_id)
        return f"The item with Orderable ID {orderable_id} has been added to the menu."
    except ValueError as e:
        raise HTTPException(
            status_code=400, detail=f"[AdminController] Cannot add orderable to menu : {str(e)}"
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orderables: {str(e)}") from e


@admin_orderables_router.delete(
    "/orderables/remove",
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(AdminBearer())],
)
def remove_orderable_from_menu(
    orderable_id: int = Query(None, description="The id of the orderable to remove"),
):
    """
    Add an item on the menu if it's not already in the menu

    Parameters
    ----------
        orderable_id: int
            The id of the orderable you want to remove from the menu
    """
    try:
        menu_service.remove_orderable_from_menu(orderable_id)
        return f"The item with Orderable ID {orderable_id} has been removed from the menu."
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"[AdminController] Cannot remove orderable from menu : {str(e)}",
        ) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching orderables: {e}") from e


# ITEMS
@admin_orderables_router.get(
    "/items/{item_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_item_by_id(item_id: int = Path(description="The id of the item you want")):
    """
    Fetch an item from the database

    Parameters
    ----------
        item_id: int
            The id of the item you want
    """
    try:
        item = item_service.get_item_by_id(item_id)
        if item is None:
            raise HTTPException(status_code=404, detail=f"Item with id [{item_id}] not found")
        return APIItem.from_item(item)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_orderables_router.post(
    "/items", status_code=status.HTTP_201_CREATED, dependencies=[Depends(AdminBearer())]
)
async def create_item(
    item_name: str = Query(description="The name of the item"),
    item_price: float = Query(description="The price of the item", gt=0),
    item_type: Literal["Starter", "Main course", "Dessert", "Side dish", "Drink"] = Query(
        description="The type of the item"
    ),
    item_description: str = Query(description="A description of the item"),
    item_stock: int = Query(description="The number of units you have", ge=0),
    item_image: Optional[str] = Query(None, description="An url to linkin to an image of the item"),
):
    """
    Add an item to the database

    Parameters
    ----------
        item_name: str
            A name for the item

        item_price: float
            The price of the item (must be postitive)

        item_type: str
            An item can be a starter, main course, dessert, side dish or a drink

        item_description: str
            A little description of the item

        item_stock: int
            How many units of the item do you have (equal or greater than zero)

        item_image: str | None
            An optional link to the item's image

    """
    try:
        item = item_service.create_item(
            item_name, item_price, item_type, item_description, item_stock, item_image
        )
        return item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_orderables_router.put(
    "/items/{item_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
async def update_item(
    item_id: int = Path(description="The id of the item you want to update"),
    item_name: str = Query(None, description="The name of the item"),
    item_price: float = Query(None, description="The price of the item", gt=0),
    item_type: Literal["Starter", "Main course", "Dessert", "Side dish", "Drink"] = Query(
        None, description="The type of the item"
    ),
    item_description: str = Query(None, description="A description of the item"),
    item_stock: int = Query(None, description="The number of units you have", ge=0),
    item_image: Optional[str] = Query(None, description="An url to linkin to an image of the item"),
):
    """
    Update a given item

    Parameters
    ----------
        item_id: int
            The id of the item you want to update

        item_name: int | None
            A name for the item

        item_price: float | None
            The price of the item (must be postitive)

        item_type: str | None
            An item can be a starter, main course, dessert, side dish or a drink

        item_description: str | None
            A little description of the item

        item_stock: int | None
            How many units of the item do you have (equal or greater than zero)

        item_image: str | None
            An optional link to the item's image
    """
    try:
        update = locals()
        update.pop("item_id")
        updated_item = item_service.update_item(item_id, update)
        return updated_item
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_orderables_router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminBearer())],
)
def delete_item(item_id: int = Path(description="The id of the item you want to delete")):
    """
    Remove an item from the database (this action cannot be undone)

    Parameters
    ----------
        item_id: int
            The id of the item you want to remove from the database
    """
    try:
        item_service.delete_item(item_id)
        return
    except Exception as e:
        if "foreign key constraint" in str(e):
            raise HTTPException(
                status_code=403, detail=f"Forbidden - cannot delete item in bundles: {e}"
            ) from e
        else:
            raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


# BUNDLES
@admin_orderables_router.get(
    "/bundles/{bundle_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
def get_bundle_by_id(bundle_id: int = Path(description="The id of the bundle you want")):
    """
    Fetch a bundle from the database

    Parameters
    ----------
        bundle_id: int
            The id of the bundle you want
    """
    try:
        bundle = bundle_service.get_bundle_by_id(bundle_id)
        if bundle is None:
            raise HTTPException(status_code=404, detail=f"Bundle with id [{bundle_id}] not found")
        return APIBundle.from_bundle(bundle)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


query_item_id = Query(None, description="The different id of the items you want to add")
query_item_quantities = Query(None, description="Quantités correspondantes")


@admin_orderables_router.post(
    "/bundles", status_code=status.HTTP_201_CREATED, dependencies=[Depends(AdminBearer())]
)
async def create_bundle(
    bundle_name: str = Query(description="The name of the bundle"),
    bundle_reduction: int = Query(
        description="The reduction percentage of the bundle", ge=0, le=100
    ),
    bundle_description: str = Query(description="A description of the bundle"),
    bundle_availability_start_date: str = Query(
        description="The starting date in format dd-mm-YYYY"
    ),
    bundle_availability_end_date: str = Query(description="The ending date in format dd-mm-YYYY"),
    item_ids: List[int] = query_item_id,
    item_quantities: List[int] = query_item_quantities,
    bundle_image: Optional[str] = Query(None, description="An url linking to the bundle image"),
):
    """
    Add a bundle to the database

    Parameters
    ----------
        bundle_name: str
            A name for the item

        bundle_reduction: int
            The reduction of the bundle,
            the new price will be calculated with :
               (sum item prices) * (1-bundle_reduction)/100

        bundle_description: str
            A short description of the bundle

        bundle_availability_start_date: str
            The date at which the bundle becomes available (must be later than today)

        bundle_availability_end_date: str
            The date at which the bundle's availability ends

        item_ids: List[int]
            A list containing the id of the items in the bundle

        item_quantities: List[int]
            A list containing the quantity of each item

        bundle_image: str | None
            An optional link to the item's image
    """
    try:
        if len(set(item_ids)) != len(item_ids):
            raise ValueError("An item can only appear once in a bundle")

        if len(item_ids) != len(item_quantities):
            raise ValueError("The number of item and quantities does not match.")

        if any([item_quantity <= 0 for item_quantity in item_quantities]):
            raise ValueError("All items in the bundle must be in positive quantity.")
        Items = {}
        for item_id, nb in zip(item_ids, item_quantities, strict=False):
            item = item_service.get_item_by_id(int(item_id))
            if not item:
                raise ValueError(f"Item with id {item_id} not found")
            Items[item] = nb

        bundle = bundle_service.create_bundle(
            bundle_name,
            bundle_reduction,
            bundle_description,
            datetime.strptime(bundle_availability_start_date, "%d/%m/%Y"),
            datetime.strptime(bundle_availability_end_date, "%d/%m/%Y"),
            Items,
            bundle_image,
        )
        return bundle
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_orderables_router.put(
    "/bundles/{bundle_id}", status_code=status.HTTP_200_OK, dependencies=[Depends(AdminBearer())]
)
async def update_bundle(
    bundle_id: int = Path(description="The id of the bundle you want to update"),
    bundle_name: Optional[str] = Query(description="The name of the bundle"),
    bundle_reduction: Optional[int] = Query(
        None, description="The reduction percentage of the bundle", ge=0, le=100
    ),
    bundle_description: Optional[str] = Query(None, description="A description of the bundle"),
    bundle_availability_start_date: Optional[str] = Query(
        None, description="The starting date in format dd-mm-YYYY"
    ),
    bundle_availability_end_date: Optional[str] = Query(
        description="The ending date in format dd-mm-YYYY"
    ),
    item_ids: Optional[List[int]] = query_item_id,
    item_quantities: Optional[List[int]] = query_item_quantities,
    bundle_image: Optional[str] = Query(None, description="An url linking to the bundle image"),
):
    """
    Parameters
    ----------
        bundle_id: int
            The id of the bundle you want to update

        bundle_name: str | None
            A name for the item

        bundle_reduction: int | None
            The reduction of the bundle,
            the new price will be calculated with :
               (sum item prices) * (1-bundle_reduction)/100

        bundle_description: str | None
            A short description of the bundle

        bundle_availability_start_date: str | None
            The date at which the bundle becomes available (must be later than today)

        bundle_availability_end_date: str | None
            The date at which the bundle's availability ends

        item_ids: List[int] | None
            A list containing the id of the items in the bundle

        item_quantities: List[int] | None
            A list containing the quantity of each item

        bundle_image: str | None
            An optional link to the item's image
    """
    try:
        update = locals()
        update.pop("item_ids")
        update.pop("item_quantities")
        update.pop("bundle_id")

        if item_ids and item_quantities:
            if len(item_ids) != len(item_quantities):
                raise ValueError("The number of item and quantities does not match.")
            Items = {}
            for item_id, nb in zip(item_ids, item_quantities, strict=False):
                item = item_service.get_item_by_id(int(item_id))
                if not item:
                    raise ValueError(f"Item with id {item_id} not found")
                Items[item] = nb
            update["bundle_items"] = Items

        updated_bundle = bundle_service.update_bundle(bundle_id, update)
        return updated_bundle
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_orderables_router.delete(
    "/bundles/{bundle_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(AdminBearer())],
)
def delete_bundle(bundle_id: int = Path(description="The id of the bundle you want to remove")):
    """
    Remove a bundle from the database (this action cannot be undone)

    Parameters
    ----------
        bundle_id: int
            The id of the bundle you want to remove from the database
    """
    try:
        bundle_service.delete_bundle(bundle_id)
        return
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid request: {e}") from e


@admin_orderables_router.get(
    "/orderables/{orderable_id}/image", status_code=status.HTTP_200_OK, response_class=Response
)
def get_orderable_image(
    orderable_id: int = Path(description="The id of the orderable whose image you want"),
):
    """
    Fetch the image of the orderable of your choice

    Parameters
    ----------
        orderable_id: int
            The id of the orderable whose image you want
    """
    try:
        image_data = menu_service.get_orderable_image(orderable_id)
        if image_data is None:
            raise HTTPException(status_code=404, detail="Image not found")

        return {"url": image_data, "message": "Copy the URL to view the image"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {e}") from e
