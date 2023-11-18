"""This script includes functions and classes for getting Lanis applets and checking for the availability of this library supported applets."""

from dataclasses import dataclass
from difflib import SequenceMatcher
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
        A list which contains some of these strings: ``Kalender``, ``Mein Unterricht``, ``Nachrichten - Beta-Version``, ``Vertretungsplan``
    """
    implemented_apps = [
        "Kalender",
        "Mein Unterricht",
        "Nachrichten - Beta-Version",  # Yeah there are probably more names for that app
        "Vertretungsplan",
    ]
    gotten_apps = _get_apps()

    available_apps: list[str] = []

    # We use Python's SequenceMatcher to get similar applet names.
    for app in gotten_apps:
        for implemented in implemented_apps:
            if (
                SequenceMatcher(None, app.name.lower(), implemented.lower()).ratio()
                > 0.8 # Probably need to tweak this number
            ):
                available_apps.append(implemented)

    LOGGER.info("Get apps availability: Success.")

    return available_apps


@cache
def _get_app_availability(app_name: str) -> bool:
    """Check if one of these apps: ``Kalender``, ``Mein Unterricht``, ``Nachrichten - Beta-Version``, ``Vertretungsplan`` is supported by the school.

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
