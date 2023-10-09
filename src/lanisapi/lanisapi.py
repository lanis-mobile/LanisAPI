from typing import Optional
import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass
from urllib.parse import urlparse, ParseResult
import logging
from functools import wraps
import re
from datetime import datetime, date
import calendar

from .authentication_functions import get_authentication_data, get_authentication_url, get_session

class LanisClient:
    """
    The interface between python and Schulportal Hessen.
    
    ### Parameters
    -------
    1. schoolid : ``string``
        - The id of the school which you can see it in the url at ``i=``.
    2. username : ``string``
        - The username in ``firstname.lastname``.
    3. password : ``string``
        -  The password.
    4. ad_header : ``httpx.Headers``
        - Send custom headers to Lanis. Primarily used to send a
          custom ``user-agent``.
    """
    
    authenticated = False
    logger = logging.getLogger("LanisClient")
    
    @dataclass
    class SubstitutionPlan:
        """
        #### The substitution plan page in a data type.
        Use ``data`` to access the data.
        
        ``info`` is the box with the title "Allgemein" that exists sometimes.
        """
        
        @dataclass
        class SubstitutionData:
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
        """
        #### The calendar page in a data type.
        Use ``data`` to access the most important properties.
        Use ``json`` to access all properties.
        
        Don't forget that ``start`` and ``end`` can also include hours and minutes.
        """
        
        @dataclass
        class CalendarData:
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
    class TaskData:
        """
        #### The "Mein Unterricht" page in a data type.
        
        ``details`` is the blue button with a comment symbol that sometimes appears.
        """
        
        title: str
        date: datetime
        subject_name: str
        teacher: str
        description: Optional[str] = None
        details: Optional[str] = None
        attachment: Optional[list[str]] = None
        attachment_url: Optional[ParseResult] = None

    def requires_auth(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            if not args[0].authenticated:
                args[0].logger.error("A2: Not authenticated.")
                return
            return f(*args, **kwargs)
        return decorated

    def __init__(self,
                 schoolid: str,
                 username: str,
                 password: str,
                 ad_header: httpx.Headers = 
                 httpx.Headers({ "user-agent": 
                     "LanisClient by kurwjan and contributors (https://github.com/kurwjan/LanisAPI/)" })
                 ) -> None:
        
        self.schoolid = schoolid
        self.username = username
        self.password = password
        
        self.ad_header = ad_header
        
        self.parser = httpx.Client(headers=ad_header)
        
        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s - %(name)s   %(message)s")
    
        self.logger.warning(
            "IMPORTANT: Schulportal Hessen can change things quickly"
            "and is fragmented (some schools work, some not),"
            "so expect something to not be working")

    def __del__(self) -> None:
        self.parser.close()
        
    def close(self) -> None:
        self.parser.close()
        self.authenticated = False
        

    def authenticate(self) -> None:
        """
        #### This function must be executed once to use other functions.
        
        Logs into the school portal and sets the session id in the auth_cookies.
        """
        
        if self.authenticated:
            self.logger.warning("A1: Already authenticated.")
            return;

        response_session = get_session(self.schoolid, self.username,
                                       self.password,self.parser, self.ad_header)
        response_cookies = response_session["cookies"]
    
        if not response_session["location"]:
            self.logger.error("A3: Could not log in, possibly wrong credentials.")
            return
    
        auth_url = get_authentication_url(response_cookies, self.parser, self.ad_header)
        
        self.parser.cookies = get_authentication_data(auth_url, response_cookies,
                                                      self.parser, self.ad_header)

        self.authenticated = True

        self.logger.info("A0: Successfully authenticated.")

    def __get_substitution_info__(self) -> dict[str, str]:
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
        
        date = re.findall("(\d\d\.\d\d\.\d\d\d\d)", html.html)[0]

        return {"notice": notice, "date": date}
    
    @requires_auth
    def logout(self) -> None:
        """
        Logs out.
        """
        
        url = "https://start.schulportal.hessen.de/index.php?logout=all"
        self.parser.get(url)
        self.authenticated = False
        self.logger.info("A4: Logged out.")

    @requires_auth
    def get_substitution_plan(self) -> SubstitutionPlan:
        """
        Returns the whole substitution plan of the current day.

        ### Returns
        -------
        - ``SubstitutionPlan``
        """
        
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        info = self.__get_substitution_info__()
        data = {"ganzerPlan": "true", "tag": info["date"]}

        substitution_raw_data = self.parser.post(url, data=data)

        plan = self.SubstitutionPlan(
            datetime.strptime(info["date"], '%d.%m.%Y').date(), [])
        
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
        """
        Uses the get_calendar() function but only returns all events of the current month.

        ### Returns
        -------
        - ``Calendar``
            -  Calendar type with CalendarData
        """
        
        today = date.today()

        _, last_day = calendar.monthrange(int(today.strftime('%Y')),
                                          int(today.strftime('%-m')))
        last_date = today.replace(day=last_day)
        first_date = today.replace(day=1)

        return self.get_calendar(first_date, last_date)
    
    @requires_auth
    def get_calendar(self, start: datetime,
                    end: datetime, json: bool = True) -> Calendar:
        """
        Returns all calendar events between the start and end date.

        ### Parameters
        -------
        1. start : ``datetime``
            - Start date
        2. end : ``datetime``
            - End date
        3. json : ``datetime, optional``
            -   Returns Json with every property instead of the limited CalendarData.
                Defaults to True.

        ### Returns
        -------
        - ``Calendar``
            - Calendar type with CalendarData or Json.
        """
        
        url = "https://start.schulportal.hessen.de/kalender.php"
        data = {"f": "getEvents", "start": start.strftime('%Y-%m-%d'),
                "end": end.strftime('%Y-%m-%d')}

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
                start=datetime.strptime(data["Anfang"], '%Y-%m-%d %H:%M:%S'),
                end=datetime.strptime(data["Ende"], '%Y-%m-%d %H:%M:%S'),
                whole_day=data["allDay"],
            )
            calendar.data.append(calendar_data)

        self.logger.info("C0: Successfully got calendar")

        return calendar
    
    @requires_auth
    def get_tasks(self) -> list[TaskData]:
        """
        Returns all tasks from the "Mein Unterricht" page 
        also with the download link of all attachments in .zip format.

        ### Returns
        -------
        - ``list[TaskData]``
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
            date = datetime.strptime(date_element, '%d.%m.%Y')

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

                for i in range(0, len(first_attachment_elements) - 2):
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

                for i in range(0, len(second_attachment_elements) - 2):
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
