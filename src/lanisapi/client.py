"""This script includes the LanisClient to interact with Lanis."""

import json
import os
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from time import time

import httpx

from .constants import JSON, LOGGER, URL
from .exceptions import (
    ForceNewAuthenticationError,
    NoSchoolFoundError,
    WrongCredentialsError,
)
from .functions.apps import (
    App,
    Folder,
    _get_app_availability,
    _get_apps,
    _get_available_apps,
    _get_folders,
)
from .functions.authentication_types import LanisAccount, LanisCookie, SessionType
from .functions.calendar import Calendar, _get_calendar, _get_calendar_month
from .functions.conversations import Conversation, _get_conversations
from .functions.schools import _get_schools
from .functions.substitution import SubstitutionPlan, _get_substitutions
from .functions.tasks import Task, _get_tasks
from .helpers.authentication import (
    get_authentication_sid,
    get_authentication_url,
    get_session,
    get_session_and_autologin,
    get_session_by_autologin,
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
    authentication : LanisAccount or LanisCookie or None
        1. A Lanis account with its username and password, and a school id or school name and city in ``School``.
        2. Cookies with authentication data (school id and session id) in ``LanisCookie`` for instantly interacting with Lanis. You can obtain this during a session with ``authentication_cookies``.
        3. If None it will use the session.json, like for the 30-days session or last session (100min), when no session.json exists, it will return ``ForceNewAuthenticationError``.
    ad_header : httpx.Headers, default {"user-agent": ....}
        Send custom headers to Lanis. Primarily used to send a
        custom ``user-agent``.
    """

    class AuthenticationMethod(Enum):
        """Used to indicate with which method that this lib provides was used."""

        LanisCookie = 1
        LanisAccount = 2
        SessionsFile = 3

    def __init__(  # noqa: D107
        self,
        authentication: LanisAccount | LanisCookie | None,
        ad_header: httpx.Headers = None,
    ) -> None:
        self.authentication = authentication
        self.ad_header = (
            ad_header
            if ad_header is not None
            else httpx.Headers(
                {
                    "user-agent": "LanisAPI by kurwjan and contributors (https://github.com/kurwjan/LanisAPI/)"
                }
            )
        )
        self.authenticated = False
        self.authentication_method: self.AuthenticationMethod = None
        self.session_type: SessionType = None
        self.autologin: list[str] | None = None
        self.cryptor = Cryptor()

        Request.set_headers(self.ad_header)

        LOGGER.info("USING VERSION 0.4.1 (0.4.0)")

        LOGGER.warning("LANISAPI IS STILL IN A EARLY STAGE SO EXPECT BUGS.")

        LOGGER.warning(
            "IMPORTANT: Schulportal Hessen can change some things "
            "and is fragmented (some schools work, some not), "
            "so expect something to not be working"
        )

        HTMLLogger.init()

    def __del__(self) -> None:
        """If the script closes close the parser."""
        Request.close()

    @property
    def authentication_cookies(self) -> LanisCookie:
        """Return ``LanisCookie`` with the authentication data (school id and session id) if authenticated. You can use this to authenticate with Lanis instantly."""
        cookies = Request.get_cookies()
        return LanisCookie(cookies.get("i", domain=""), cookies.get("sid"))

    def close(self) -> None:
        """Close the client and saves to session.json; you need to do this."""
        Request.close()

        self.authenticated = False

        if (
            self.session_type == SessionType.LONG
            and self.authentication_method == self.AuthenticationMethod.SessionsFile
        ):
            LOGGER.info("Closed current session.")

            return

        session_data_normal = {
            "session_id": self.authentication_cookies.session_id,
            "timestamp": time(),
        }

        session_data_long = (
            {"autologin": self.autologin[0], "timestamp": self.autologin[1]}
            if self.session_type == SessionType.LONG
            else None
        )

        session_data = {
            "SCHOOLID": self.authentication_cookies.school_id,
            "NORMAL": session_data_normal,
            "LONG": session_data_long,
        }

        # If file exist update it.
        if Path("session.json").exists():
            with open("session.json", "r+") as file:
                raw_session_file = file.read()
                # If empty
                if not raw_session_file:
                    file.write(json.dumps(session_data))
                    LOGGER.info("Closed current session.")
                    return

                session_file: JSON = json.loads(raw_session_file)
                session_data["LONG"] = (
                    session_file["LONG"]
                    if session_data["LONG"] is None
                    else session_data["LONG"]
                )
                session_data["NORMAL"]["timestamp"] = time()
                session_file.update(session_data)

                file.seek(0)
                file.truncate(0)
                file.write(json.dumps(session_file))
        else:
            with open("session.json", "w") as file:
                file.write(json.dumps(session_data))

        LOGGER.info("Closed current session.")

    @handle_exceptions
    def get_schools(self) -> list[dict[str, str]]:
        """Return all schools with their id, name and city.

        Returns
        -------
        list[dict[str, str]]
            JSON
        """
        return _get_schools()

    @handle_exceptions
    def _create_new_session(self) -> None:
        # Check if a id or school and place is provided.
        if isinstance(self.authentication.school, str):
            school_id = self.authentication.school
        else:
            schools = self.get_schools()

            # Try to get wanted school with a one liner generator.
            try:
                school_id = next(
                    school
                    for school in schools
                    if school["Name"] == self.authentication.school.name
                    and school["Ort"] == self.authentication.school.city
                )["Id"]
            except StopIteration as err:
                msg = "School doesn't exist, check for right spelling."
                raise NoSchoolFoundError(msg) from err

        # Get new session (value: SPH-Session) and autologin token by posting to login page.
        if self.session_type == SessionType.LONG:
            response_cookies, autologin = get_session_and_autologin(
                school_id, self.authentication.username, self.authentication.password
            )
            self.autologin = autologin
            response_location = "."
        else:
            response_cookies, response_location = get_session(
                school_id, self.authentication.username, self.authentication.password
            )

        if not response_location:
            # It also could be other problems, Lanis can be very finicky.
            msg = "Could not log in, possibly wrong credentials."
            raise WrongCredentialsError(msg)

        # Get authentication url to get sid.
        auth_url = get_authentication_url(response_cookies)

        # Get sid.
        Request.set_cookies(
            get_authentication_sid(auth_url, response_cookies, school_id)
        )

        self.authentication_method = self.AuthenticationMethod.LanisAccount

    @handle_exceptions
    def _get_from_sessions_file(self) -> None:
        with open("session.json", "r") as file:
            raw_session_file = file.read()

            # If session file is empty return forced authenticate
            if raw_session_file:
                try:
                    session_file: JSON = json.loads(raw_session_file)
                except json.JSONDecodeError as err:
                    LOGGER.warning("Authenticate: session.json file is corrupted.")

                    if not self.authentication:
                        msg = "Can't login, no credentials and corrupted session.json."
                        raise WrongCredentialsError(msg) from err

                    os.remove("session.json")
                    self.authenticate(force=True, session_type=self.session_type)
                    raise ForceNewAuthenticationError from err
            else:
                LOGGER.info("Authenticate: session.json file is empty.")

                if not self.authentication:
                    msg = "Can't login, no credentials and empty session.json."
                    raise WrongCredentialsError(msg)

                self.authenticate(force=True, session_type=self.session_type)
                raise ForceNewAuthenticationError

            try:
                if session_file["NORMAL"] and datetime.fromtimestamp(
                    session_file["NORMAL"]["timestamp"]
                ) > datetime.now() + timedelta(minutes=-100):
                    session_id = session_file["NORMAL"]["session_id"]
                else:
                    LOGGER.info(
                        "Authenticate: Check for long session, because normal session is empty or outdated."
                    )
                    # Check if autologin timestamp is older then now.
                    if (
                        session_file["LONG"]
                        and datetime.fromtimestamp(session_file["LONG"]["timestamp"])
                        > datetime.now()
                    ):
                        LOGGER.info(
                            "Authenticate: Get now session id by autologin token."
                        )

                        self.autologin = session_file["LONG"]["autologin"]

                        response_cookies = get_session_by_autologin(
                            session_file["SCHOOLID"], self.autologin
                        )

                        auth_url = get_authentication_url(response_cookies)

                        session_id = get_authentication_sid(
                            auth_url,
                            response_cookies,
                            schoolid=session_file["SCHOOLID"],
                        )["sid"]

                        self.session_type = SessionType.LONG
                    else:
                        LOGGER.info("Authenticate: Long session is outdated or empty.")
                        os.remove("session.json")
                        self.authenticate(force=True, session_type=self.session_type)
                        raise ForceNewAuthenticationError
            except (ValueError, KeyError) as err:
                LOGGER.info("Authenticate: session.json file is corrupted.")

                if not self.authentication:
                    msg = "Can't login, no credentials and corrupted session.json."
                    raise WrongCredentialsError(msg) from err

                self.authenticate(force=True, session_type=self.session_type)
                raise ForceNewAuthenticationError from err

            Request.set_cookies(
                {
                    "i": session_file["SCHOOLID"],
                    "sid": session_id,
                }
            )

            LOGGER.info("Authenticate: Using found session.json file.")
            self.authentication_method = self.AuthenticationMethod.SessionsFile

    @handle_exceptions
    def authenticate(
        self, session_type: SessionType = SessionType.NORMAL, force: bool = False
    ) -> None:
        """Log into the school portal and sets the session id in the auth_cookies.

        Parameters
        ----------
        force : bool, optional
            If True it always makes a new session with Lanis, by default False
        session_type : SessionType, optional by default SessionType.NORMAL
            Which session to create.
            There are two session types: NORMAL and LONG. The long session is 30-days long (``angemeldet bleiben`` option) and needs no password or name to be put in afterwards.
            It does not force a new session!

        Note
        ----
        Supports only the new system (login.schulportal.hessen.de).
        More at https://support.schulportal.hessen.de/knowledgebase.php?article=1087.
        """
        if self.authenticated:
            LOGGER.warning("Authenticate: Already authenticated.")
            return

        self.session_type = session_type

        if self.authentication is None and not Path("session.json").exists():
            msg = "Can't login, no credentials and no session.json."
            raise WrongCredentialsError(msg)

        # First check if we can restore session from a file.
        if not force:
            # LanisCookie login (highest priority)
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
                self.authentication_method = self.AuthenticationMethod.LanisCookie
            # Login with session.json
            elif Path("session.json").exists():
                try:
                    self._get_from_sessions_file()
                except ForceNewAuthenticationError:
                    LOGGER.info("Authenticate: Forced new authentication, return.")
                    return

        # Create new session if force is True or the other methods are False.
        if force or not (
            Path("session.json").exists()
            or isinstance(self.authentication, LanisCookie)
        ):
            self._create_new_session()

        # Tell Lanis how to encrypt
        if not self.cryptor.authenticate():
            LOGGER.error("Authenticate: Couldn't handshake with Lanis.")
            return

        self.authenticated = True

        available_apps = _get_available_apps()

        LOGGER.info(f"Session type: {self.session_type.name}")

        LOGGER.info(f"Authentication method: {self.authentication_method.name}")

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

    @requires_auth
    @handle_exceptions
    def get_folders(self) -> list[Folder]:
        """Get all web folders from Lanis.

        Returns
        -------
        list[Folder]
            A list of Folder.
        """
        return _get_folders()
