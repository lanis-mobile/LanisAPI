"""This script has functions to log into Lanis."""
import logging

import httpx


def get_session(schoolid: str,
                username: str,
                password: str,
                parser: httpx.Client,
                ad_header: httpx.Headers,
                logger: logging.Logger
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

    response = parser.post(url, headers=ad_header, data=data, params=params)

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

    logger.info("Authentication - Get session: Successfully created session.")

    return data

def get_authentication_url(
    cookies: httpx.Cookies,
    parser: httpx.Client,
    ad_header: httpx.Headers,
    logger: logging.Logger
    ) -> str:
    """Get the authentication url to get sid."""
    url = "https://connect.schulportal.hessen.de/"
    response = parser.get(url, cookies=cookies, headers=ad_header)

    # Link to the next (and final) page.
    authentication_url = response.headers.get("location")

    logger.info("Authentication - Get url: Successfully got url.")

    return authentication_url

def get_authentication_sid(url: str,
                            cookies: httpx.Cookies,
                            parser: httpx.Client,
                            ad_header: httpx.Headers,
                            logger: logging.Logger,
                            schoolid: str,
                            ) -> httpx.Cookies:
    """Get sid and return the 'final' cookies."""
    response = parser.get(url, cookies=cookies, headers=ad_header)

    cookies = httpx.Cookies()

    cookies.set("i", schoolid)
    cookies.set("sid",
                response.headers
                .get("set-cookie")
                .split(";")[2]
                .split(", ")[1]
                .split("=")[1])

    logger.info("Authentication - Get sid: Success.")

    return cookies
