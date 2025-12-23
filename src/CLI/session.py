class Session:
    def __init__(self):
        self.user = None
        self.user_id = None
        self.username = None
        self.role = None
        self.token = None

    def is_authenticated(self):
        return self.user is not None

    def logout(self):
        self.user = None
        self.user_id = None
        self.username = None
        self.role = None
        self.token = None
