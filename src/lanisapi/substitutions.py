from dataclasses import dataclass

import httpx
import re
import datetime
from ._constants import URL


@dataclass
class Substitution:
    substitute: str | None
    teacher: str | None
    hour: str | None
    class_name: str | None
    class_old: str | None
    subject: str | None
    subject_old: str | None
    room: str | None
    room_old: str | None
    info: str | None
    info2: str | None
    type: str | None
    learn_group: str | None
    teacher_abbreviation: str | None
    substitute_abbreviation: str | None
    highlighted: list | None


@dataclass
class SubstitutionPlan:
    """A day of substitutions."""

    date: datetime.date
    substitutions: list[Substitution]


def parse_substitutions(substitutions: dict) -> SubstitutionPlan:
    """
    Parses a JSON of substitutions and returns a handy dataclass.

    :param dict substitutions: A JSON of a substitution day.
    :return: A :class:`SubstitutionDay` object.
    :rtype: SubstitutionDay
    """

    substitution_elements: list[Substitution] = []
    for substitution in substitutions["substitutions"]:
        substitution_elements.append(Substitution(
            substitute=None if not substitution["Vertreter"] else substitution["Vertreter"],
            teacher=None if not substitution["Lehrer"] else substitution["Lehrer"],
            hour=None if not substitution["Stunde"] else substitution["Stunde"],
            class_name=None if not substitution["Klasse"] else substitution["Klasse"],
            class_old=None if not substitution["Klasse_alt"] else substitution["Klasse_alt"],
            subject=None if not substitution["Fach"] else substitution["Fach"],
            subject_old=None if not substitution["Fach_alt"] else substitution["Fach_alt"],
            room=None if not substitution["Raum"] else substitution["Raum"],
            room_old=None if not substitution["Raum_alt"] else substitution["Raum_alt"],
            info=None if not substitution["Hinweis"] else substitution["Hinweis"],
            info2=None if not substitution["Hinweis2"] else substitution["Hinweis2"],
            type=None if not substitution["Art"] else substitution["Art"],
            learn_group=None if not substitution["Lerngruppe"] else substitution["Lerngruppe"],
            teacher_abbreviation=None if not substitution["Lehrerkuerzel"] else substitution["Lehrerkuerzel"],
            substitute_abbreviation=None if not substitution["Vertreterkuerzel"] else substitution["Vertreterkuerzel"],
            highlighted=None if not substitution["_hervorgehoben"] else substitution["_hervorgehoben"],
        ))

    return SubstitutionPlan(
        date=datetime.datetime.strptime(substitutions["date"], "%d.%m.%Y").date(),
        substitutions=substitution_elements
    )


def get_substitution_dates(request: httpx.Client) -> list[datetime.date]:
    """
    Gets a list of all available substitution dates.

    :param httpx.Client request:
    :return: List of :class:`datetime.date` objects.
    :rtype: list[datetime.date]
    """

    response = request.get(URL.substitutions).text

    dates: set[datetime.date] = set()

    for date in re.findall(r'data-tag="(\d{2}\.\d{2}\.\d{4})"', response):
        dates.add(datetime.datetime.strptime(date, "%d.%m.%Y").date())

    return list(dates)


def get_substitutions(date: datetime.date, request: httpx.Client, whole_plan=True) -> dict:
    """
    **Uses the Ajax method to get the substitutions, some schools may not have this method available!
    Non-Ajax isn't supported right now.**

    Gets substitutions of the current date. The list has the following format::

        dict{
            date: str; date format = %d.%m.%Y, added by the function for convenience
            list[
                dict{ -> Substitution element
                    Tag: str; date format = %d.%m.%Y
                    Vertreter: str
                    Lehrer: str; can include HTML like <del>
                    Stunde: str; can be just one number, can be range like 3 - 4
                    Klasse: str
                    Klasse_alt: str
                    Fach: str
                    Fach_alt: str
                    Raum: str
                    Raum_alt: str
                    Hinweis: str; can be empty
                    Art: str
                    Hinweis2: str; can be empty
                    Lerngruppe: str
                    Tag_en: str; date format = %Y-%m-%d
                    Lehrerkuerzel: str
                    Vertreterkuerzel: str
                    _hervorgehoben: list[]
                }
            ]
        }

    Elements can also be `None`.

    :param httpx.Client request:
    :param datetime.date date:
    :param bool whole_plan: Defaults to true. If false, only substitution connected with your schedule will be shown.
    :return: A JSON of substitutions.
    :rtype: dict
    """

    response = request.post(
        URL.substitutions,
        data={
            "ganzerPlan": str(whole_plan),
            "tag": date.strftime("%d.%m.%Y"),
        }
    )

    return {
        "date": date.strftime("%d.%m.%Y"),
        "substitutions": response.json()
    }
