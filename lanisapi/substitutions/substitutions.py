import httpx
import re
from datetime import datetime

from .._core.constants import URL


def get_substitution_dates(request: httpx.Client) -> list[datetime.date]:
    """
    Gets the dates which have substitutions available.

    :param request: An authenticated :class:`httpx.Client` instance.
    :return: List of :class:`datetime.date` objects.
    """

    response = request.get(URL.substitutions).text

    dates: set[datetime.date] = set()

    for date in re.findall(r'data-tag="(\d{2}\.\d{2}\.\d{4})"', response):
        dates.add(datetime.strptime(date, "%d.%m.%Y").date())

    return list(dates)


def get_substitutions(date: datetime.date, request: httpx.Client) -> dict:
    """
    **Uses the Ajax method to get the substitutions, some schools may not have Ajax available!
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

    :param request: An authenticated :class:`httpx.Client` instance.
    :param date: A :class:`datetime.date` object, probably gotten by :func:`get_substitution_dates`.
    :return: A JSON of substitutions.
    """

    response = request.post(
        URL.substitutions,
        data={
            "ganzerPlan": "true",
            "tag": date.strftime("%d.%m.%Y"),
        }
    )

    return {
        "date": date.strftime("%d.%m.%Y"),
        "substitutions": response.json()
    }
