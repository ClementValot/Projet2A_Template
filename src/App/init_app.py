from dotenv import load_dotenv

from src.DAO.DBConnector import DBConnector
from src.Service.address_service import AddressService
from src.Service.admin_menu_service import AdminMenuService
from src.Service.admin_order_service import AdminOrderService
from src.Service.admin_user_service import AdminUserService
from src.Service.authentication_service import AuthenticationService
from src.Service.driver_service import DriverService
from src.Service.JWTService import JwtService
from src.Service.order_service import OrderService
from src.Service.password_service import PasswordService

load_dotenv()

db_connector = DBConnector()

password_service = PasswordService()
jwt_service = JwtService()

auth_service = AuthenticationService(db_connector=db_connector, password_service=password_service)
admin_user_service = AdminUserService(db_connector=db_connector, password_service=password_service)
driver_service = DriverService(db_connector=db_connector)
address_service = AddressService(db_connector=db_connector)
order_service = OrderService(db_connector=db_connector)

admin_order_service = AdminOrderService(db_connector=db_connector)
admin_menu_service = AdminMenuService(db_connector=db_connector)

services = {
    "db_connector": db_connector,
    "password": password_service,
    "jwt": jwt_service,
    "auth": auth_service,
    "admin_user": admin_user_service,
    "driver": driver_service,
    "address": address_service,
    "order": order_service,
    "admin_order": admin_order_service,
    "admin_menu": admin_menu_service,
}
