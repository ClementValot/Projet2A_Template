from dotenv import load_dotenv

from src.DAO.AddressDAO import AddressDAO
from src.DAO.AdminDAO import AdminDAO
from src.DAO.BundleDAO import BundleDAO
from src.DAO.CustomerDAO import CustomerDAO
from src.DAO.DBConnector import DBConnector
from src.DAO.DeliveryDAO import DeliveryDAO
from src.DAO.DriverDAO import DriverDAO
from src.DAO.ItemDAO import ItemDAO
from src.DAO.OrderableDAO import OrderableDAO
from src.DAO.OrderDAO import OrderDAO
from src.Service.AddressService import AddressService
from src.Service.BundleService import BundleService
from src.Service.CustomerService import CustomerService
from src.Service.DriverService import DriverService
from src.Service.GoogleMapService import GoogleMapService
from src.Service.ItemService import ItemService
from src.Service.JWTService import JwtService
from src.Service.MenuService import MenuService
from src.Service.OrderService import OrderService
from src.Service.StripeService import StripeService
from src.Service.UserService import UserService

load_dotenv()
db_connector = DBConnector()

# DAOs
address_dao = AddressDAO(db_connector)
customer_dao = CustomerDAO(db_connector, address_dao)
driver_dao = DriverDAO(db_connector)
admin_dao = AdminDAO(db_connector)
orderable_dao = OrderableDAO(db_connector)
item_dao = ItemDAO(db_connector, orderable_dao)
bundle_dao = BundleDAO(db_connector, orderable_dao, item_dao)
delivery_dao = DeliveryDAO(db_connector)

# Services
order_dao = OrderDAO(db_connector, orderable_dao, item_dao, bundle_dao)
gm_service = GoogleMapService()
user_service = UserService(customer_dao, driver_dao, admin_dao)
address_service = AddressService(address_dao, gm_service)
customer_service = CustomerService(customer_dao, address_service, user_service)
driver_service = DriverService(delivery_dao, driver_dao, order_dao, user_service)
order_service = OrderService(order_dao, orderable_dao, item_dao, bundle_dao)
item_service = ItemService(item_dao, order_dao)
bundle_service = BundleService(bundle_dao)
menu_service = MenuService(orderable_dao, item_dao, bundle_dao)


jwt_service = JwtService()
stripe_service = StripeService()
