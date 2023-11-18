"""This script includes functions and classes for getting Lanis applets and checking for the availability of this library supported applets."""

from dataclasses import dataclass
from functools import cache
from urllib.parse import urljoin

from ..constants import LOGGER, URL
from ..helpers.request import Request


@dataclass
class App:
    """A Lanis web applet.

    Parameters
    ----------
    name : str
        The name.
    colour : str
        The colour which you can see on Lanis.
    group : str
        The groups, category, folder or how you want to call it of the app.
        You can see it on the index page of Lanis.
    link : str
        The full Lanis link.
    """

    name: str
    colour: str
    group: str
    link: str


@cache
def _get_apps() -> list[App]:
    """Get all web applets from Lanis, not only supported ones.

    Returns
    -------
    list[App]
        A list of ``App``.
    """
    apps: list[App] = []

    response = Request.get(URL.index, params={"a": "ajax", "f": "apps"})

    for entry in response.json()["entrys"]:
        apps.append(
            App(
                name=entry["Name"],
                colour=entry["Farbe"],
                group=entry["Ordner"][0],
                link=urljoin(URL.base, entry["link"]),
            )
        )

    LOGGER.info("Get apps: Success.")

    return apps


@cache
def _get_available_apps() -> list[str]:
    """Get all supported web applets by this library which are also supported by the Lanis of the user.

    Returns
    -------
    list[str]
        A list of the supported applets.
    """
    implemented_apps = [
        "Kalender",
        "mein Unterricht",
        "Nachrichten - Beta-Version",
        "Vertretungsplan",
    ]
    gotten_apps = _get_apps()

    available_apps: list[str] = []

    for app in gotten_apps:
        if app.name in implemented_apps:
            available_apps.append(app.name)

    LOGGER.info("Get apps availability: Success.")

    return available_apps


def _get_app_availability(app_name: str) -> bool:
    """Check if app is supported by the school.

    Parameters
    ----------
    app_name : str
        The applet name.

    Returns
    -------
    bool
    """
    available_apps = _get_available_apps()
    return app_name in available_apps
