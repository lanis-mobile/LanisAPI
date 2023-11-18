"""This script includes classes and functions about the 'Mein Unterricht' page."""

from dataclasses import dataclass
from datetime import datetime
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from ..constants import LOGGER, URL
from ..exceptions import CriticalElementWasNotFoundError
from ..helpers.html_logger import HTMLLogger
from ..helpers.request import Request


@dataclass
class Task:
    """The "Mein Unterricht" page in a data type. Expect many parameters to be `None`.

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
    description : str
        Optional description of the task.
    details : str
        ``details`` is the blue button with a comment symbol that sometimes appears.
    attachment : list[str]
        List of the attachments names.
    attachment_url : str
        Download link to a zip file containing all attachments.
    """

    title: str
    date: datetime
    subject_name: str
    teacher: str
    description: str
    details: str
    attachment: list[str]
    attachment_url: str


def _get_tasks() -> list[Task]:
    """Return all tasks from the "Mein Unterricht" page with downloads in .zip format.

    Returns
    -------
    list[Task]
    """
    # Unfortunately there is no API for us.
    response = Request.get(URL.tasks)

    html = HTMLParser(response.text)

    elements = html.css("#aktuellTable tr.printable")

    # Parse page to get all tasks. Also report suspicious missing elements.
    task_list = []
    for element in elements:
        if not element:
            HTMLLogger.log_missing_element(
                html.html, "get_task()", elements.index(element), "element"
            )
            msg = "Critical task element was not found, something is definitely wrong! Please file a bug with the html_logs.txt file."
            raise CriticalElementWasNotFoundError(msg)

        # Name of task.
        title_element = element.css_first("b.thema")
        try:
            title = title_element.text()
        except AttributeError:
            LOGGER.warning(
                "Get tasks: No task name found, possibly wrong css selector? Please file a bug with the html_logs.txt file."
            )
            HTMLLogger.log_missing_element(
                element.html, "get_task()", elements.index(element), "title"
            )
            title = None

        # Date it was given.
        date_element = element.css_first("small span.datum")
        try:
            date = datetime.strptime(date_element.text(), "%d.%m.%Y")
        except AttributeError:
            LOGGER.warning(
                "Get tasks: No date found, possibly wrong css selector? Please file a bug with the html_logs.txt file."
            )
            HTMLLogger.log_missing_element(
                element.html, "get_task()", elements.index(element), "date"
            )
            date = None

        # Description, sometimes there is none, so maybe there is text under the details button.
        description_element = element.css_first("div.markup.text.realHomework")
        try:
            description = description_element.text()
        except AttributeError:
            description = None

        # Details, hidden under the the blue button with the message symbol.
        details_element = element.css_first("div.inhalt span.markup")
        try:
            details = details_element.text()
        except AttributeError:
            details = None

        # Subject (with weird suffixes sometimes).
        subject_element = element.css_first("h3 span")
        try:
            subject = subject_element.text()
        except AttributeError:
            LOGGER.warning(
                "Get tasks: No subject name found, possibly wrong css selector? Please file a bug with the html_logs.txt file."
            )
            HTMLLogger.log_missing_element(
                element.html, "get_task()", elements.index(element), "subject"
            )
            subject = None

        # Teacher
        teacher_element = element.css_first("span.teacher button")
        try:
            teacher = teacher_element.attributes["title"]
        except AttributeError:
            LOGGER.warning(
                "Get tasks: No teacher name found, possibly wrong css selector? Please file a bug with the html_logs.txt file."
            )
            HTMLLogger.log_missing_element(
                element.html, "get_task()", elements.index(element), "teacher"
            )
            teacher = None

        # List of all attachment names.
        attachments = []
        attachment_elements = element.css("a.file")
        for attachment_element in attachment_elements:
            attachments.append(attachment_element.attributes["data-file"])

        # The url of a zip containing all attachments.
        attachment_url_element = element.css_first(
            "div.btn-group.files ul.dropdown-menu li:last-child a"
        )
        try:
            attachment_url = urljoin(
                URL.base, attachment_url_element.attributes["href"]
            )
        except AttributeError:
            attachment_url = None

        # Map everything together to `Task`.
        task_data = Task(
            title=title,
            date=date,
            subject_name=subject,
            teacher=teacher,
            description=description,
            details=details,
            attachment=attachments,
            attachment_url=attachment_url,
        )

        task_list.append(task_data)

    LOGGER.info("Get tasks: Successfully got tasks.")

    return task_list
