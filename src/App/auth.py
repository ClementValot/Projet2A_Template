from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials

from src.Model.abstract_user import AbstractUser
from src.Model.admin import Admin

from .init_app import admin_user_service, jwt_service
from .JWTBearer import JWTBearer


def get_user_dao_from_service():
    return admin_user_service.user_dao


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(JWTBearer())) -> AbstractUser:
    """
    A dependency that decodes the token and returns the full user object
    (Admin, Customer, or Driver) from the database.
    """
    try:
        token = credentials.credentials
        user_id = int(jwt_service.validate_user_jwt(token))

        user = admin_user_service.user_dao.find_user_by_id(user_id)

        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from e


def admin_required(current_user: AbstractUser = Depends(get_current_user)) -> Admin:
    """
    This dependency verifies that the authenticated user is indeed an administrator.
    If not, it gives a 403 error.
    """
    if not isinstance(current_user, Admin):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden: Admin rights required")
    return current_user
