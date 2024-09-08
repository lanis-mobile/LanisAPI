class Account:
    """
    Collection of necessary parameters to create a :class:`Session`.
    """

    __slots__ = ("school_id", "username", "password")

    def __init__(self, school_id: int, username: str, password: str):
        self.school_id = school_id
        self.username = username
        self.password = password
