"""This script includes functions that wrap other functions."""

from functools import wraps

import httpx

from ..constants import LOGGER
from ..exceptions import NotAuthenticatedError, PageNotFoundError


def handle_exceptions(function: any) -> any:
    """Handle exceptions that may happen and raise them."""
    @wraps(function)
    def handle_exception_wrapper(*args: tuple, **kwargs: dict[str, any]) -> any:
        try:
            return function(*args, **kwargs)
        except httpx.RequestError as err:
            LOGGER.exception(f"A {err.__class__.__name__} happend while requesting: {err}")
        except PageNotFoundError as err:
            raise err
    return handle_exception_wrapper

def requires_auth(function: any) -> any:
    """Check if the class is authenticated and returns the function if true."""
    @wraps(function)
    def check_authenticated(*args: tuple, **kwargs: dict[str, any]) -> any:
        if not args[0].authenticated:
            msg = f"Exception at {function.__qualname__}: Not authenticated."
            raise NotAuthenticatedError(msg)
        return function(*args, **kwargs)
    return check_authenticated
