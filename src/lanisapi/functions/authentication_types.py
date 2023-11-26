"""This script includes handy dataclasses for authenticating with Lanis."""

from dataclasses import dataclass
from enum import Enum


@dataclass
class School:
    """Alternative to school id for authentication.

    Parameters
    ----------
    name : str
        Full school name
    city : str
        City name sometimes with abbreviations or fully written.
    """

    name: str
    city: str


@dataclass
class LanisAccount:
    """A dataclass to authenticate with this library. It's a normal Lanis user account.

    Parameters
    ----------
    name : str or School
        School id or `School` class.
    username : str
        Format: firstname.lastname
    password : str
        The password.
    """

    school: str | School
    username: str
    password: str


@dataclass
class LanisCookie:
    """A dataclass to authenticate with this library. It's a cookie with the school id and session id.

    Parameters
    ----------
    school_id : str
        The id of the school.
    session_id : str
        The id or how Lanis calls it `sid` of a session.

    Note
    ----
    Use ``LanisClient.authentication_cookies`` from a previous session to get ``LanisCookie`` for the next session.
    """

    school_id: str
    session_id: str


class SessionType(Enum):
    """Used in ``authenticate()`` to indicate which session type you want.

    * NORMAL, used to get a normal session which lasts 100min.
    * LONG, used to get a 30-days (``angemeldet bleiben`` option).

    """

    NORMAL = 1
    LONG = 2
