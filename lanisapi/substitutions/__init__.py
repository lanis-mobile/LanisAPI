"""Collection of functions and classes to get substitutions via the Ajax method. Non-Ajax method not yet supported."""

from .substitutions import get_substitution_dates, get_substitutions
from .parse import parse_substitutions, Substitution, SubstitutionDay

substitution_link = "https://start.schulportal.hessen.de/vertretungsplan.php"
