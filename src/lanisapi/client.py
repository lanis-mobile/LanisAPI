"""This script includes the LanisClient to interact with Lanis."""

from datetime import datetime

import httpx

from .constants import LOGGER, URL
from .functions.calendar import Calendar, _get_calendar, _get_calendar_month
from .functions.conversations import Conversation, _get_conversations
from .functions.schools import School, _get_schools
from .functions.substitution import SubstitutionPlan, _get_substitutions
from .functions.tasks import Task, _get_tasks
from .helpers.authentication import (
    get_authentication_sid,
    get_authentication_url,
    get_session,
)
from .helpers.cryptor import Cryptor
from .helpers.request import Request
from .helpers.wrappers import handle_exceptions, requires_auth


class LanisClient:
    """The interface between python and Schulportal Hessen.

    Use ``authenticate()`` to use this interface.

    Parameters
    ----------
    school : str | School
        1. The id of the school which you can see it in the url at ``i=``.
        2. The school name and city in ``School``.
    username : str
        The username in firstname.lastname.
    password : str
        The password.
    save : bool, default True
        If False the school list and future things won't be saved to a file.
    ad_header : httpx.Headers, default {"user-agent": ....}
        Send custom headers to Lanis. Primarily used to send a
        custom ``user-agent``.
    """

    def __init__(self,
                 school: str | School,
                 username: str,
                 password: str,
                 save: bool = True,
                 ad_header: httpx.Headers = None,
                 ) -> None:

        self.school = school
        self.username = username
        self.password = password

        self.save = save

        self.ad_header = ad_header if ad_header is not None else httpx.Headers({ "user-agent":
                        "LanisClient by kurwjan and contributors (https://github.com/kurwjan/LanisAPI/)" })

        self.authenticated = False

        Request.set_headers(self.ad_header)

        self.cryptor = Cryptor()

        LOGGER.warning(
            "LANISAPI IS STILL IN A EARLY STAGE SO EXPECT BUGS.")

        LOGGER.warning(
            "IMPORTANT: Schulportal Hessen can change things quickly"
            "and is fragmented (some schools work, some not),"
            "so expect something to not be working")

    def __del__(self) -> None:
        """If the script closes close the parser."""
        Request.close()

    def close(self) -> None:
        """Close the client; you need to do this."""
        Request.close()
        self.authenticated = False
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
    def authenticate(self) -> None:
        """Log into the school portal and sets the session id in the auth_cookies.

        Note
        ----
        Supports only the new system (login.schulportal.hessen.de).
        More at https://support.schulportal.hessen.de/knowledgebase.php?article=1087.
        """
        if self.authenticated:
            LOGGER.warning("A1: Already authenticated.")
            return

        school_id: int

        # Check if a id or school and place is provided.
        if isinstance(self.school, str):
            school_id = self.school
        else:
            schools = self.get_schools()

            try:
                school_id = next(school for school in schools if school["Name"] == self.school.name and school["Ort"] == self.school.city)["Id"]
            except StopIteration:
                LOGGER.warning("Authenticate: School doesn't exist, check for right spelling.")
                return

        # Get new session (value: SPH-Session) by posting to login page.
        response_session = get_session(school_id, self.username, self.password)
        response_cookies = response_session["cookies"]

        if not response_session["location"]:
            # It also could be other problems, Lanis can be very finicky.
            LOGGER.error("Authenticate: Could not log in, possibly wrong credentials.")
            return

        # Get authentication url to get sid.
        auth_url = get_authentication_url(response_cookies)

        # Get sid.
        Request.set_cookies(get_authentication_sid(auth_url, response_cookies, schoolid=school_id))

        # Tell Lanis how to encrypt
        if not self.cryptor.authenticate():
            LOGGER.error("Authenticate: Couldn't handshake with Lanis.")
            return

        self.authenticated = True

        LOGGER.info("Authenticated.")

    @requires_auth
    @handle_exceptions
    def logout(self) -> None:
        """Log out.

        Note
        ----
        For closing the current LanisClient use `close()`
        """
        Request.post(URL.logout)
        self.authenticated = False
        LOGGER.info("Logged out.")

    @requires_auth
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
    @handle_exceptions
    def get_calendar(self, start: datetime,
                    end: datetime, json: bool = False) -> Calendar:
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
    @handle_exceptions
    def get_tasks(self) -> list[Task]:
        """Return all tasks from the "Mein Unterricht" page in .zip format.

        Returns
        -------
        list[TaskData]
        """
        return _get_tasks()

    @requires_auth
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
