from urllib.parse import urljoin
from dataclasses import dataclass

from ..constants import URL


@dataclass
class Applet:
    """An applet/module of Lanis."""

    name: str
    link: str
    color: str


def parse_applets(json: list[dict]) -> list[Applet]:
    """
    Parses a JSON of applets and returns a handy dataclass.

    :param json: A JSON of applets.
    :return: A list of :class:`Applet` objects.
    """

    applets: list[Applet] = []

    for applet in json:
        applets.append(Applet(applet['Name'], urljoin(URL.base, applet['link']), applet['Farbe']))

    return applets
