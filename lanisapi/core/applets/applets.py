from functools import cache

import httpx

from .parse import parse_applets
from ..constants import URL


@cache
def get_applets(request: httpx.Client) -> list[dict]:
    """Gets the various applets which you can see on the start page."""

    response = request.get(
        URL.start,
        params={
            "a": "ajax",
            "f": "apps"
        }
    )

    return response.json()["entrys"]


def get_applet_availability(link: str, request: httpx.Client) -> bool:
    """
    Checks if the applet is supported by the account.

    :param link: A full link with https as a scheme or a short link just with the filename of the applet.
    :param request: An authenticated :class:`httpx.Client` instance.
    :return: If supported return true if not return false.
    """

    applets = parse_applets(get_applets(request))
    for applet in applets:
        if applet.link.find(link) != -1:
            return True
    return False

