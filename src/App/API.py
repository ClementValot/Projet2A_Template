import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.utils.log_init import initialiser_logs

from .AdminController.AdminController import admin_router
from .AdminController.AdminOrderablesController import admin_orderables_router
from .AdminController.AdminOrdersController import admin_orders_router
from .AdminController.AdminUsersController import admin_users_router
from .AuthentificationController import auth_router
from .CustomerController import customer_router
from .DriverController import driver_router
from .WebController import web_router


def run_app():
    app = FastAPI(
        title="Ub'EJR Eats",
        description="Main app",
        docs_url=None,
        redoc_url=None,
    )

    initialiser_logs("Projet Ub'EJR Eats")
    app.mount("/static", StaticFiles(directory="static"), name="static")

    admin_app = FastAPI(
        title="Admin API of Ub'EJR Eats",
        description="Admin panel",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    admin_app.include_router(admin_router, prefix="")
    admin_app.include_router(admin_orderables_router, prefix="")
    admin_app.include_router(admin_users_router, prefix="")
    admin_app.include_router(admin_orders_router, prefix="")
    app.mount("/admin", admin_app)

    app.include_router(web_router)
    app.include_router(auth_router)
    app.include_router(customer_router)
    app.include_router(driver_router)

    @app.get("/", include_in_schema=False)
    async def redirect_to_login():
        return RedirectResponse(url="/login")

    uvicorn.run(app, port=8000, host="0.0.0.0")
