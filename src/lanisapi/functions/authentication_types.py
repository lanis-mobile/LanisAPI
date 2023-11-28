"""This script includes handy dataclasses for authenticating with Lanis."""

from enum import Enum

from attrs import define, field


@define
class School:
    """Alternative to school id for authentication.

    Parameters
    ----------
    name : str
        Full school name
    city : str
        City name sometimes with abbreviations or fully written.
    """

    name: field(type=str)
    city: field(type=str)


@define
class LanisAccount:
    """An attrs class to authenticate with this library. It's a normal Lanis user account.

    Parameters
    ----------
    name : str or School
        School id or `School` class.
    username : str
        Format: firstname.lastname
    password : str
        The password.
    """

    school: field(type=str | School)
    username: field(type=str)
    password: field(type=str)


@define
class LanisCookie:
    """An attrs class to authenticate with this library. It's a cookie with the school id and session id.

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

    school_id: field(type=str)
    session_id: field(type=str)


class SessionType(Enum):
    """Used in ``authenticate()`` to indicate which session type you want.

    * NORMAL, used to get a normal session which lasts 100min.
    * LONG, used to get a 30-days (``angemeldet bleiben`` option).

    """

    NORMAL = 1
    LONG = 2
