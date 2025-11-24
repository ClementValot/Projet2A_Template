from .User import User


class Admin(User):
    username: str
    """
    Represents an administrator in the system.
    """

    def __init__(self, **args):
        args["user_role"] = "admin"
        super().__init__(**args)
