"""This script includes classes and functions about the 'Vertretungsplan' page."""

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from selectolax.parser import HTMLParser

from ..constants import LOGGER, URL
from ..helpers.request import Request


@dataclass
class SubstitutionPlan:
    """The substitution plan page in a data type.

    Parameters
    ----------
    date : datetime.datetime
        Date of the substitution plan.
    substitutions : list[Substitution]
        The individual substitutions.
    info : str, optional
        ``info`` is the box with the title "Allgemein" that exists sometimes.
    """

    @dataclass
    class Substitution:
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
    substitutions: list[Substitution]
    info: Optional[str] = None

def _get_substitution_info() -> dict[str, str]:
    """Return the notice (if available) and date of the substitution plan.

    Returns
    -------
    dict[str, str]
        The data
    """
    page = Request.get(URL.substitution_plan)

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

    LOGGER.info(f"Substitution info: Successfully got info. Notice is {bool(notice)}.")

    return {"notice": notice, "date": date}

def _get_substitutions() -> SubstitutionPlan:
    """Return the whole substitution plan of the current day.

    Returns
    -------
    SubstitutionPlan
    """
    info = _get_substitution_info()

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
    substitution_raw_data = Request.post(URL.substitution_plan, data=data)

    plan = SubstitutionPlan(
        datetime.strptime(info["date"], "%d.%m.%Y").date(), [])

    if info["notice"]:
        plan.info = info["notice"]

    # Map JSON to Substitution.
    for data in substitution_raw_data.json():
        substitution_data = SubstitutionPlan.Substitution(
            substitute=data["Vertreter"],
            teacher=data["Lehrer"],
            hours=data["Stunde"],
            class_name=data["Klasse"],
            subject=data["Fach"],
            room=data["Raum"],
            notice=data["Hinweis"] if data["Hinweis"] else None,
        )

        plan.substitutions.append(substitution_data)

    LOGGER.info("Get substitution plan: Success.")

    return plan
