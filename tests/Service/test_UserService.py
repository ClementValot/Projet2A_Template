import re

import pytest

from src.Service.PasswordService import create_salt, hash_password


class TestUserService:
    def test_login_customer_with_email_success(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test login with customer email"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        customer = customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="+33612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        logged_in_user = user_service.login("john.doe@email.com", password, "customer")

        assert logged_in_user is not None
        assert logged_in_user.id == customer.id
        assert logged_in_user.customer_mail == customer.customer_mail

    def test_login_customer_with_phone_success(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test login with customer phone"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        customer = customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="+33612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        logged_in_user = user_service.login("+33612345678", password, "customer")

        assert logged_in_user is not None
        assert logged_in_user.id == customer.id
        assert logged_in_user.customer_phone == customer.customer_phone

    def test_login_customer_wrong_password(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test login with wrong password raises error"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="+33612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        with pytest.raises(ValueError, match="Incorrect password"):
            user_service.login("john.doe@email.com", "WrongP@ssword123", "customer")

    def test_login_customer_not_found(self, user_service, clean_database):
        """Test login with non-existing customer raises error"""
        with pytest.raises(
            ValueError,
            match=re.escape("[UserService] User not found with identifier: nonexistent@email.com"),
        ):
            user_service.login("nonexistent@email.com", "V4lidP@ssword", "customer")

    def test_login_driver_success(self, user_service, driver_dao, clean_database):
        """Test login with driver phone"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        driver = driver_dao.create_driver(
            first_name="Lewis",
            last_name="Hamilton",
            phone="+33607070707",
            password_hash=hashed_password,
            salt=salt,
        )

        logged_in_user = user_service.login("+33607070707", password, "driver")

        assert logged_in_user is not None
        assert logged_in_user.id == driver.id
        assert logged_in_user.driver_phone == driver.driver_phone

    def test_login_driver_wrong_password(self, user_service, driver_dao, clean_database):
        """Test login driver with wrong password raises error"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        driver_dao.create_driver(
            first_name="Lewis",
            last_name="Hamilton",
            phone="+33756652832",
            password_hash=hashed_password,
            salt=salt,
        )

        with pytest.raises(ValueError, match="Incorrect password"):
            user_service.login("+33756652832", "WrongP@ssword123", "driver")

    def test_login_driver_not_found(self, user_service, clean_database):
        """Test login with non-existing driver raises error"""
        with pytest.raises(
            ValueError, match=re.escape("[UserService] User not found with identifier: 0999999999")
        ):
            user_service.login("0999999999", "V4lidP@ssword", "driver")

    def test_change_password_customer_success(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test changing customer password successfully"""
        salt = create_salt()
        old_password = "0ldP@ssword"
        new_password = "N3wP@ssword"
        hashed_password = hash_password(old_password, salt)

        customer = customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="+33612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        updated_customer = user_service.change_password(
            customer.id, old_password, new_password, "customer"
        )

        assert updated_customer is not None
        assert updated_customer.id == customer.id

        logged_in = user_service.login("john.doe@email.com", new_password, "customer")
        assert logged_in.id == customer.id

    def test_change_password_customer_wrong_old_password(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test changing password with wrong old password raises error"""
        salt = create_salt()
        old_password = "0ldP@ssword"
        hashed_password = hash_password(old_password, salt)

        customer = customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="0612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        with pytest.raises(ValueError, match="Incorrect password"):
            user_service.change_password(customer.id, "WrongOldP@ss", "N3wP@ssword", "customer")

    def test_change_password_customer_weak_new_password(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test changing password with weak new password raises error"""
        salt = create_salt()
        old_password = "0ldP@ssword"
        hashed_password = hash_password(old_password, salt)

        customer = customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="+33612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        with pytest.raises(ValueError):
            user_service.change_password(customer.id, old_password, "weak", "customer")

    def test_change_password_driver_success(self, user_service, driver_dao, clean_database):
        """Test changing driver password successfully"""
        salt = create_salt()
        old_password = "0ldP@ssword"
        new_password = "N3wP@ssword"
        hashed_password = hash_password(old_password, salt)

        driver = driver_dao.create_driver(
            first_name="Lewis",
            last_name="Hamilton",
            phone="+33756652832",
            password_hash=hashed_password,
            salt=salt,
        )

        updated_driver = user_service.change_password(
            driver.id, old_password, new_password, "driver"
        )

        assert updated_driver is not None
        assert updated_driver.id == driver.id

        logged_in = user_service.login("+33756652832", new_password, "driver")
        assert logged_in.id == driver.id

    def test_change_password_driver_wrong_old_password(
        self, user_service, driver_dao, clean_database
    ):
        """Test changing driver password with wrong old password raises error"""
        salt = create_salt()
        old_password = "0ldP@ssword"
        hashed_password = hash_password(old_password, salt)

        driver = driver_dao.create_driver(
            first_name="Lewis",
            last_name="Hamilton",
            phone="0707070707",
            password_hash=hashed_password,
            salt=salt,
        )

        with pytest.raises(ValueError, match="Incorrect password"):
            user_service.change_password(driver.id, "WrongOldP@ss", "N3wP@ssword", "driver")

    def test_get_user_by_type_customer(
        self, user_service, customer_dao, sample_address, clean_database
    ):
        """Test getting user by type (customer)"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        customer = customer_dao.create_customer(
            first_name="John",
            last_name="Doe",
            phone="0612345678",
            mail="john.doe@email.com",
            password_hash=hashed_password,
            salt=salt,
            address_id=sample_address.address_id,
        )

        retrieved_user = user_service._get_user_by_type(customer.id, "customer")

        assert retrieved_user is not None
        assert retrieved_user.id == customer.id
        assert retrieved_user.user_role == "customer"

    def test_get_user_by_type_driver(self, user_service, driver_dao, clean_database):
        """Test getting user by type (driver)"""
        salt = create_salt()
        password = "V4lidP@ssword"
        hashed_password = hash_password(password, salt)

        driver = driver_dao.create_driver(
            first_name="Lewis",
            last_name="Hamilton",
            phone="+33756652832",
            password_hash=hashed_password,
            salt=salt,
        )

        retrieved_user = user_service._get_user_by_type(driver.id, "driver")

        assert retrieved_user is not None
        assert retrieved_user.id == driver.id
        assert retrieved_user.user_role == "driver"

    def test_get_user_by_type_admin(self, user_service, admin_dao, clean_database, sample_admin):
        """Test getting user by type (admin)"""
        admin = admin_dao.get_admin_by_id(1)

        retrieved_user = user_service._get_user_by_type(admin.id, "admin")

        assert retrieved_user is not None
        assert retrieved_user.id == admin.id
        assert retrieved_user.user_role == "admin"
