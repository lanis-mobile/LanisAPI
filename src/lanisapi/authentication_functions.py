import httpx

def get_session(schoolid: str,
                username: str,
                password: str,
                parser: httpx.Client,
                ad_header: httpx.Headers
                ) -> dict[str, any]:
    
    url = "https://login.schulportal.hessen.de/"
    params = { "i": schoolid }
    data = {
        "user2": username,
        "user": "{schoolid}.{username}".format(schoolid=schoolid, username=username),
        "password": password,
        }
    response = parser.post(url, headers=ad_header, data=data, params=params)

    cookies = httpx.Cookies()
    cookies.set(
        "SPH-Session",
        response.headers.get("set-cookie").split(";")[0].split("=")[1],
        ".hessen.de",
        "/",
        )

    location = response.headers.get("location")

    return {"cookies": cookies, "location": location}

def get_authentication_url(
    cookies: httpx.Cookies,
    parser: httpx.Client,
    ad_header: httpx.Headers
    ) -> str:
    
    url = "https://connect.schulportal.hessen.de/"
    response = parser.get(url, cookies=cookies, headers=ad_header) 

    auth_url = response.headers.get("location")

    return auth_url

def get_authentication_data(url: str,
                            cookies: httpx.Cookies,
                            parser: httpx.Client,
                            ad_header: httpx.Headers
                            ) -> httpx.Cookies:
    
    response = parser.get(url, cookies=cookies, headers=ad_header)

    cookies = httpx.Cookies()

    cookies.set("i", "6091")
    cookies.set("sid",
                response.headers
                .get("set-cookie")
                .split(";")[2]
                .split(", ")[1]
                .split("=")[1])

    return cookies