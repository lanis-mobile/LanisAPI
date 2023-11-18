"""This script includes the Request class to request data with exception handling."""

import httpx

from ..exceptions import LoginPageRedirectError, PageNotFoundError


class Request:
    """Request with a httpx client and exception handling."""

    client: httpx.Client = httpx.Client(timeout=httpx.Timeout(30.0, connect=60.0))

    @classmethod
    def post(cls, *args: tuple, **kwargs: dict[str, any]) -> httpx.Response:
        """Return a response using the post function from httpx.Client."""
        response = cls.client.post(*args, **kwargs)

        return cls._check_response(response)

    @classmethod
    def get(cls, *args: tuple, **kwargs: dict[str, any]) -> httpx.Response:
        """Return a response using the get function from httpx.Client."""
        response: httpx.Response = cls.client.post(*args, **kwargs)

        return cls._check_response(response)

    @classmethod
    def head(cls, *args: tuple, **kwargs: dict[str, any]) -> httpx.Response:
        """Return a response using the head function from httpx.Client."""
        response: httpx.Response = cls.client.head(*args, **kwargs)

        return cls._check_response(response)

    @classmethod
    def request(cls, *args: tuple, **kwargs: dict[str, any]) -> httpx.Response:
        """Return a response using the request function from httpx.Client."""
        response: httpx.Response = cls.client.request(*args, **kwargs)

        return cls._check_response(response)

    @classmethod
    def set_cookies(cls, cookie: httpx.Cookies) -> None:
        """Set cookies."""
        cls.client.cookies = cookie

    @classmethod
    def get_cookies(cls) -> httpx.Cookies:
        """Get cookies."""
        return cls.client.cookies

    @classmethod
    def set_headers(cls, headers: httpx.Headers) -> None:
        """Set headers."""
        cls.client.headers = headers

    @classmethod
    def close(cls) -> None:
        """Close the httpx client."""
        cls.client.close()

    @classmethod
    def _check_response(cls, response: httpx.Response) -> httpx.Response:
        if response.status_code == 404:
            msg = f"Lanis couldn't find the specified page: {response.url}"
            raise PageNotFoundError(msg)

        header_cookies = response.headers.get("set-cookie")
        if header_cookies and header_cookies == "i=0; secure":
            msg = f"Lanis returned the login page while trying to access {response.url}. Maybe the session is over."
            raise LoginPageRedirectError(msg)

        return response
