"""A lib to interact with the Schulportal Hessen. Use LanisClient to interact."""

from .client import LanisClient
from .functions.calendar import Calendar
from .functions.conversations import Conversation
from .functions.schools import School
from .functions.substitution import SubstitutionPlan
from .functions.tasks import Task

__all__ = ["LanisClient", "Task", "SubstitutionPlan", "Calendar", "Conversation", "School"]
