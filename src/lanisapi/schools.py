"""Provides an interface to access the list of schools which have Lanis."""

from dataclasses import dataclass
from functools import cache

import httpx

from ._constants import URL


@dataclass
class School:
    id: int
    name: str
    city: str


@dataclass
class District:
    id: int
    name: str
    schools: list[School]


def parse_schools(json: list[dict]) -> list[District]:
    """
    Produces a list of dataclasses so you can use the school list easily.

    :param list[dict] json: The JSON from :func:`get_schools`.
    :return: The JSON parsed into a dataclass.
    :rtype: list[District]
    """

    districts: list[District] = []

    for district in json:
        schools: list[School] = []
        for school in district["Schulen"]:
            schools.append(School(int(school["Id"]), school["Name"], school["Ort"]))
        districts.append(District(int(district["Id"]), district["Name"], schools))

    return districts


@cache
def get_schools(request=httpx.Client()) -> list[dict] | None:
    """
    Returns a list of schools that have Lanis. The list has this format::

        list[
            dict{ -> District
                Id: str
                Name: str
                Schulen: list[
                    dict{ -> School
                        Id: str
                        Name: str
                        Ort: str
                    }
                ]
            }
        ]

    The gotten value is cached until the python interpreter stops.

    :param httpx.Client request: Optional, authentication isn't required.
    :return: The school list JSON or when an error occurred None.
    :rtype: list[dict] or None
    """

    response = request.get(URL.schools, params={"a": "schoollist"})

    if not response:
        return None

    return response.json()


def get_school_id(name: str, city: str, request=httpx.Client()) -> int | None:
    """
    Gets a school id via the provided name and district name.

    :param str name: The name of the school.
    :param str city: The city of the school.
    :param httpx.Client request: Optional, authentication isn't required.
    :return: A school id or None when not successful.
    :rtype: int or None
    """

    schools = parse_schools(get_schools(request))
    for district in schools:
        for school in district.schools:
            if school.name == name and school.city == city:
                return school.id
    return None
