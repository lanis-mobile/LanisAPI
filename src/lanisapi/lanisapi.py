import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urlparse
import logging
from functools import wraps
import re
from datetime import datetime, date
import calendar

from .authentication_functions import get_authentication_data, get_authentication_url, get_session

class LanisClient:
    authenticated = False
    auth_cookies = httpx.Cookies
    logger = logging.getLogger("LanisClient")
    ad_header = { "user-agent": "LanisClient by kurwjan and contributors (https://github.com/kurwjan/LanisAPI/)" }
    
    @dataclass
    class SubstitutionPlan:
        class SubstitutionData:
            substitute: str
            teacher: str
            hours: str
            class_name: str
            subject: str
            room: str
            notice: str

        info: str
        date: datetime
        data: list[SubstitutionData]

    @dataclass
    class Calendar:
        @dataclass
        class CalendarData:
            title: str
            description: str
            place: str
            start: datetime
            end: datetime
            all_day: bool
        
        start: datetime
        end: datetime
        data: list[CalendarData] = None
        json: list[dict[str]] = None

    @dataclass
    class TaskData:
        class AttachmentDownload:
            def __init__(self, url, cookies, ad_header):
                self.url = url
                self.cookies = cookies
                self.ad_header = ad_header

            def download(self) -> httpx.Response:
                return httpx.get("https://start.schulportal.hessen.de/meinunterricht.php", params=self.url.query, cookies=self.cookies, headers=self.ad_header)
        
        title: str
        description: str
        #details: str
        date: datetime
        subject_name: str
        teacher: str
        attachment: list[str]
        attachment_url: AttachmentDownload

    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not args[0].authenticated:
                args[0].logger.error("A2: Not authenticated.")
                return
            return f(*args, **kwargs)
        return decorated

    def __init__(self, schoolid: str, username: str, password: str) -> None:
        self.schoolid = schoolid
        self.username = username
        self.password = password
        logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s   %(message)s")
        self.logger.warning("IMPORTANT: Schulportal Hessen can change things quickly and is fragmented (some schools work, some not), so expect something to not be working")

    def authenticate(self) -> None:
        if self.authenticated:
            self.logger.warning("A1: Already authenticated.")
            return;

        response_session = get_session(self.schoolid, self.username, self.password)
        response_cookies = response_session["cookies"]
    
        if not response_session["location"]:
            self.logger.error("A3: Could not log in, possibly wrong credentials.")
            return
    
        auth_url = get_authentication_url(response_cookies)

        self.auth_cookies = get_authentication_data(auth_url, response_cookies)

        self.authenticated = True

        self.logger.info("A0: Successfully authenticated.")

    def _get_substitution_info(self) -> dict[str, str]:
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        page = httpx.get(url, cookies=self.auth_cookies, headers=self.ad_header)
        html = HTMLParser(page.text)

        notice = re.sub(r"^[\n][ \t]+|[\n][ \t]+$", "", html.css_first(".infos > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1)").text())
        date = re.findall("(\d\d.\d\d.\d\d\d\d)", html.css_first("h3.hidden-xs").text())[0]

        return {"notice": notice, "date": date}
    
    @requires_auth
    def logout(self) -> None:
        url = "https://start.schulportal.hessen.de/index.php?logout=all"
        httpx.get(url, cookies=self.auth_cookies, headers=self.ad_header)
        self.authenticated = False
        self.logger.info("A4: Logged out.")

    @requires_auth
    def get_substitution_plan(self) -> SubstitutionPlan:
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        info = self._get_substitution_info()
        data = {"ganzerPlan": "true", "tag": info["date"]}

        substitution_raw_data = httpx.post(url, data=data, cookies=self.auth_cookies, headers=self.ad_header)

        plan = self.SubstitutionPlan(info["notice"], datetime.strptime(info["date"], '%d.%m.%Y').date(), [])
        for data in substitution_raw_data.json():
            substitution_data = self.SubstitutionPlan.SubstitutionData(
                substitute=data["Vertreter"],
                teacher=data["Lehrer"],
                hours=data["Stunde"],
                class_name=data["Klasse"],
                subject=data["Fach"],
                room=data["Raum"],
                notice=data["Hinweis"],
            )
            plan.data.append(substitution_data)

        self.logger.info("B0: Successfully got substitution plan")

        return plan
    
    @requires_auth
    def get_calendar_of_month(self) -> Calendar:
        today = date.today()

        _, last_day = calendar.monthrange(int(today.strftime('%Y')), int(today.strftime('%-m')))
        last_date = today.replace(day=last_day).strftime("%Y-%m-%d")
        first_date = today.replace(day=1).strftime("%Y-%m-%d")

        return self.get_calendar(first_date, last_date)
    
    @requires_auth
    def get_calendar(self, start: datetime, end: datetime, json: bool = True) -> Calendar:
        url = "https://start.schulportal.hessen.de/kalender.php"
        data = {"f": "getEvents", "start": start.strftime('%Y-%m-%d'), "end": end.strftime('%Y-%m-%d')}

        calendar_raw_data = httpx.post(url, data=data, headers=self.ad_header, cookies=self.auth_cookies)
        
        if json:
            calendar = self.Calendar(start, end, json=[])
            for data in calendar_raw_data.json():
                calendar.json.append(data)
            
            self.logger.info("C1: Successfully got calendar in JSON format")
            
            return calendar

        calendar = self.Calendar(start, end, data=[])
        for data in calendar_raw_data.json():
            calendar_data = self.Calendar.CalendarData(
                title=data["title"],
                description=data["description"],
                place=data["Ort"],
                start=datetime.strptime(data["Anfang"], '%Y-%m-%d %H:%M:%S'),
                end=datetime.strptime(data["Ende"], '%Y-%m-%d %H:%M:%S'),
                all_day=data["allDay"],
            )
            calendar.data.append(calendar_data)

        self.logger.info("C0: Successfully got calendar")

        return calendar
    
    @requires_auth
    def get_tasks(self) -> list[TaskData]:
        url = "https://start.schulportal.hessen.de/meinunterricht.php"

        response = httpx.get(url, headers=self.ad_header, cookies=self.auth_cookies)

        html = HTMLParser(response.text)

        task_list = []
        for i in range(1, len(html.css("tr.printable")) + 1):
            element = html.css_first("tr.printable:nth-child({i})".format(i=i))

            title = element.css_first("td:nth-child(2) > b:nth-child(1)").text()

            first_date_element = element.css_first("td:nth-child(2) > small:nth-child(2) > span:nth-child(1)")
            date_element = first_date_element.text() if first_date_element else element.css_first("td:nth-child(2) > small:nth-child(3) > span:nth-child(1)").text()
            date = datetime.strptime(date_element, '%d.%m.%Y')

            description_element = element.css_first("td:nth-child(2) > div:nth-child(4) > div:nth-child(4)")
            description = description_element.text() if description_element else ""

            subject_name = element.css_first("td:nth-child(1) > h3:nth-child(1) > a:nth-child(1) > span:nth-child(2)").text()
            teacher = element.css_first("td:nth-child(1) > span:nth-child(2) > div:nth-child(1) > button:nth-child(1)").attributes["title"]

            attachments = []

            first_attachment_elements = element.css("td:nth-child(3) > div:nth-child(1) > div:nth-child(1) > ul:nth-child(2) > li")

            attachment_url: tuple

            if first_attachment_elements:
                attachment_url = urlparse(first_attachment_elements[len(first_attachment_elements) - 1].css_first("a").attributes["href"])

                for i in range(0, len(first_attachment_elements) - 2):
                    attachments.append(first_attachment_elements[i].css_first("a").attributes["data-file"])

            second_attachment_elements = element.css("div.files:nth-child(2) > ul:nth-child(2) > li")

            if second_attachment_elements:
                attachment_url = urlparse(second_attachment_elements[len(second_attachment_elements) - 1].css_first("a").attributes["href"])

                for i in range(0, len(second_attachment_elements) - 2):
                    attachments.append(second_attachment_elements[i].css_first("a").attributes["data-file"])
                    
            task_list.append(self.TaskData(
                title=title,
                description=description,
                date=date,
                subject_name=subject_name,
                teacher=teacher,
                attachment=attachments,
                attachment_url=self.TaskData.AttachmentDownload(attachment_url, self.auth_cookies, self.ad_header),
            ))

        self.logger.info("D0: Successfully got tasks")

        return task_list