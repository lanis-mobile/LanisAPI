from functools import cache

import httpx

from .parse import parse_applets
from ..constants import URL


@cache
def get_applets(request: httpx.Client) -> list[dict]:
    response = request.get(
        URL.start,
        params={
            "a": "ajax",
            "f": "apps"
        }
    )

    return response.json()["entrys"]


def get_applet_availability(link: str, request: httpx.Client) -> bool:
    applets = parse_applets(get_applets(request))
    for applet in applets:
        if applet.link.find(link) != -1:
            return True
    return False
