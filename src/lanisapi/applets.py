"""Collection of stuff for receiving applets and getting their availability."""

from dataclasses import dataclass
from functools import cache
from urllib.parse import urljoin

import httpx

from ._constants import URL


@dataclass
class Applet:
    """An applet/module of Lanis."""

    name: str
    link: str
    color: str


def parse_applets(json: list[dict]) -> list[Applet]:
    """
    Parses a JSON of applets into a list of dataclasses.

    :param list[dict] json: A JSON of applets.
    :return: A list of :class:`Applet` objects.
    :rtype: list[Applet]
    """

    applets: list[Applet] = []

    for applet in json:
        applets.append(Applet(applet['Name'], urljoin(URL.base, applet['link']), applet['Farbe']))

    return applets


@cache
def get_applets(request: httpx.Client) -> list[dict] | None:
    """
    Gets the various applets which you can see on the start page. The list has this format::

        list[
            dict{ -> Applet
                Name: str
                Farbe: str; rgb hex format
                Logo: str; uses font awesome v4 (maybe even older) and glyphicons
                Ordner: list[str]
                link: str
                target: str; doesn't always exist and often is set to "_blank"
            }
        ]

    The gotten value is cached throughout the runtime.

    :param httpx.Client request:
    :return: A list of applets in JSON or None when an error occurred.
    :rtype: list[dict] | None
    """

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

    :param str link: A full link with https as a scheme or a short link just with the filename of the applet.
    :param httpx.Client request:
    :return: If supported return true if not return false.
    :rtype: bool
    """

    applets = parse_applets(get_applets(request))
    for applet in applets:
        if applet.link.find(link) != -1:
            return True
    return False
