"""
The _core elements of this library. It offers general stuff like authentication and other non-applet dependent stuff.
"""

from .schools import get_schools, get_school_id, School, District, parse_schools
from .applets import parse_applets, get_applet_availability, get_applets
from .authentication import Account, Session, Authentication

__all__ = ["get_schools", "get_school_id", "School",
           "District", "parse_schools", "parse_applets",
           "get_applet_availability", "get_applets", "Account",
           "Session", "Authentication"]
