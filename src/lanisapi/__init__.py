"""A package for interacting with Lanis."""

from .__version__ import __description__, __title__, __version__
from .auth import authenticate, Account
from .schools import *
from .applets import *

__all__ = [
    "authenticate",
    "Account",
    "District",
    "School",
    "parse_schools",
    "get_schools",
    "get_school_id",
    "get_applets",
    "get_applet_availability",
    "parse_applets",
    "Applet",
]