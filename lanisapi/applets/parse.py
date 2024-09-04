from urllib.parse import urljoin
from dataclasses import dataclass

from ..constants import URL


@dataclass
class Applet:
    name: str
    link: str
    color: str


def parse_applets(json: list[dict]) -> list[Applet]:
    applets: list[Applet] = []

    for applet in json:
        applets.append(Applet(applet['Name'], urljoin(URL.base, applet['link']), applet['Farbe']))

    return applets
