"""This script includes classes and functions about the 'Mein Unterricht' page."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from urllib.parse import urljoin

from selectolax.parser import HTMLParser

from ..constants import LOGGER, URL
from ..helpers.request import Request


@dataclass
class Task:
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
    attachment_url : str, optional
        Download link to a zip file containing all attachments.
    """

    title: str
    date: datetime
    subject_name: str
    teacher: str
    description: Optional[str] = None
    details: Optional[str] = None
    attachment: Optional[list[str]] = None
    attachment_url: Optional[str] = None


def _get_tasks() -> list[Task]:
    """Return all tasks from the "Mein Unterricht" page in .zip format.

    Returns
    -------
    list[Task]
    """
    # Unfortunately there are no APIs for us.
    response = Request.get(URL.tasks)

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
            attachment_url = urljoin(URL.base, attachment_url_element[len(attachment_url_element) - 1].attributes["href"])
        except IndexError:
            attachment_url = None

        # Map everything together to `Task`.
        task_data = Task(
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

    LOGGER.info("Get tasks: Successfully got tasks.")

    return task_list
