"""This script includes functions and classes for getting Lanis applets and checking for the availability of this library supported applets."""

import re
from dataclasses import dataclass
from difflib import SequenceMatcher
from functools import cache
from urllib.parse import urljoin

from ..constants import LOGGER, URL
from ..helpers.request import Request


@dataclass
class Folder:
    """A Lanis web folder.

    Parameters
    ----------
    name : str
        The name.
    symbol : str
        A symbol which represents this applet. Lanis uses Font Awesome and Glyphicons for this.
    colour : str
        The colour of these small top bars which you can see on Lanis.
    """

    name: str
    symbol: str
    colour: str


@dataclass
class App:
    """A Lanis web applet.

    Parameters
    ----------
    name : str
        The name.
    colour : str
        The colour which you can see on Lanis.
    folder : list of Folder
        The groups, category, folder or how you want to call it of the app.
        You can see it on the index page of Lanis.
    link : str
        The full Lanis link.
    symbol : str
        A symbol which represents this applet. Lanis uses Font Awesome and Glyphicons for this.
    """

    name: str
    colour: str
    folder: list[Folder]
    link: str
    symbol: str


@cache
def _get_folders() -> list[Folder]:
    """Get all web folders from Lanis.

    Returns
    -------
    list[Folder]
        A list of Folder.
    """
    folders: list[Folder] = []

    response = Request.get(URL.index, params={"a": "ajax", "f": "apps"})

    for entry in response.json()["folders"]:
        folders.append(
            Folder(
                name=entry["name"],
                symbol=re.sub(
                    r"(fas.|fa.|flip-\w+|glyphicon.|-o|-alt|fw|\n|\r| )",
                    "",
                    entry["logo"],
                ),
                colour=None if entry["farbe"] == "000000" else entry["farbe"],
            )
        )

    LOGGER.info("Get folders: Success.")

    return folders


@cache
def _get_apps() -> list[App]:
    """Get all web applets from Lanis, not only supported ones.

    Returns
    -------
    list[App]
        A list of ``App``.
    """
    apps: list[App] = []

    folders = _get_folders()

    response = Request.get(URL.index, params={"a": "ajax", "f": "apps"})

    for entry in response.json()["entrys"]:
        # Get Folder dataclass from folder list.
        folder: list[str] = []
        for entry_folder in entry["Ordner"]:
            folder.append(
                next(folder for folder in folders if folder.name == entry_folder)
            )

        apps.append(
            App(
                name=entry["Name"],
                colour=entry["Farbe"],
                folder=folder,
                link=urljoin(URL.base, entry["link"]),
                symbol=re.sub(
                    r"(fas.|fa.|flip-\w+|glyphicon.|-o|-alt|fw|\n|\r| )",
                    "",
                    entry["Logo"],
                ),
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
                > 0.8  # Probably need to tweak this number
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
