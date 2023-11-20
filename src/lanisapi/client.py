"""This script includes the LanisClient to interact with Lanis."""

import json
import os
from base64 import b64decode, b64encode
from datetime import datetime, timedelta
from pathlib import Path
from time import time

import httpx
from Cryptodome.Cipher import AES
from Cryptodome.Protocol.KDF import scrypt
from Cryptodome.Random import get_random_bytes

from .constants import LOGGER, URL
from .exceptions import (
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

        self.authentication_method = None

        Request.set_headers(self.ad_header)

        self.cryptor = Cryptor()

        LOGGER.info("USING VERSION 0.4.0 ALPHA")

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

    @property
    def authentication_cookies(self) -> LanisCookie:
        """Return ``LanisCookie`` with the authentication data (school id and session id) if authenticated. You can use this to authenticate with Lanis instantly."""
        cookies = Request.get_cookies()
        return LanisCookie(cookies.get("i", domain=""), cookies.get("sid"))

    def close(self) -> None:
        """Close the client and saves to session.json; you need to do this."""
        Request.close()

        self.authenticated = False

        # If we already authenticated using the file just update it quickly
        if self.authentication_method == "SessionsFile":
            with open("session.json", "r+") as file:
                session_file: dict[str, any] = json.loads(file.read())
                session_file["timestamp"] = time()
                session_file.update(session_file)

                file.seek(0)
                file.write(json.dumps(session_file))

            LOGGER.info("Closed current session.")

            return

        # Encrypt the session data using AES-GCM and scrypt for the key
        salt = get_random_bytes(12)
        key = b64encode(scrypt(self.authentication.password, salt, 16, 2**14, 8, 1))
        cipher = AES.new(key, AES.MODE_GCM, nonce=salt)

        session_id = cipher.encrypt_and_digest(
            self.authentication_cookies.session_id.encode()
        )

        # session_id: Append salt to beginning (16 chars) then mac (32 chars) and then the ciphertext.
        session_data = {
            "school_id": self.authentication_cookies.school_id,
            "session_id": f"{b64encode(salt).decode()}{b64encode(session_id[1]).decode()}{b64encode(session_id[0]).decode()}",
            "timestamp": time(),
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

                session_file: dict[str, any] = json.loads(raw_session_file)
                session_file.update(session_data)

                file.seek(0)
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
        return _get_schools(self.save)

    @handle_exceptions
    def authenticate(self, force: bool = False) -> None:
        """Log into the school portal and sets the session id in the auth_cookies.

        Parameters
        ----------
        force : bool, optional
            If True it always makes a new session with Lanis, by default False

        Note
        ----
        Supports only the new system (login.schulportal.hessen.de).
        More at https://support.schulportal.hessen.de/knowledgebase.php?article=1087.
        """
        if self.authenticated:
            LOGGER.warning("Authenticate: Already authenticated.")
            return

        school_id: int

        if not force:
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
                self.authentication_method = "LanisCookie"
            elif Path("session.json").exists():
                with open("session.json", "r") as file:
                    raw_session_file = file.read()

                # If session file is empty return forced authenticate
                if raw_session_file:
                    try:
                        session_file: dict[str, any] = json.loads(raw_session_file)
                    except json.JSONDecodeError:
                        LOGGER.warning("Authenticate: session.json file is corrupted.")
                        os.remove("session.json")
                        self.authenticate(True)
                        return
                else:
                    LOGGER.info("Authenticate: session.json file is empty.")
                    self.authenticate(True)
                    return

                # If session data is not older then 100 minutes.
                if session_file and datetime.fromtimestamp(
                    session_file["timestamp"]
                ) > datetime.now() + timedelta(minutes=-100):
                    # Preparing the decrypt of the session id.
                    salt = b64decode(session_file["session_id"][:16])
                    mac = b64decode(session_file["session_id"][16:40])
                    key = b64encode(
                        scrypt(
                            self.authentication.password, salt, 16, 2**14, 8, 1
                        )
                    )
                    cipher = AES.new(key, AES.MODE_GCM, nonce=salt)

                    # Decrypt and verify if the mac is right.
                    try:
                        session_id = cipher.decrypt_and_verify(
                            b64decode(session_file["session_id"][40:].encode()), mac
                        ).decode()
                    except ValueError:
                        LOGGER.info("Authenticate: session.json file is corrupted.")
                        self.authenticate(True)
                        return

                    Request.set_cookies(
                        {
                            "i": session_file["school_id"],
                            "sid": session_id,
                        }
                    )
                else:
                    LOGGER.info("Authenticate: Session.json file is outdated.")
                    os.remove("session.json")
                    self.authenticate(True)
                    return

                LOGGER.info("Authenticate: Using found session.json file.")
                self.authentication_method = "SessionsFile"

        if force or not (
            Path("session.json").exists()
            or isinstance(self.authentication, LanisCookie)
        ):
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

            # Get new session (value: SPH-Session) by posting to login page.
            response_session = get_session(
                school_id, self.authentication.username, self.authentication.password
            )
            response_cookies = response_session["cookies"]

            if not response_session["location"]:
                # It also could be other problems, Lanis can be very finicky.
                msg = "Could not log in, possibly wrong credentials."
                raise WrongCredentialsError(msg)

            # Get authentication url to get sid.
            auth_url = get_authentication_url(response_cookies)

            # Get sid.
            Request.set_cookies(
                get_authentication_sid(auth_url, response_cookies, schoolid=school_id)
            )

            self.authentication_method = "LanisAccount"

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
