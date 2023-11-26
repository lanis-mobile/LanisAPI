"""A lib to interact with the Schulportal Hessen. Use LanisClient to interact."""

from .client import LanisClient
from .functions.apps import App, Folder
from .functions.authentication_types import LanisAccount, LanisCookie, School, SessionType
from .functions.calendar import Calendar
from .functions.conversations import Conversation
from .functions.substitution import SubstitutionPlan
from .functions.tasks import Task

__all__ = [
    "LanisClient",
    "Task",
    "SubstitutionPlan",
    "Calendar",
    "Conversation",
    "App",
    "Folder",
    "LanisAccount",
    "LanisCookie",
    "School",
    "SessionType"
]
