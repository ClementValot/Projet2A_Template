from fastapi import APIRouter, HTTPException, status

from src.App.init_app import auth_service, jwt_service
from src.Model.JWTResponse import JWTResponse

auth_router = APIRouter(tags=["Authentification"])


@auth_router.post("/auth", status_code=status.HTTP_201_CREATED)
def login(username: str, password: str) -> JWTResponse:
    """
    Authenticate with username and password and obtain a token
    """
    try:
        user = auth_service.login(username=username, password=password)
    except Exception as error:
        raise HTTPException(status_code=403, detail="Invalid username and password combination") from error
        raise HTTPException(status_code=400, detail=str(error)) from error

    return jwt_service.encode_jwt(user.id_user)
