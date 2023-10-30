"""This script includes the Request class to post and get with exception handling."""

import httpx

from ..exceptions import PageNotFoundError


class Request:
    """Post and get with a httpx client and exception handling."""

    client: httpx.Client = httpx.Client(timeout=httpx.Timeout(30.0, connect=60.0))

    @classmethod
    def post(cls: any, *args: tuple, **kwargs: dict[str, any]) -> httpx.Response:
        """Return a response using the post function from httpx.Client."""
        response = cls.client.post(*args, **kwargs)

        if response.status_code == 404:
            msg = f"Lanis couldn't find the specified page: {response.url}"
            raise PageNotFoundError(msg)

        return response

    @classmethod
    def get(cls: any, *args: tuple, **kwargs: dict[str, any]) -> httpx.Response:
        """Return a response using the get function from httpx.Client."""
        response = cls.client.post(*args, **kwargs)

        if response.status_code == 404:
            msg = f"Lanis couldn't find the specified page: {response.url}"
            raise PageNotFoundError(msg)

        return response

    @classmethod
    def set_cookies(cls: any, cookie: httpx.Cookies) -> None:
        """Set cookies."""
        cls.client.cookies = cookie

    @classmethod
    def set_headers(cls: any, headers: httpx.Headers) -> None:
        """Set headers."""
        cls.client.headers = headers

    @classmethod
    def close(cls: any) -> None:
        """Close the httpx client."""
        cls.client.close()

