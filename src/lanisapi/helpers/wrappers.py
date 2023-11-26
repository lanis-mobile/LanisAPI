"""This script includes functions that wrap other functions."""

from functools import wraps
from types import FunctionType

import httpx

from ..constants import LOGGER
from ..exceptions import (
    AppNotAvailableError,
    CriticalElementWasNotFoundError,
    ForceNewAuthenticationError,
    LoginPageRedirectError,
    NoSchoolFoundError,
    NotAuthenticatedError,
    PageNotFoundError,
    WrongCredentialsError,
)
from ..functions.apps import _get_app_availability


def handle_exceptions(function: FunctionType) -> FunctionType:
    """Handle general exceptions that may happen and raise them."""

    @wraps(function)
    def handle_exceptions_wrapper(
        *args: tuple, **kwargs: dict[str, any]
    ) -> FunctionType:
        # Check code
        try:
            return function(*args, **kwargs)
        except httpx.RequestError as err:
            LOGGER.exception(
                f"A {err.__class__.__name__} happened while requesting: {err}"
            )
        except (
            PageNotFoundError,
            CriticalElementWasNotFoundError,
            LoginPageRedirectError,
            NoSchoolFoundError,
            WrongCredentialsError,
            ForceNewAuthenticationError,
        ) as err:
            raise err

    return handle_exceptions_wrapper


def requires_auth(function: FunctionType) -> FunctionType:
    """Check if the class is authenticated and returns the function if true."""

    @wraps(function)
    def check_authentication_wrapper(
        *args: tuple, **kwargs: dict[str, any]
    ) -> FunctionType:
        # Check code
        if not args[0].authenticated:
            msg = f"Exception at {function.__qualname__}: Not authenticated."
            raise NotAuthenticatedError(msg)
        return function(*args, **kwargs)

    return check_authentication_wrapper


def check_availability(app_name: str) -> FunctionType:
    """Check if the applet of the function is supported by the school."""

    def check_availability_decorator(function: FunctionType) -> FunctionType:
        @wraps(function)
        def check_availability_wrapper(
            *args: tuple, **kwargs: dict[str, any]
        ) -> FunctionType:
            # Check code
            if not _get_app_availability(app_name):
                msg = f"The app ({app_name}) of the function {function.__name__} is not available!"
                raise AppNotAvailableError(msg)
            return function(*args, **kwargs)

        return check_availability_wrapper

    return check_availability_decorator
