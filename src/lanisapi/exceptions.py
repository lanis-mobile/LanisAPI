"""Here are all all Lanis- and lib-related Exceptions."""


class PageNotFoundError(Exception):
    """Returned if Lanis couldn't find the page (404)."""


class LoginPageRedirectError(Exception):
    """Returned if Lanis returned the login page."""


class NotAuthenticatedError(Exception):
    """Returned if ``LanisClient`` or ``Cryptor`` wasn't authenticated yet."""


class AppNotAvailableError(Exception):
    """Returned if you tried to access a not supported applet by your school."""


class CriticalElementWasNotFoundError(Exception):
    """Returned if a critical html element was not found."""
