from pydantic import BaseModel


class User(BaseModel):
    id: int
    username: str
    password: str
    salt: str
