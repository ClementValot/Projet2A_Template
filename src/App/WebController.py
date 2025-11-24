from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .CustomerController import get_customer_id_from_token
from .DriverController import get_driver_id_from_token
from .init_app import customer_service, driver_service, jwt_service, menu_service

templates = Jinja2Templates(directory="templates")

web_router = APIRouter(tags=["Web Interface"])


@web_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


@web_router.get("/menu", response_class=HTMLResponse)
async def menu_page(request: Request, user_id: int = Depends(get_customer_id_from_token)):
    try:
        user = customer_service.get_customer_by_id(user_id)
        orderables = menu_service.get_all_orderables()
        items = []
        bundles = []
        item_types = []

        for o in orderables:
            if o.orderable_type == "item":
                items.append(o)
                item_types.append(o.item_type)
            else:
                bundles.append(o)

        return templates.TemplateResponse(
            "customer/menu.html",
            {
                "request": request,
                "items": items,
                "bundles": bundles,
                "item_types": set(item_types),
                "user": user,
            },
        )
    except Exception as e:
        print(f"Erreur lors du chargement du menu: {e}")
        return templates.TemplateResponse(
            "customer/menu.html",
            {"request": request, "items": [], "bundles": [], "item_types": []},
        )


@web_router.get("/profile", response_class=HTMLResponse)
async def get_profile_page(
    request: Request,
):
    try:
        cookie = request.cookies.get("access_token")
        token = jwt_service.decode_jwt(cookie)
        user_id = int(token["user_id"])
        user_type = token["user_role"]

        if user_type == "customer":
            user = customer_service.get_customer_by_id(user_id)
            return templates.TemplateResponse(
                "customer/profile_customer.html",
                {"request": request, "user": user, "user_type": "customer"},
            )

        elif user_type == "driver":
            user = driver_service.get_driver_by_id(user_id)
            stats = driver_service.get_driver_stats(user_id)
            return templates.TemplateResponse(
                "driver/profile_driver.html",
                {
                    "request": request,
                    "user": user,
                    "user_type": "driver",
                    "nb_orders": stats["nb_orders"],
                    "earnings": stats["earnings"],
                },
            )

        else:
            raise HTTPException(status_code=403, detail="You're not allowed to access this page")

    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Erreur lors du chargement du profil: {e}"
        ) from e


@web_router.get("/payment/success", response_class=HTMLResponse)
async def payment_success_page(
    request: Request,
    session_id: str,
):
    cookie = request.cookies.get("access_token")
    token = jwt_service.decode_jwt(cookie.encode("utf-8"))

    user_id = int(token["user_id"])
    user = customer_service.get_customer_by_id(user_id)

    user_id = int(token["user_id"])
    user = customer_service.get_customer_by_id(user_id)
    return templates.TemplateResponse(
        "customer/success.html",
        {"request": request, "session_id": session_id, "user": user},
    )


@web_router.get("/deliveries", response_class=HTMLResponse)
async def driver_deliveries_page(
    request: Request, user_id: int = Depends(get_driver_id_from_token)
):
    driver = driver_service.get_driver_by_id(user_id)
    return templates.TemplateResponse(
        "driver/deliveries.html", {"request": request, "user": driver}
    )


@web_router.get("/delivery/{order_id}", response_class=HTMLResponse)
async def driver_active_delivery_page(
    request: Request, order_id: int, user_id: int = Depends(get_driver_id_from_token)
):
    user = driver_service.get_driver_by_id(user_id)
    return templates.TemplateResponse(
        "driver/active_delivery.html", {"request": request, "user": user, "order_id": order_id}
    )


@web_router.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse("/", status_code=302)
    response.delete_cookie(key="access_token")
    return templates.TemplateResponse("auth.html", {"request": request})
