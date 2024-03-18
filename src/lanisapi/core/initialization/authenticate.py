import httpx

from ..helper.url import URL


def get_session(request: httpx.Client, school_id, username, password):
    params = {
        "i": school_id
    }

    data = {
        "user2": username,
        "user": f"{school_id}.{username}",
        "password": password
    }

    response = request.post(URL.login, data=data, params=params)

    cookies = httpx.Cookies()
    cookies.set(
        "SPH-Session",
        response.headers.get("set-cookie").split(";")[0].split("=")[1],
        ".hessen.de",
        "/",
    )

    next_step = response.headers.get("location")

    return cookies, next_step


def get_authentication_url(request: httpx.Client, cookies):
    response = request.head(URL.connect, cookies=cookies)

    next_page = response.headers.get("location")

    return next_page


def get_authentication_cookies(request: httpx.Client, url, cookies, school_id):
    response = request.head(url, cookies=cookies)

    cookies = httpx.Cookies()

    cookies.set("i", str(school_id))
    cookies.set(
        "sid",
        response.headers.get("set-cookie").split(";")[1].split(", ")[1].split("=")[1],
    )

    return cookies
