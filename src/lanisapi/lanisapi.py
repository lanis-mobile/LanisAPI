import calendar
import json
import logging
import os.path
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from functools import wraps
from typing import Optional
from urllib.parse import ParseResult, urlparse

import httpx
from selectolax.parser import HTMLParser

from .helpers.authentication import (
    get_authentication_data,
    get_authentication_url,
    get_session,
)
from .helpers.cryptor import Cryptor


class LanisClient:
    """The interface between python and Schulportal Hessen.

    Use ``authenticate()`` to use this interface.

    Parameters
    ----------
    school : str | School
        1. The id of the school which you can see it in the url at ``i=``.
        2. The school name and city in ``School``.
    username : str
        The username in firstname.lastname.
    password : str
        The password.
    save : bool, default True
        If False the school list and future things won't be saved to a file.
    ad_header : httpx.Headers, default {"user-agent": ....}
        Send custom headers to Lanis. Primarily used to send a
        custom ``user-agent``.
    """

    @dataclass
    class SubstitutionPlan:
        """The substitution plan page in a data type.

        Parameters
        ----------
        date : datetime.datetime
            Date of the substitution plan.
        data : list[SubstitutionData]
            The individual substitutions.
        info : str, optional
            ``info`` is the box with the title "Allgemein" that exists sometimes.
        """

        @dataclass
        class SubstitutionData:
            """The individual substitution data (table row).

            Parameters
            ----------
            substitute : str
                Often abbreviation of the substitute.
            teacher : str
                Often abbreviation of the teacher.
            hours : str
                When is it in school hours.
            class_name : str
                Name of the classes.
            subject : str
                The subject is rarely given.
            room : str
                Room of the substitution.
            notice : str
                More info about the substitution.
            """

            substitute: str
            teacher: str
            hours: str
            class_name: str
            subject: str
            room: str
            notice: str

        date: datetime
        data: list[SubstitutionData]
        info: Optional[str] = None

    @dataclass
    class Calendar:
        """The calendar page in a data type.

        Parameters
        ----------
        start : datetime.datetime
            Start date and time of the calendar.
        end : datetime.datetime
            End date and time of the calendar.
        data : list[CalendarData] or None
            Use data to access the most important properties.
            You need to use get_calendar(json=False) to get this.
        json : list[dict[str, any]] or None
            Use ``json`` to access all properties.
            You need to use get_calendar(json=True) to get this.
        """

        @dataclass
        class CalendarData:
            """Each calendar cell "event" data.

            Parameters
            ----------
            title : str
                Name of the event.
            description : str
                Description of the event.
            place : str
                Place of the event.
            start : datetime.datetime
                Start day and time of the event.
            end : datetime.datetime
                End day and time of the event.
                Could also exceed the calendars start and end.
            whole_day : bool
                Does it happen the whole day or only between a specific time.
            """

            title: str
            description: str
            place: str
            start: datetime
            end: datetime
            whole_day: bool

        start: datetime
        end: datetime
        data: list[CalendarData] = None
        json: list[dict[str, any]] = None

    @dataclass
    class School:
        """Alternative to school id for authentication.

        Parameters
        ----------
        name : str
            Full school name
        city : str
            City name sometimes with abbreviations or fully written.
        """

        name: str
        city: str

    @dataclass
    class TaskData:
        """The "Mein Unterricht" page in a data type.

        Parameters
        ----------
        title : str
            Name of the task.
        date : datetime.datetime
            Creation date of the task.
        subject_name : str
            Subject of the task often with the class name and weird ids at the end,
            like "Chemie 7GA (071CH01-GYM)"
        teacher : str
            Abbreviation of the teacher.
        description : str, optional
            Optional description of the task.
        details : str, optional
            ``details`` is the blue button with a comment symbol that sometimes appears.
        attachment : list[str], optional
            List of the attachments names.
        attachment_url : urllib.parse.ParseResult, optional
            Download link to a zip file containing all attachments.
        """

        title: str
        date: datetime
        subject_name: str
        teacher: str
        description: Optional[str] = None
        details: Optional[str] = None
        attachment: Optional[list[str]] = None
        attachment_url: Optional[ParseResult] = None

    def __init__(self,
                 school: str | School,
                 username: str,
                 password: str,
                 save: bool = True,
                 ad_header: httpx.Headers = None,
                 ) -> None:

        self.school = school
        self.username = username
        self.password = password

        self.save = save

        self.ad_header = ad_header if ad_header is not None else httpx.Headers({ "user-agent":
                        "LanisClient by kurwjan and contributors (https://github.com/kurwjan/LanisAPI/)" })

        self.parser = httpx.Client(headers=ad_header)

        self.authenticated = False
        self.logger = logging.getLogger("LanisClient")

        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s - %(name)s   %(message)s")

        self.logger.warning(
            "IMPORTANT: Schulportal Hessen can change things quickly"
            "and is fragmented (some schools work, some not),"
            "so expect something to not be working")

    def __del__(self) -> None:
        self.parser.close()

    def _get_substitution_info(self) -> dict[str, str]:
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        page = self.parser.get(url)
        html = HTMLParser(page.text)

        notice_element = html.css_first(
            ".infos > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1)"
            )

        if notice_element:
            notice = re.sub(r"^[\n][ \t]+|[\n][ \t]+$", "", notice_element)
        else:
            notice = ""

        date = re.findall(r"(\d\d\.\d\d\.\d\d\d\d)", html.html)[0]

        return {"notice": notice, "date": date}

    def requires_auth(self) -> any:
        @wraps(self)
        def decorated(*args, **kwargs):
            if not args[0].authenticated:
                args[0].logger.error("A2: Not authenticated.")
                return
            return self(*args, **kwargs)
        return decorated

    def close(self) -> None:
        """Close the client; you need to do this."""
        self.parser.close()
        self.authenticated = False

    def get_schools(self):
        """Return all schools with their id, name and city.

        Returns
        -------
        list[dict[str, str]]
            JSON
        """
        if os.path.exists("schools.json"):
            with open("schools.json", "r") as file:
                return json.load(file)

        url = "https://startcache.schulportal.hessen.de/exporteur.php"

        response = self.parser.get(url, params=httpx.QueryParams({"a": "schoollist"})).json()

        schools = []

        for group in response:
            for school in group["Schulen"]:
                schools.append(school)

        if self.save is True:
            with open("schools.json", "w") as file:
                    json.dump(schools, file)

        return schools

    def authenticate(self) -> None:
        """Log into the school portal and sets the session id in the auth_cookies."""
        if self.authenticated:
            self.logger.warning("A1: Already authenticated.")
            return

        school_id: int

        if isinstance(self.school, str):
            school_id = self.school
        else:
            schools = self.get_schools()

            try:
                school_id = next(school for school in schools if school["Name"] == self.school.name and school["Ort"] == self.school.city)["Id"]
            except StopIteration:
                self.logger.warning("E0: School doesn't exist check for right spelling.")
                return

        response_session = get_session(school_id, self.username,
                                       self.password,self.parser, self.ad_header)
        response_cookies = response_session["cookies"]

        if not response_session["location"]:
            self.logger.error("A3: Could not log in, possibly wrong credentials.")
            return

        auth_url = get_authentication_url(response_cookies, self.parser, self.ad_header)

        self.parser.cookies = get_authentication_data(auth_url, response_cookies,
                                                      self.parser, self.ad_header,
                                                      schoolid=school_id)

        self.authenticated = True

        self.logger.info("A0: Successfully authenticated.")

    @requires_auth
    def logout(self) -> None:
        """Log out."""
        url = "https://start.schulportal.hessen.de/index.php?logout=all"
        self.parser.get(url)
        self.authenticated = False
        self.logger.info("A4: Logged out.")

    @requires_auth
    def get_substitution_plan(self) -> SubstitutionPlan:
        """Return the whole substitution plan of the current day.

        Returns
        -------
        SubstitutionPlan
        """
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        info = self._get_substitution_info()
        data = {"ganzerPlan": "true", "tag": info["date"]}

        substitution_raw_data = self.parser.post(url, data=data)

        plan = self.SubstitutionPlan(
            datetime.strptime(info["date"], "%d.%m.%Y").date(), [])

        if info["notice"]:
            plan.info = info["notice"]

        for data in substitution_raw_data.json():
            substitution_data = self.SubstitutionPlan.SubstitutionData(
                substitute=data["Vertreter"],
                teacher=data["Lehrer"],
                hours=data["Stunde"],
                class_name=data["Klasse"],
                subject=data["Fach"],
                room=data["Raum"],
                notice=data["Hinweis"] if data["Hinweis"] else None,
            )

            plan.data.append(substitution_data)

        self.logger.info("B0: Successfully got substitution plan")

        return plan

    @requires_auth
    def get_calendar_of_month(self) -> Calendar:
        """Use the get_calendar() function but only returns all events of the current month.

        Returns
        -------
        Calendar
            Calendar type with CalendarData
        """
        today = date.today()

        _, last_day = calendar.monthrange(int(today.strftime("%Y")),
                                          int(today.strftime("%-m")))
        last_date = today.replace(day=last_day)
        first_date = today.replace(day=1)

        return self.get_calendar(first_date, last_date)

    @requires_auth
    def get_calendar(self, start: datetime,
                    end: datetime, json: bool = False) -> Calendar:
        """Return all calendar events between the start and end date.

        Parameters
        ----------
        start : datetime.datetime
            Start date
        end : datetime.datetime
            End date
        json : bool, default False
            Returns Json with every property instead of the limited CalendarData.
            Defaults to False.

        Returns
        -------
        Calendar
            Calendar type with CalendarData or Json.
        """
        url = "https://start.schulportal.hessen.de/kalender.php"
        data = {"f": "getEvents", "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d")}

        calendar_raw_data = self.parser.post(url, data=data)

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
                start=datetime.strptime(data["Anfang"], "%Y-%m-%d %H:%M:%S"),
                end=datetime.strptime(data["Ende"], "%Y-%m-%d %H:%M:%S"),
                whole_day=data["allDay"],
            )
            calendar.data.append(calendar_data)

        self.logger.info("C0: Successfully got calendar")

        return calendar

    @requires_auth
    def get_tasks(self) -> list[TaskData]:
        """Return all tasks from the "Mein Unterricht" page in .zip format.

        Returns
        -------
        list[TaskData]
        """
        url = "https://start.schulportal.hessen.de/meinunterricht.php"

        response = self.parser.get(url)

        html = HTMLParser(response.text)

        task_list = []
        for i in range(1, len(html.css("tr.printable")) + 1):
            element = html.css_first(f"tr.printable:nth-child({i})".format(i=i))

            title = element.css_first("td:nth-child(2) > b:nth-child(1)").text()

            first_date_element = element.css_first(
                "td:nth-child(2) > small:nth-child(2) > span:nth-child(1)")
            date_element = first_date_element.text() if first_date_element else element.css_first(
                "td:nth-child(2) > small:nth-child(3) > span:nth-child(1)").text()
            date = datetime.strptime(date_element, "%d.%m.%Y")

            description_element = element.css_first(
                "td:nth-child(2) > div:nth-child(4) > div:nth-child(4)")
            description = description_element.text() if description_element else None

            details_element = element.css_first("span.markup")
            details = details_element.text() if details_element else None

            subject_name = element.css_first(
                "td:nth-child(1) > h3:nth-child(1) > a:nth-child(1) > span:nth-child(2)"
                ).text()

            teacher = element.css_first(
                "td:nth-child(1) > span:nth-child(2) >"
                "div:nth-child(1) > button:nth-child(1)").attributes["title"]

            attachments = []

            first_attachment_elements = element.css(
                "td:nth-child(3) > div:nth-child(1) >"
                "div:nth-child(1) > ul:nth-child(2) > li")

            attachments_url: ParseResult = None

            if first_attachment_elements:
                attachments_url = urlparse(
                    first_attachment_elements[len(first_attachment_elements) - 1]
                    .css_first("a")
                    .attributes["href"])

                for i in range(len(first_attachment_elements) - 2):
                    attachments.append(first_attachment_elements[i]
                                       .css_first("a")
                                       .attributes["data-file"])

            second_attachment_elements = element.css(
                "div.files:nth-child(2) > ul:nth-child(2) > li")

            if second_attachment_elements:
                attachments_url = urlparse(
                    second_attachment_elements[len(second_attachment_elements) - 1]
                    .css_first("a")
                    .attributes["href"])

                for i in range(len(second_attachment_elements) - 2):
                    attachments.append(second_attachment_elements[i]
                                       .css_first("a")
                                       .attributes["data-file"])

            task_data = self.TaskData(
                title=title,
                date=date,
                subject_name=subject_name,
                teacher=teacher,
                description=description if description else None,
                details=details if details else None,
                attachment=attachments if attachments else None,
                attachment_url=attachments_url if attachments_url else None,
            )

            task_list.append(task_data)


        self.logger.info("D0: Successfully got tasks")

        return task_list

    def get_conversations_encrypted_data_test(self):
        cryptor = Cryptor(self.parser)

        secret = cryptor.generate_key()

        challenge = cryptor.handshake(cryptor.encrypt_key(secret, cryptor.get_public_key()))

        if cryptor.challenge(challenge, secret):
            print("bobr")

        url = "https://start.schulportal.hessen.de/nachrichten.php"

        response = self.parser.post(url,
                                    data={"a": "headers", "getType": "visibleOnly", "last": "0"},
                                    headers={
                                        "Sec-Fetch-Dest": "empty",
                                        "Sec-Fetch-Mode": "cors",
                                        "Sec-Fetch-Site": "same-origin",
                                        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
                                        "X-Requested-With": "XMLHttpRequest",
                                        },)

        big_data = response.json()["rows"]

        with open("encrpyted.json", "w") as file:
            file.write(cryptor.decrypt(big_data, secret))
