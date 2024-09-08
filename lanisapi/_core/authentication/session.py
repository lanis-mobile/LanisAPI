import httpx

from .account import Account
from .authenticate import authenticate


class Session:
    """
    A Lanis session which can be used to access various things with the provided request client.

    :param account: An :class:`Account` instance.
    :param session_token: The session token for accessing Lanis.
    :param request: A :class:`httpx.Client` instance with cookies for accesing Lanis.
    """

    __slots__ = ("account", "token", "request")

    def __init__(self, account: Account):
        self.account = account
        self.request = httpx.Client()
        self.token = authenticate(account, self.request)
