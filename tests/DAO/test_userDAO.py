from datetime import date
from typing import TYPE_CHECKING, Literal, Optional, Union

import pytest

from src.DAO.userDAO import UserDAO
from src.Model.admin import Admin
from src.Model.customer import Customer
from src.Model.driver import Driver

if TYPE_CHECKING:
    from src.Model.abstract_user import AbstractUser


class MockDBConnector:
    """Mock to simulate interactions with the database."""

    def __init__(self):
        self.users = [
            {
                "id_user": 1,
                "user_type": "customer",
                "username": "janjak",
                "password": "myHashedPassword",
                "sign_up_date": date.today(),
                "customer_name": "Jean",
                "customer_phone": "0000000000",
                "driver_name": None,
                "driver_phone": None,
                "vehicle_type": None,
                "availability": None,
                "admin_name": None,
                "admin_phone": None,
                "hash_password": "random_hash",
                "salt": "random_salt",
            },
            {
                "id_user": 2,
                "user_type": "driver",
                "username": "driver_bob",
                "password": "driverHashedPassword",
                "sign_up_date": date.today(),
                "customer_name": None,
                "customer_phone": None,
                "driver_name": "Bob Driver",
                "driver_phone": "1111111111",
                "vehicle_type": "car",
                "availability": True,
                "admin_name": None,
                "admin_phone": None,
                "hash_password": "random_driver_hash",
                "salt": "random_driver_salt",
            },
            {
                "id_user": 3,
                "user_type": "admin",
                "username": "super_admin",
                "password": "adminHashedPassword",
                "sign_up_date": date.today(),
                "customer_name": None,
                "customer_phone": None,
                "driver_name": None,
                "driver_phone": None,
                "vehicle_type": None,
                "availability": None,
                "admin_name": "Chief Admin",
                "admin_phone": "9999999999",
                "hash_password": "random_admin_hash",
                "salt": "random_admin_salt",
            },
        ]
        self.next_id = 4
        self.raise_exception = False

    def sql_query(
        self,
        query: str,
        data: Optional[Union[tuple, list, dict]] = None,
        return_type: Union[Literal["one"], Literal["all"], None] = "one",
    ):
        q = " ".join(query.lower().split())

        if self.raise_exception:
            if "where u.id_user" in q and 'from "user"' in q:
                if data and data.get("id_user") == 1:
                    raise Exception("Simulated DB Error (find by id)")
            if "where u.username" in q and 'from "user"' in q:
                if data and data.get("username") == "janjak":
                    raise Exception("Simulated DB Error (find by username)")
            if 'from "user"' in q and "left join" in q and return_type == "all":
                if "where" not in q or "where u.user_type" in q:
                    raise Exception("Simulated DB Error (find all)")
            if 'update "user"' in q:
                if data and data.get("id_user") == 1:
                    raise Exception("Simulated DB Error (update user)")
            if "update driver" in q:
                if data and data.get("id_user") == 2:
                    raise Exception("Simulated Child DB Update Error")
            if q.startswith('delete from "user"') and data and data.get("id_user") == 1:
                raise Exception("Simulated DB Error (delete user)")

        if 'from "user"' in q and "where u.id_user" in q:
            id_user = data.get("id_user")
            for u in self.users:
                if u["id_user"] == id_user:
                    return u
            return None

        if 'from "user"' in q and "where u.username" in q:
            username = data.get("username")
            for u in self.users:
                if u["username"] == username:
                    return u
            return None

        if 'from "user"' in q and "left join" in q and "where" not in q:
            if return_type == "all":
                return self.users
            else:
                return self.users[0]

        if 'from "user"' in q and "left join" in q and "where u.user_type" in q:
            user_type = data.get("user_type")
            filtered_users = [u for u in self.users if u["user_type"] == user_type]
            if return_type == "all":
                return filtered_users
            else:
                return filtered_users[0] if filtered_users else None

        if q.startswith('insert into "user"'):
            new_id = self.next_id
            user_type = data.get("user_type")

            new_user = {
                "id_user": new_id,
                "user_type": user_type,
                "username": data.get("username"),
                "password": data.get("password"),
                "sign_up_date": date.today(),
                "salt": data.get("salt"),
                "hash_password": data.get("hash_password"),
                "customer_name": None,
                "customer_phone": None,
                "driver_name": None,
                "driver_phone": None,
                "vehicle_type": None,
                "availability": False,
                "admin_name": None,
                "admin_phone": None,
            }

            self.users.append(new_user)
            self.next_id += 1

            return {"id_user": new_user["id_user"]}

        if q.startswith("insert into driver"):
            id_user = data.get("id_user")
            for u in self.users:
                if u["id_user"] == id_user:
                    u["driver_name"] = data.get("name")
                    u["driver_phone"] = data.get("phone_number")
                    u["vehicle_type"] = data.get("vehicle_type")
                    u["availability"] = data.get("availability")
            return None

        if q.startswith("insert into customer"):
            id_user = data.get("id_user")
            for u in self.users:
                if u["id_user"] == id_user:
                    u["customer_name"] = data.get("name")
                    u["customer_phone"] = data.get("phone_number")
            return None

        if q.startswith("insert into admin"):
            id_user = data.get("id_user")
            for u in self.users:
                if u["id_user"] == id_user:
                    u["admin_name"] = data.get("name")
                    u["admin_phone"] = data.get("phone_number")
            return None

        if 'update "user"' in q:
            if not data:
                raise Exception("no data provided")
            user_id = data.get("id_user")
            for u in self.users:
                if u["id_user"] == user_id:
                    u["username"] = data.get("username")
                    u["hash_password"] = data.get("hash_password")
                    u["user_type"] = data.get("user_type")
                    if "salt" in data:
                        u["salt"] = data.get("salt")
            return None

        if "update customer" in q:
            if not data:
                raise Exception("no data provided")
            user_id = data.get("id_user")
            for u in self.users:
                if u["id_user"] == user_id:
                    u["customer_name"] = data.get("name")
                    u["customer_phone"] = data.get("phone_number")
            return None

        if "update driver" in q:
            if not data:
                raise Exception("no data provided")
            user_id = data.get("id_user")
            for u in self.users:
                if u["id_user"] == user_id:
                    u["driver_name"] = data.get("name")
                    u["driver_phone"] = data.get("phone_number")
                    u["vehicle_type"] = data.get("vehicle_type")
                    u["availability"] = data.get("availability")
            return None

        if "update admin" in q:
            if not data:
                raise Exception("no data provided")
            user_id = data.get("id_user")

            if user_id is not None:
                user_id = int(user_id)

            for u in self.users:
                if u["id_user"] == user_id:
                    u["admin_name"] = data.get("name")
                    u["admin_phone"] = data.get("phone_number")
            return None

        if q.startswith("delete from customer"):
            return None
        elif q.startswith("delete from driver"):
            return None
        elif q.startswith("delete from admin"):
            return None

        if q.startswith('delete from "user"'):
            id_user_to_delete = data.get("id_user")

            if id_user_to_delete is not None:
                id_user_to_delete = int(id_user_to_delete)

                self.users = [u for u in self.users if u["id_user"] != id_user_to_delete]

        return None


@pytest.fixture
def mock_db():
    """Provides a reusable instance of the MockDBConnector."""
    return MockDBConnector()


@pytest.fixture
def user_dao(mock_db):
    """Provides a UserDAO instance with the MockDBConnector."""
    return UserDAO(mock_db)


def test_find_user_by_id(user_dao: UserDAO):
    """Tests finding a user by ID and verifying its type and data."""
    user: AbstractUser = user_dao.find_user_by_id(1)
    assert user is not None
    assert user.id_user == 1
    assert user.username == "janjak"
    assert isinstance(user, Customer)


def test_find_user_by_username(user_dao: UserDAO):
    """Tests finding a user by username and verifying its type and data."""
    user: AbstractUser = user_dao.find_user_by_username("janjak")
    assert user is not None
    assert user.id_user == 1
    assert user.username == "janjak"
    assert isinstance(user, Customer)


def test_find_all(user_dao: UserDAO):
    """Tests retrieving all users."""
    users: list[AbstractUser] = user_dao.find_all()
    assert users is not None
    assert isinstance(users, list)
    assert len(users) == 3


def test_add_customer(user_dao: UserDAO, mock_db: MockDBConnector):
    """Tests adding a new Customer."""
    new_user = Customer(
        id_user=0,
        username="alice",
        sign_up_date=date.today(),
        name="Alice",
        phone_number="0123456789",
    )
    new_user._hash_password = "random_hash"
    new_user._salt = "random_salt_value"

    added_user = user_dao.add_user(new_user)
    assert added_user is not None
    assert added_user.username == "alice"
    assert added_user.id_user == 4
    assert any(u["username"] == "alice" for u in mock_db.users)
    assert isinstance(added_user, Customer)


def test_add_driver(user_dao: UserDAO, mock_db: MockDBConnector):
    """Tests adding a new Driver."""
    new_driver = Driver(
        id_user=0,
        username="trucker_mike",
        sign_up_date=date.today(),
        name="Mike",
        phone_number="1234567890",
        vehicle_type="car",
        availability=False,
    )
    new_driver._hash_password = "driver_hash"
    new_driver._salt = "driver_salt"

    added_driver = user_dao.add_user(new_driver)
    assert added_driver is not None
    assert added_driver.username == "trucker_mike"
    assert isinstance(added_driver, Driver)
    assert added_driver.vehicle_type == "car"


def test_add_admin(user_dao: UserDAO, mock_db: MockDBConnector):
    """Tests adding a new Admin."""
    new_admin = Admin(
        id_user=0,
        username="new_chief",
        sign_up_date=date.today(),
        name="New Chief",
        phone_number="1122334455",
    )
    new_admin._hash_password = "admin_hash"
    new_admin._salt = "admin_salt"

    added_admin = user_dao.add_user(new_admin)
    assert added_admin is not None
    assert added_admin.username == "new_chief"
    assert isinstance(added_admin, Admin)


def test_update_customer(user_dao: UserDAO):
    """Tests updating an existing Customer's details."""
    existing_user = user_dao.find_user_by_id(1)
    assert existing_user is not None

    updated_user = Customer(
        id_user=1,
        username="janjak_updated",
        sign_up_date=date.today(),
        name="Jean Updated",
        phone_number="0000000001",
    )
    # Inject private attributes
    updated_user._hash_password = existing_user._hash_password
    updated_user._salt = existing_user._salt

    user_dao.update_user(updated_user)

    modified_user = user_dao.find_user_by_id(1)

    assert modified_user is not None
    assert modified_user.username == "janjak_updated"
    assert modified_user.name == "Jean Updated"
    assert modified_user.phone_number == "0000000001"


def test_update_driver(user_dao: UserDAO):
    """Tests updating an existing Driver's details."""
    existing_driver = user_dao.find_user_by_id(2)
    assert isinstance(existing_driver, Driver)

    updated_driver = Driver(
        id_user=2,
        username="driver_bob_updated",
        sign_up_date=date.today(),
        name="Bob Driver Updated",
        phone_number="2222222222",
        vehicle_type="bike",
        availability=False,
    )
    updated_driver._hash_password = "driver_h"
    updated_driver._salt = "driver_s"

    user_dao.update_user(updated_driver)
    modified_driver = user_dao.find_user_by_id(2)

    assert isinstance(modified_driver, Driver)
    assert modified_driver.name == "Bob Driver Updated"
    assert modified_driver.phone_number == "2222222222"
    assert modified_driver.vehicle_type == "bike"
    assert modified_driver.availability is False


def test_update_admin(user_dao: UserDAO):
    """Tests updating an existing Admin's details."""
    existing_admin = user_dao.find_user_by_id(3)
    assert isinstance(existing_admin, Admin)

    updated_admin = Admin(
        id_user=3,
        username="super_admin_updated",
        sign_up_date=date.today(),
        name="Chief Admin Updated",
        phone_number="8888888888",
    )
    updated_admin._hash_password = "admin_h"
    updated_admin._salt = "admin_s"

    user_dao.update_user(updated_admin)
    modified_admin = user_dao.find_user_by_id(3)

    assert isinstance(modified_admin, Admin)
    assert modified_admin.name == "Chief Admin Updated"
    assert modified_admin.phone_number == "8888888888"


def test_delete_user(user_dao: UserDAO, mock_db: MockDBConnector):
    """Tests deleting a user by ID."""
    id_to_delete = 1
    existing_user = user_dao.find_user_by_id(1)
    assert existing_user is not None

    initial_count = len(mock_db.users)
    assert initial_count > 0

    delete = user_dao.delete_user(id_to_delete)
    assert delete is True

    deleted_user = user_dao.find_user_by_id(id_to_delete)
    assert deleted_user is None

    final_count = len(mock_db.users)
    assert final_count == initial_count - 1


def test_find_all_filtered_drivers(user_dao: UserDAO):
    """Tests finding all users filtered by 'driver' type."""
    drivers = user_dao.find_all(user_type="driver")

    assert len(drivers) == 1
    assert drivers[0].username == "driver_bob"
    assert isinstance(drivers[0], Driver)


def test_find_user_by_id_error(mock_db: MockDBConnector, user_dao: UserDAO):
    """Tests error handling when finding a user by ID fails in the DB."""
    mock_db.raise_exception = True
    user = user_dao.find_user_by_id(1)
    assert user is None
    mock_db.raise_exception = False


def test_find_user_by_username_error(mock_db: MockDBConnector, user_dao: UserDAO):
    """Tests error handling when finding a user by username fails in the DB."""
    mock_db.raise_exception = True
    user = user_dao.find_user_by_username("janjak")
    assert user is None
    mock_db.raise_exception = False


def test_find_all_error(mock_db: MockDBConnector, user_dao: UserDAO):
    """Tests error handling when finding all users fails in the DB."""
    mock_db.raise_exception = True
    users = user_dao.find_all()
    assert users == []
    mock_db.raise_exception = False


def test_update_user_error(mock_db: MockDBConnector, user_dao: UserDAO):
    """Tests error handling in update_user when the general 'user' table update fails."""
    mock_db.raise_exception = True
    error_user = Customer(id_user=1, username="fail_update", name="N", phone_number="0")
    error_user._hash_password = "h"
    error_user._salt = "s"

    updated_user = user_dao.update_user(error_user)
    assert updated_user is None
    mock_db.raise_exception = False


def test_delete_user_error(mock_db: MockDBConnector, user_dao: UserDAO):
    """Tests error handling in delete_user when the final 'user' table delete fails."""
    mock_db.raise_exception = True
    success = user_dao.delete_user(1)
    assert success is False
    mock_db.raise_exception = False


def test_find_user_by_id_not_found(user_dao: UserDAO):
    """Checks that find_user_by_id returns None for a non-existent ID."""
    user = user_dao.find_user_by_id(999)
    assert user is None


def test_find_user_by_username_not_found(user_dao: UserDAO):
    """Verifies that find_user_by_username returns None for a non-existent name."""
    user = user_dao.find_user_by_username("non_existent")
    assert user is None


def test_find_all_filtered_empty(user_dao: UserDAO):
    """Verifies that find_all with a filter returns an empty list if no results are found."""
    users = user_dao.find_all(user_type="manager")
    assert users == []
    assert len(users) == 0


def test_update_driver_error_on_child_query(mock_db: MockDBConnector, user_dao: UserDAO):
    """
    Tests error handling when the general 'user' update succeeds,
    but the specific 'driver' update fails (simulated).
    """
    mock_db.raise_exception = True

    updated_driver_data = Driver(
        id_user=2,
        username="bob_fail_update",
        sign_up_date=date.today(),
        name="Bob",
        phone_number="1",
        vehicle_type="car",
        availability=True,
    )
    updated_driver_data._hash_password = "h"
    updated_driver_data._salt = "s"

    updated_user = user_dao.update_user(updated_driver_data)

    assert updated_user is None

    mock_db.raise_exception = False
