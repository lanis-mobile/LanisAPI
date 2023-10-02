import httpx

ad_header = { "user-agent": "LanisClient by kurwjan and contributors (soon on github)" }

def get_session(schoolid, username, password):
    url = "https://login.schulportal.hessen.de/"
    params = { "i": schoolid }
    data = {
        "user2": username,
        "user": "{schoolid}.{username}".format(schoolid=schoolid, username=username),
        "password": password,
        }
    response = httpx.post(url, headers=ad_header, data=data, params=params)

    cookies = httpx.Cookies()
    cookies.set(
        "SPH-Session",
        response.headers.get("set-cookie").split(";")[0].split("=")[1],
        ".hessen.de",
        "/",
        )

    location = response.headers.get("location")

    return {"cookies": cookies, "location": location}

def get_authentication_url(cookies):
    url = "https://connect.schulportal.hessen.de/"
    response = httpx.get(url, cookies=cookies, headers=ad_header) 

    auth_url = response.headers.get("location")

    return auth_url

def get_authentication_data(url, cookies):
    response = httpx.get(url, cookies=cookies, headers=ad_header)

    cookies = httpx.Cookies()

    cookies.set("i", "6091")
    cookies.set("sid", response.headers.get("set-cookie").split(";")[2].split(", ")[1].split("=")[1])

    return cookies