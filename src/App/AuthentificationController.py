from typing import Dict, Literal, Optional

from fastapi import APIRouter, HTTPException, Response, status
from pydantic import BaseModel

from src.App.init_app import customer_service, jwt_service, order_service, user_service
from src.Model.JWTResponse import JWTResponse

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterForm(BaseModel):
    first_name: str
    last_name: str
    phone: str
    mail: str
    password: str
    confirm_password: str
    address_string: str


class LoginForm(BaseModel):
    identifier: Optional[str]
    password: str
    user_type: Literal["admin", "customer", "driver"]


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register(
    register_form: RegisterForm,
    response: Response,
) -> Dict:
    """
    Allows a customer to create an account. Then, create a cookie and an order.

    Parameters
    ----------
    register_form : RegisterForm
        An object with all the informations required to register a new customer
    response : Response
        HTTP response which holds the cookie

    Returns
    -------
    Dict
        A dictionnary with the user's informations and the JWT token

    Raises
    ------
    HTTPException
        If the two passwords don't match
    HTTPException
        If a ValueError is raised beforehand
    HTTPException
        Catch any other Exception that could be raised
    """
    try:
        if register_form.confirm_password != register_form.password:
            raise HTTPException(status_code=400, detail="The two password don't match.")
        customer = customer_service.create_customer(
            register_form.first_name,
            register_form.last_name,
            register_form.phone,
            register_form.mail,
            register_form.password,
            register_form.address_string,
        )

        jwt_token = jwt_service.encode_jwt(customer.id, "customer")

        response.set_cookie(
            key="access_token",
            value=jwt_token.access_token,
            httponly=True,
            max_age=3600,
            samesite="lax",
            secure=True,
        )

        order_service.create_order(customer.id)

        return {
            "user": {
                "id": customer.id,
                "first_name": customer.first_name,
                "last_name": customer.last_name,
                "phone": customer.customer_phone,
                "email": customer.customer_mail,
                "hash_pw": customer.password,
                "type": "customer",
            },
            "access_token": jwt_token.access_token,
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {e}") from e


@auth_router.post("/login", status_code=status.HTTP_200_OK)
def login(
    login_form: LoginForm,
    response: Response,
) -> JWTResponse:
    """
    Login request for users regardless of type

    Parameters
    ----------
    identifier : Optional[str]
        For customers : email address or phone number
        For drivers : phone number
        For admins : None
    password : str
        Password of the user
    user_type : Literal[admin, customer, driver]
        Type of user

    Returns
    -------
    JWTResponse
       JWT token to allow further actions without re-login

    Raises
    ------
    HTTPException
        raised if invalid user type
    HTTPException
        raised if invalid credentials
    HTTPException
        other exceptions
    """
    try:
        if login_form.user_type not in ("admin", "customer", "driver"):
            raise HTTPException(
                status_code=400, detail="Invalid user_type. Must be: customer, driver, or admin"
            )

        user = user_service.login(
            identifier=login_form.identifier.strip(),
            password=login_form.password,
            user_type=login_form.user_type,
        )

        token = jwt_service.encode_jwt(user.id, user.user_role)

        if user.user_role == "customer":
            order_service.create_order(user.id)

        response.set_cookie(
            key="access_token",
            value=token.access_token,
            httponly=True,
            max_age=3600,
            samesite="lax",
            secure=True,
        )

        return token

    except ValueError as e:
        raise HTTPException(status_code=401, detail=f"Invalid credentials: {str(e)}") from e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Login failed: {e}") from e
