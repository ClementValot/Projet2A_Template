from pydantic import BaseModel


class APIUser(BaseModel):
    id_user: int
    username: str
