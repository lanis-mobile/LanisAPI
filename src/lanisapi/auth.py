"""The gateway to use the most stuff of this library: authentication."""
from dataclasses import dataclass

import httpx

from ._constants import URL


@dataclass
class Account:
    """
    Used for authenticating with Lanis.
    If you want to get the school id via its name, use :func:`get_school_id`.
    """

    username: str
    school_id: int
    password: str


def check_credentials(request: httpx.Client, account: Account) -> str | None:
    """
    The first step of the Lanis authentication process and checks if the credentials are right.
    Adds a school id and SPH-Session cookie to the client.

    :param httpx.Client request:
    :param Account account:
    :return: If successful, returns the SPH-Session value else None.
    :rtype: str or None
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

    return None


def get_login_url(request: httpx.Client) -> str | None:
    """
    The second step of the Lanis authentication process and returns the login value.
    It needs the `SPH-Session` cookie set by :func:`check_credentials`.

    :param httpx.Client request:
    :return: If successful, returns a login URL.
    :rtype: str or None
    """

    response: httpx.Response = request.head(URL.connect)

    if response.status_code == httpx.codes.FOUND:
        return response.headers.get("location")

    return None


def get_session_token(request: httpx.Client, url: str) -> str | None:
    """
    The final step of the Lanis authentication process and gets the session token.
    Adds the session token as a cookie to the client.

    :param httpx.Client request:
    :param str url: The login url gotten by :func:`get_login_url`.
    :return: If successful, returns a session token.
    :rtype: str
    """

    response: httpx.Response = request.head(url)

    if response.status_code == httpx.codes.OK:
        session_token = response.cookies.get("sid")
        request.cookies.set("sid", session_token)
        return session_token

    return None


def authenticate(account: Account, request=httpx.Client()) -> str:
    """
    Combines every authentication step into one function.
    Also adds cookies to the request client.

    :param Account account:
    :param httpx.Client request: If not provided, one will be created.
    :return: A session token.
    :rtype: str
    """

    check_credentials(request, account)
    login_url = get_login_url(request)
    return get_session_token(request, login_url)
