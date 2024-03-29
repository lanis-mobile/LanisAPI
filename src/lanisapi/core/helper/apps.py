from dataclasses import dataclass
from functools import cache
from urllib.parse import urljoin

import httpx
from .url import URL


@dataclass
class App:
    name: str
    link: str


@cache
def get_apps(request: httpx.Client) -> list[App]:
    response = request.get(URL.index, params={
        "a": "ajax",
        "f": "apps"
    })

    apps = []
    for app in response.json()["entrys"]:
        apps.append(App(
            name=app["Name"],
            link=urljoin(URL.index, app["link"])
        ))

    return apps


def is_link_supported(link, apps: list[App]) -> bool:
    for app in apps:
        if app.link == link:
            return True
