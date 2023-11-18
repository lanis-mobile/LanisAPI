"""This script includes the LanisClient to interact with Lanis."""

from datetime import datetime

import httpx

from .constants import LOGGER, URL
from .functions.apps import App, _get_app_availability, _get_apps, _get_available_apps
from .functions.authentication_types import LanisAccount, LanisCookie
from .functions.calendar import Calendar, _get_calendar, _get_calendar_month
from .functions.conversations import Conversation, _get_conversations
from .functions.schools import _get_schools
from .functions.substitution import SubstitutionPlan, _get_substitutions
from .functions.tasks import Task, _get_tasks
from .helpers.authentication import (
    get_authentication_sid,
    get_authentication_url,
    get_session,
)
from .helpers.cryptor import Cryptor
from .helpers.html_logger import HTMLLogger
from .helpers.request import Request
from .helpers.wrappers import check_availability, handle_exceptions, requires_auth


class LanisClient:
    """The interface between python and Schulportal Hessen.

    Use ``authenticate()`` to use this interface.

    Parameters
    ----------
    authentication : LanisAccount | LanisCookie
        1. A Lanis account with its username and password, and a school id or school name and city in ``School``.
        2. Cookies with authentication data (school id and session id) in ``LanisCookie`` for instantly interacting with Lanis. You can obtain this during a session with ``authentication_cookies``.
    save : bool, default True
        If False the school list, html data logs and future things won't be saved to a file.
    ad_header : httpx.Headers, default {"user-agent": ....}
        Send custom headers to Lanis. Primarily used to send a
        custom ``user-agent``.
    """

    def __init__(  # noqa: D107
        self,
        authentication: LanisAccount | LanisCookie,
        save: bool = True,
        ad_header: httpx.Headers = None,
    ) -> None:
        self.authentication = authentication

        self.save = save

        self.ad_header = (
            ad_header
            if ad_header is not None
            else httpx.Headers(
                {
                    "user-agent": "LanisClient by kurwjan and contributors (https://github.com/kurwjan/LanisAPI/)"
                }
            )
        )

        self.authenticated = False

        Request.set_headers(self.ad_header)

        self.cryptor = Cryptor()

        LOGGER.info("USING VERSION 0.3.1")

        LOGGER.warning("LANISAPI IS STILL IN A EARLY STAGE SO EXPECT BUGS.")

        LOGGER.warning(
            "IMPORTANT: Schulportal Hessen can change things quickly "
            "and is fragmented (some schools work, some not), "
            "so expect something to not be working"
        )

        HTMLLogger.setup(self.save)

    def __del__(self) -> None:
        """If the script closes close the parser."""
        Request.close()

    def close(self) -> None:
        """Close the client; you need to do this."""
        Request.close()
        self.authenticated = False
        LOGGER.info("Closed current session.")

    @property
    def authentication_cookies(self) -> LanisCookie:
        """Return ``LanisCookie`` with the authentication data (school id and session id) if authenticated. You can use this to authenticate with Lanis instantly."""
        cookies = Request.get_cookies()
        return LanisCookie(cookies.get("i", domain=""), cookies.get("sid"))

    @handle_exceptions
    def get_schools(self) -> list[dict[str, str]]:
        """Return all schools with their id, name and city.

        Returns
        -------
        list[dict[str, str]]
            JSON
        """
        return _get_schools(self.save)

    @handle_exceptions
    def authenticate(self) -> None:
        """Log into the school portal and sets the session id in the auth_cookies.

        Note
        ----
        Supports only the new system (login.schulportal.hessen.de).
        More at https://support.schulportal.hessen.de/knowledgebase.php?article=1087.
        """
        if self.authenticated:
            LOGGER.warning("Authenticate: Already authenticated.")
            return

        school_id: int

        if isinstance(self.authentication, LanisCookie):
            Request.set_cookies(
                {
                    "i": self.authentication.school_id,
                    "sid": self.authentication.session_id,
                }
            )
            LOGGER.info(
                "Authenticate: Using cookies to authenticate, skip authentication."
            )
        else:
            # Check if a id or school and place is provided.
            if isinstance(self.authentication.school, str):
                school_id = self.authentication.school
            else:
                schools = self.get_schools()

                try:
                    school_id = next(
                        school
                        for school in schools
                        if school["Name"] == self.authentication.school.name
                        and school["Ort"] == self.authentication.school.city
                    )["Id"]
                except StopIteration:
                    LOGGER.warning(
                        "Authenticate: School doesn't exist, check for right spelling."
                    )
                    return

            # Get new session (value: SPH-Session) by posting to login page.
            response_session = get_session(
                school_id, self.authentication.username, self.authentication.password
            )
            response_cookies = response_session["cookies"]

            if not response_session["location"]:
                # It also could be other problems, Lanis can be very finicky.
                LOGGER.error(
                    "Authenticate: Could not log in, possibly wrong credentials."
                )
                return

            # Get authentication url to get sid.
            auth_url = get_authentication_url(response_cookies)

            # Get sid.
            Request.set_cookies(
                get_authentication_sid(auth_url, response_cookies, schoolid=school_id)
            )

        # Tell Lanis how to encrypt
        if not self.cryptor.authenticate():
            LOGGER.error("Authenticate: Couldn't handshake with Lanis.")
            return

        self.authenticated = True

        available_apps = _get_available_apps()

        LOGGER.info(
            "Available apps:\n"
            f"  Calendar: {'Kalender' in available_apps}\n"
            + f"  Tasks: {'Mein Unterricht' in available_apps}\n"
            + f"  Conversations: {'Nachrichten - Beta-Version' in available_apps}\n"
            + f"  Substitution plan: {'Vertretungsplan' in available_apps}"
        )

        LOGGER.info("Authenticated.")

    @requires_auth
    @handle_exceptions
    def logout(self) -> None:
        """Log out.

        Note
        ----
        For closing the current LanisClient use `close()`
        """
        Request.post(URL.index, data={"logout": "all"})
        self.authenticated = False
        LOGGER.info("Logged out.")

    @requires_auth
    @check_availability("Vertretungsplan")
    @handle_exceptions
    def get_substitution_plan(self) -> SubstitutionPlan:
        """Return the whole substitution plan of the current day.

        Returns
        -------
        SubstitutionPlan
        """
        return _get_substitutions()

    @requires_auth
    @handle_exceptions
    def get_calendar_of_month(self) -> Calendar:
        """Use the get_calendar() function but only returns all events of the current month.

        Returns
        -------
        Calendar
            `Calendar` with `Event`
        """
        return _get_calendar_month()

    @requires_auth
    @check_availability("Kalender")
    @handle_exceptions
    def get_calendar(
        self, start: datetime, end: datetime, json: bool = False
    ) -> Calendar:
        """Return all calendar events between the start and end date.

        Parameters
        ----------
        start : datetime.datetime
            Start date
        end : datetime.datetime
            End date
        json : bool, default False
            Returns Json with every property instead of the limited CalendarData.
            Defaults to False.

        Returns
        -------
        Calendar
            `Calendar` with `Event` or Json.
        """
        return _get_calendar(start, end, json)

    @requires_auth
    @check_availability("Mein Unterricht")
    @handle_exceptions
    def get_tasks(self) -> list[Task]:
        """Return all tasks from the "Mein Unterricht" page with downloads in .zip format.

        Returns
        -------
        list[TaskData]
        """
        return _get_tasks()

    @requires_auth
    @check_availability("Nachrichten - Beta-Version")
    @handle_exceptions
    def get_conversations(self, number: int = 5) -> list[Conversation]:
        """Return conversations from the "Nachrichten - Beta-Version".

        Parameters
        ----------
        number : int, optional
            The number of conversations to return, by default 5. To get all conversations use -1 but this will take a while and spam Lanis servers.

        Returns
        -------
        list[Conversation]
            The conversations in Conversation.
        """
        return _get_conversations(self.cryptor, number)

    @requires_auth
    @handle_exceptions
    def get_apps(self) -> list[App]:
        """Get all web applets from Lanis, not only supported ones.

        Returns
        -------
        list[App]
            A list of `App`.
        """
        return _get_apps()

    @requires_auth
    @handle_exceptions
    def get_available_apps(self) -> list[str]:
        """Get all supported web applets by this library which are also supported by the Lanis of the user.

        Returns
        -------
        list[str]
            A list of the supported applets.
        """
        return _get_available_apps()

    @requires_auth
    @handle_exceptions
    def get_app_availability(self, app_name: str) -> bool:
        """Check if one of these apps: ``Kalender``, ``Mein Unterricht``, ``Nachrichten - Beta-Version``, ``Vertretungsplan`` is supported by the school.

        Parameters
        ----------
        app_name : str
            The applet name.

        Returns
        -------
        bool
        """
        return _get_app_availability(app_name)
