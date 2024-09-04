import httpx

from ..constants import URL
from .account import Account


def check_credentials(request: httpx.Client, account: Account) -> str:
    """
    The first step of the Lanis authentication process and checks if the credentials are right.
    Adds the school id and return value as Cookies to the request client.

    :param request: A :class:`httpx.Client` instance.
    :param account: An :class:`Account` instance.
    :return: The value of the SPH-Session cookie, if successful.
    """

    response: httpx.Response = request.post(
        URL.login,
        data={
            "user2": account.username,
            "user": f"{account.school_id}.{account.username}",
            "password": account.password,
        },
        params={
            "i": account.school_id,
        }
    )

    if response.status_code == httpx.codes.FOUND:
        request.cookies.set("i", str(account.school_id))
        request.cookies.set("SPH-Session", response.cookies.get("SPH-Session"), ".hessen.de", "/")
        return request.cookies.get("SPH-Session")


def get_login_url(request: httpx.Client) -> str:
    """
    The second step of the Lanis authentication process and returns the login value.#
    It needs the `SPH-Session` Cookie set by :func:`check_credentials`.

    :param request: A :class:`httpx.Client` instance.
    :return: A login url.
    """

    response: httpx.Response = request.head(URL.connect)

    if response.status_code == httpx.codes.FOUND:
        return response.headers.get("location")


def get_session_token(request: httpx.Client, url: str) -> str:
    """
    The final step of the Lanis authentication process and gets the session token.
    Adds the session token as a Cookie to the request client.

    :param request: A :class:`httpx.Client` instance.
    :param url: The login url gotten by :func:`get_login_url`.
    :return: A session token.
    """

    response: httpx.Response = request.head(url)

    if response.status_code == httpx.codes.OK:
        session_token = response.cookies.get("sid")
        request.cookies.set("sid", session_token)
        return session_token


def authenticate(account: Account, request=httpx.Client()) -> str:
    """
    Combines every authentication step into one function.
    Also adds Cookies to the request client.

    :param account: An :class:`Account` instance.
    :param request: A :class:`httpx.Client` instance.
    :return: A session token.
    """

    check_credentials(request, account)
    login_url = get_login_url(request)
    return get_session_token(request, login_url)
