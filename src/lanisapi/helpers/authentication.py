"""This script has functions to log into Lanis."""
import httpx

from ..constants import LOGGER
from .request import Request


def get_session(schoolid: str,
                username: str,
                password: str,
                ) -> dict[str, any]:
    """Create new session (value: SPH-Session) at Lanis by posting to the login page.

    Note
    ----
    There are two login systems, the new one uses login.schulportal.hessen.de and the other
    one uses start.schulportal.hessen.de. This library currently supports only the new system.
    """
    url = "https://login.schulportal.hessen.de/"

    params = { "i": schoolid }

    # `user2` = The username
    # `user` = The schoolid + username
    # `password` = The password
    # Idk why we need 2 usernames.
    data = {
        "user2": username,
        "user": "{schoolid}.{username}".format(schoolid=schoolid, username=username),
        "password": password,
        }

    response = Request.post(url, data=data, params=params)

    cookies = httpx.Cookies()
    cookies.set(
        "SPH-Session",
        response.headers.get("set-cookie").split(";")[0].split("=")[1],
        ".hessen.de",
        "/",
        )

    # Link to the next page. If this attribute doesn't exist
    location = response.headers.get("location")

    data = {"cookies": cookies, "location": location}

    LOGGER.info("Authentication - Get session: Successfully created session.")

    return data

def get_authentication_url(cookies: httpx.Cookies) -> str:
    """Get the authentication url to get sid."""
    url = "https://connect.schulportal.hessen.de/"
    response = Request.get(url, cookies=cookies)

    # Link to the next (and final) page.
    authentication_url = response.headers.get("location")

    LOGGER.info("Authentication - Get url: Successfully got url.")

    return authentication_url

def get_authentication_sid(url: str,
                            cookies: httpx.Cookies,
                            schoolid: str,
                            ) -> httpx.Cookies:
    """Get sid and return the 'final' cookies."""
    response = Request.get(url, cookies=cookies)

    cookies = httpx.Cookies()

    cookies.set("i", schoolid)
    cookies.set("sid",
                response.headers
                .get("set-cookie")
                .split(";")[2]
                .split(", ")[1]
                .split("=")[1])

    LOGGER.info("Authentication - Get sid: Success.")

    return cookies
