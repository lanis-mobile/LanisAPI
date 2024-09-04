from functools import cache

import httpx

from .parse import parse_schools
from ..constants import URL


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

    :param request: A :class:`httpx.Client` instance.
    :return: The school list JSON or when an error occurred None.
    """

    response = request.get(URL.schools, params={"a": "schoollist"})

    if not response:
        return None

    return response.json()


def get_school_id(name: str, district_name: str, request=httpx.Client()) -> int | None:
    schools = parse_schools(get_schools(request))
    for district in schools:
        if district.name == district_name:
            for school in district.schools:
                if school.name == name:
                    return school.id
    return None
