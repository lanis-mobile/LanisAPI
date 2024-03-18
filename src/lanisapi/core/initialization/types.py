import httpx

from .authenticate import get_session, get_authentication_url, get_authentication_cookies


class CookieInitialization:
    request = httpx.Client()

    def __init__(self, school_id, cookies):
        self.school_id = school_id
        self.cookies = cookies

        self.request.cookies = self.cookies


class AccountInitialization(CookieInitialization):
    def __init__(self, school_id, username, password):
        cookies, next_page = get_session(self.request, school_id, username, password)

        if not next_page:
            raise NotImplementedError

        auth_page = get_authentication_url(self.request, cookies)

        super().__init__(school_id, get_authentication_cookies(self.request, auth_page, cookies, school_id))
