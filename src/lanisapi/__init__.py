from .__version__ import __description__, __title__, __version__
from .auth import authenticate, Account
from .schools import *

__all__ = [
    authenticate,
    Account,
    District,
    School,
    parse_schools,
    get_schools,
    get_school_id,
]