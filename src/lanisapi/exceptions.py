"""This script has all Lanis- and lib-related Exceptions."""

class PageNotFoundError(Exception):
    """Returned if Lanis couldn't find the page (404)."""

class NotAuthenticatedError(Exception):
    """Returned if `LanisClient` or `Cryptor` wasn't authenticated yet."""
