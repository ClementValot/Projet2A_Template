import os
import time
from typing import Literal

import jwt
from jwt import ExpiredSignatureError

from src.Model.JWTResponse import JWTResponse


class JwtService:
    """
    Handler for JWT encryption and validation
    """

    def __init__(self, secret: str = "", algorithm: str = "HS256"):
        if secret == "":
            self.secret = os.environ["JWT_SECRET"]
        else:
            self.secret = secret
        self.algorithm = algorithm

    def encode_jwt(
        self, user_id: int, user_role: Literal["admin", "customer", "driver"]
    ) -> JWTResponse:
        """
        Creates a token with a 10 minutes expiry time
        """
        payload = {
            "user_id": user_id,
            "user_role": user_role,
            "expiry_timestamp": time.time() + 3600,
        }
        token = jwt.encode(payload, self.secret, algorithm=self.algorithm)

        return JWTResponse(access_token=token)

    def decode_jwt(self, token: str) -> dict:
        """
        Unciphers an authentication token
        """
        return jwt.decode(token, self.secret, algorithms=[self.algorithm])

    def validate_user_jwt(self, token: str) -> str:
        """
        Returns the id of the user authenticated by the JWT
        Throws in case of invalid or expired JWT
        """
        decoded_jwt = self.decode_jwt(token)
        if decoded_jwt["expiry_timestamp"] < time.time():
            raise ExpiredSignatureError("Expired JWT")

        return {"user_id": decoded_jwt["user_id"], "user_role": decoded_jwt["user_role"]}
