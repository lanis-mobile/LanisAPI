from dataclasses import dataclass
from urllib.parse import urljoin

import httpx
from .url import URL


@dataclass
class App:
    name: str
    link: str


def get_apps(request: httpx.Client):
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


def _is_supported(link, apps: list[App]):
    for app in apps:
        if app.link == link:
            return True
