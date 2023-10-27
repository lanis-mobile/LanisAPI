import calendar
import json
import logging
import os.path
import re
from dataclasses import dataclass
from datetime import date, datetime
from functools import wraps
from typing import Optional
from urllib.parse import ParseResult, urlparse

import httpx
from selectolax.parser import HTMLParser

from .helpers.authentication import (
    get_authentication_sid,
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

    @dataclass
    class ConversationData:
        id: str
        title: str
        teacher: str
        creation_date: datetime
        newest_date: datetime
        unread: bool
        special_receivers: list[str]
        receivers: list[str]
        content: str
        comments = None

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

        self.client = httpx.Client(headers=ad_header, timeout=httpx.Timeout(30.0, connect=60.0))

        self.authenticated = False

        self.logger = logging.getLogger("LanisClient")

        logging.basicConfig(
            level=logging.INFO, format="%(levelname)s - %(name)s   %(message)s")

        self.cryptor = Cryptor(self.client, self.logger)

        self.logger.warning(
            "IMPORTANT: Schulportal Hessen can change things quickly"
            "and is fragmented (some schools work, some not),"
            "so expect something to not be working")

    def __del__(self) -> None:
        """If the script closes close the parser."""
        self.client.close()

    def _get_substitution_info(self) -> dict[str, str]:
        """Return the notice (if available) and date of the substitution plan.

        Returns
        -------
        dict[str, str]
            The data
        """
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        page = self.client.get(url)
        html = HTMLParser(page.text)

        notice_element = html.css_first(
            ".infos > tbody:nth-child(1) > tr:nth-child(2) > td:nth-child(1)"
            )

        if notice_element:
            # Remove whitespace at the beginning and end.
            notice = re.sub(r"^[\n][ \t]+|[\n][ \t]+$", "", notice_element.text())
        else:
            notice = ""

        date = re.findall(r"(\d\d\.\d\d\.\d\d\d\d)", html.html)[0]

        self.logger.info(f"Substitution info: Successfully got info. Notice is {bool(notice)}.")

        return {"notice": notice, "date": date}

    def requires_auth(function) -> any:
        """Check if the client is authenticated and returns the function if true."""
        @wraps(function)
        def check_authenticated(*args: tuple, **kwargs: dict[str, any]) -> any:
            if not args[0].authenticated:
                args[0].logger.error("Not authenticated.")
                return None
            return function(*args, **kwargs)
        return check_authenticated

    def close(self) -> None:
        """Close the client; you need to do this."""
        self.client.close()
        self.authenticated = False
        self.logger.info("Closed current session.")

    def get_schools(self) -> list[dict[str, str]]:
        """Return all schools with their id, name and city.

        Returns
        -------
        list[dict[str, str]]
            JSON
        """
        # If schools.json was already created, just read it.
        if os.path.exists("schools.json"):
            with open("schools.json", "r") as file:
                return json.load(file)

        url = "https://startcache.schulportal.hessen.de/exporteur.php"

        # `a`: `schoollist` = just means to get the schoollist.
        response = self.client.get(url, params={"a": "schoollist"}).json()

        schools = []

        # We don't want the categories only the schools.
        for group in response:
            for school in group["Schulen"]:
                schools.append(school)

        if self.save is True:
            with open("schools.json", "w") as file:
                    json.dump(schools, file)

        self.logger.info("Get schools: Successfully got schools.")

        return schools

    def authenticate(self) -> None:
        """Log into the school portal and sets the session id in the auth_cookies.

        Note
        ----
        Supports only the new system (login.schulportal.hessen.de).
        """
        if self.authenticated:
            self.logger.warning("A1: Already authenticated.")
            return

        school_id: int

        # Check if a id or school and place is provided.
        if isinstance(self.school, str):
            school_id = self.school
        else:
            schools = self.get_schools()

            try:
                school_id = next(school for school in schools if school["Name"] == self.school.name and school["Ort"] == self.school.city)["Id"]
            except StopIteration:
                self.logger.warning("Authenticate: School doesn't exist, check for right spelling.")
                return

        # Get new session (value: SPH-Session) by posting to login page.
        response_session = get_session(school_id, self.username,
                                       self.password, self.client,
                                       self.ad_header, self.logger)
        response_cookies = response_session["cookies"]

        if not response_session["location"]:
            # It also could be other problems, Lanis can be very finicky.
            self.logger.error("Authenticate: Could not log in, possibly wrong credentials.")
            return

        # Get authentication url to get sid.
        auth_url = get_authentication_url(response_cookies, self.client,
                                          self.ad_header, self.logger)

        # Get sid.
        self.client.cookies = get_authentication_sid(auth_url, response_cookies,
                                                      self.client, self.ad_header,
                                                      self.logger, schoolid=school_id)

        # Tell Lanis how to encrypt
        if not self.cryptor.authenticate():
            self.logger.error("Authenticate: Couldn't handshake with Lanis.")
            return

        self.authenticated = True

        self.logger.info("Authenticated.")

    @requires_auth
    def logout(self) -> None:
        """Log out.

        Note
        ----
        For closing the current LanisClient use `close()`
        """
        url = "https://start.schulportal.hessen.de/index.php?logout=all"
        self.client.get(url)
        self.authenticated = False
        self.logger.info("Logged out.")

    @requires_auth
    def get_substitution_plan(self) -> SubstitutionPlan:
        """Return the whole substitution plan of the current day.

        Returns
        -------
        SubstitutionPlan
        """
        url = "https://start.schulportal.hessen.de/vertretungsplan.php"
        info = self._get_substitution_info()

        # Script: /module/vertretungsplan/js/my.js

        # `ganzerPlan` = If you want the entire plan or only stuff for you.
        #                Recommended is the entire plan because the creators of the
        #                plan can mess up.
        # `tag` = The day of the plan, often there are plans for the current and next day.
        # `kuerzel`: `Abbreviation of substitution` = Which substitution should be shown?

        ### `a` function param:
        # `a`: `my` = Does nothing, "standard" function.
        #      `protokoll` = Returns: {"status":-1,"statustext":"Kein Zugriff!"}, used to create substitution plans.

        data = {"ganzerPlan": "true", "tag": info["date"]}

        # Lanis also adds the param `a`: `my` but it does nothing.
        substitution_raw_data = self.client.post(url, data=data)

        plan = self.SubstitutionPlan(
            datetime.strptime(info["date"], "%d.%m.%Y").date(), [])

        if info["notice"]:
            plan.info = info["notice"]

        # Map JSON to SubstitutionData.
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

        self.logger.info("Get substitution plan: Success.")

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

        # calendar.monthrange returns two days (current and last).
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

        # `f` Functions ### Associated script = /module/kalender/js/kalender.js

        ### Getting all events.
        # `f`: `getEvents` = We want all events in JSON format.
        # `start` = From when do we want to start getting events, also includes events that start earlier then `start`.
        #           Format: Year-Month-Day - 2023-10-30
        # `end` = Like start but ending date, also includes events that end later then `end`.

        #-- Unknown:
        # `year` = ? Maybe which period?
        # `k` = ? category ($('#kategorie').val())
        # `s` = ? search ($('#search').val())
        # `z` = ? zielgruppe > target group ($('#zielgruppe').val())
        # `u` = ? $('#ansichten').data('selected')};

        ### Getting single event (Unknown):
        # `f`: `getEvent` = Get details from a single event.
        # `id` = The id of the event.
        # `u` = ? $('#ansichten').data('selected')};

        # There are also other `f` functions.
        # There are also `a` functions like `export` for PDFs.

        data = {"f": "getEvents", "start": start.strftime("%Y-%m-%d"),
                "end": end.strftime("%Y-%m-%d")}

        calendar_raw_data = self.client.post(url, data=data)

        # Just lazily return JSON.
        if json:
            calendar = self.Calendar(start, end, json=[])
            for data in calendar_raw_data.json():
                calendar.json.append(data)

            self.logger.info("Get calendar: Successfully got calendar in JSON format.")

            return calendar

        # Get JSON and map it to `CalendarData` data class.
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

        self.logger.info("Get calendar: Successfully got calendar.")

        return calendar

    @requires_auth
    def get_tasks(self) -> list[TaskData]:
        """Return all tasks from the "Mein Unterricht" page in .zip format.

        Returns
        -------
        list[TaskData]
        """
        # Unfortunately there are no APIs for us.
        url = "https://start.schulportal.hessen.de/meinunterricht.php"

        response = self.client.get(url)

        html = HTMLParser(response.text)

        # Parse page to get all tasks.
        task_list = []
        for i in range(1, len(html.css("tr.printable")) + 1):
            element = html.css_first(f"tr.printable:nth-child({i})".format(i=i))

            # Name of task.
            title = element.css_first("td:nth-child(2) > b:nth-child(1)").text()

            # Date it was given.
            first_date_element = element.css_first(
                "td:nth-child(2) > small:nth-child(2) > span:nth-child(1)")
            date_element = first_date_element.text() if first_date_element else element.css_first(
                "td:nth-child(2) > small:nth-child(3) > span:nth-child(1)").text()
            date = datetime.strptime(date_element, "%d.%m.%Y")

            # Description, sometimes there is none, so maybe there is text under the details button.
            description_element = element.css_first(
                "td:nth-child(2) > div:nth-child(4) > div:nth-child(4)")
            description = description_element.text() if description_element else None

            # Details, hidden under the the blue button with the message symbol.
            details_element = element.css_first("span.markup")
            details = details_element.text() if details_element else None

            # Subject (with weird suffixes sometimes).
            subject_name = element.css_first(
                "td:nth-child(1) > h3:nth-child(1) > a:nth-child(1) > span:nth-child(2)"
                ).text()

            # Teacher
            teacher = element.css_first(
                "td:nth-child(1) > span:nth-child(2) >"
                "div:nth-child(1) > button:nth-child(1)").attributes["title"]

            # List of all attachment names.
            attachments = []
            attachment_elements = element.css("td > .btn-group-vertical > .files > .dropdown-menu > li > a.file")
            for attachment_element in attachment_elements:
                attachments.append(attachment_element.attributes["data-file"])

            # The url of a zip containing all attachments.
            attachment_url_element = element.css("td > .btn-group-vertical > .files > .dropdown-menu > li > a")
            try:
                attachment_url = attachment_url_element[len(attachment_url_element)].attributes["href"]
            except IndexError:
                attachment_url = None

            # Map everything together to `TaskData`.
            task_data = self.TaskData(
                title=title,
                date=date,
                subject_name=subject_name,
                teacher=teacher,
                description=description if description else None,
                details=details if details else None,
                attachment=attachments if attachments else None,
                attachment_url=attachment_url if attachment_url else None,
            )

            task_list.append(task_data)


        self.logger.info("Get tasks: Successfully got tasks.")

        return task_list

    ### TEST # TEST # TEST # TEST ###
    def get_conversations_encrypted_data_test(self):
        cryptor = Cryptor(self.client, self.logger)

        if cryptor.authenticate():
            print("bobr")
        else:
            print("not bobr")
            return

        url = "https://start.schulportal.hessen.de/nachrichten.php"

        # script: /module/nachrichten/js/start.js
        response = self.client.post(url,
                                    data={"a": "headers", "getType": "visibleOnly", "last": "0"},
                                    headers={"X-Requested-With": "XMLHttpRequest"},
                                    )

        big_data = response.json()["rows"]

        with open("encrpyted.json", "w") as file:
            file.write(cryptor.decrypt(big_data))

    ### TEST # TEST # TEST # TEST ###
    def get_single_conversation_test(self):
        cryptor = Cryptor(self.client, self.logger)

        cryptor.authenticate()

        url = "https://start.schulportal.hessen.de/nachrichten.php"

        id = "a4c62f2f39b528a3bed37ac8895da3a3-16929c0a-6ce0-476a-8d76-8aa57ca7060a"

        response = self.client.post(url,
                                    data={"a": "read", "uniqid": cryptor.encrypt(id)},
                                    params={"a": "read", "msg": id},
                                    headers={"X-Requested-With": "XMLHttpRequest"},
                                    )

        data = response.json()

        print(cryptor.decrypt(data["message"]))

    def _get_single_conversation(self, id: str) -> dict[str, any]:
        """Get creation date and content of the conversation.

        Parameters
        ----------
        id : str
            The `Uniquid`. Cool typo.

        Returns
        -------
        dict[str, any]
            The data.

        Todo
        ----
        Get comments.
        """
        url = "https://start.schulportal.hessen.de/nachrichten.php"

        single_message_response = self.client.post(url,
                                data={"a": "read", "uniqid": self.cryptor.encrypt(id)},
                                params={"a": "read", "msg": id},
                                headers={"X-Requested-With": "XMLHttpRequest"},
                                )

        single_message = json.loads(self.cryptor.decrypt(single_message_response.json()["message"]))

        creation_date = datetime.strptime(single_message["Datum"], "%d.%m.%Y %H:%M")

        content = HTMLParser(single_message["Inhalt"]).text()

        self.logger.info("Get single conversation: Success.")

        return {"creation_date": creation_date, "content": content}

    def get_conversations(self, number: int = 5) -> list[ConversationData]:
        """Return conversations from the "Nachrichten - Beta-Version".

        Parameters
        ----------
        number : int, optional
            The number of conversations to return, by default 5. To get all conversations use -1 but this will take a while and spam Lanis servers.

        Returns
        -------
        list[ConversationData]
            The conversations in ConversationData.
        """
        url = "https://start.schulportal.hessen.de/nachrichten.php"

        response = self.client.post(url,
                            data={"a": "headers", "getType": "visibleOnly", "last": "0"},
                            headers={"X-Requested-With": "XMLHttpRequest"},
                            )

        parsed_response: dict[str, any] = response.json()

        parsed_conversations: list[dict[str, any]] = json.loads(self.cryptor.decrypt(parsed_response["rows"]))

        conversations_list: list[self.ConversationData] = []

        if number == -1:
            number = parsed_response["total"]

        for i in range(number):

            parsed_conversation = parsed_conversations[i]

            # Get full teacher name
            parsed_teacher = HTMLParser(parsed_conversation["SenderName"]).text()

            teacher = None

            # Sometimes there is just " , " for some reason so we need to get rid of it.
            if parsed_teacher != " , ":
                teacher = HTMLParser(parsed_conversation["SenderName"]).text().strip()

            # Get special receivers
            special_receivers = None
            try:
                if parsed_conversation["WeitereEmpfaenger"]:
                    special_receivers = HTMLParser(parsed_conversation["WeitereEmpfaenger"]).text().strip().split("   ")
            except (IndexError, KeyError):
                # Just skip if none are found.
                pass

            # Get all receivers
            receivers = []

            for receiver in parsed_conversation["empf"]:
                parsed_receiver = HTMLParser(receiver).text().strip()

                # Sometimes receivers are empty so we need to skip them.
                if parsed_receiver:
                    receivers.append(parsed_receiver)

            single_message_data = self._get_single_conversation(parsed_conversation["Uniquid"])

            conversation = self.ConversationData(
                id=parsed_conversation["Uniquid"],
                title=parsed_conversation["Betreff"],
                teacher=teacher,
                creation_date=single_message_data["creation_date"],
                newest_date=datetime.strptime(parsed_conversation["Datum"], "%d.%m.%Y %H:%M"),
                unread=bool(parsed_conversation["unread"]),
                special_receivers=special_receivers,
                receivers=receivers,
                content=single_message_data["content"],
            )

            conversations_list.append(conversation)

        return conversations_list
