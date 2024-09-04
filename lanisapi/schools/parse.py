from dataclasses import dataclass


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

    :param json: The JSON from :func:`get_schools`.
    :return: List of :class:`District`.
    """

    districts: list[District] = []

    for district in json:
        schools: list[School] = []
        for school in district["Schulen"]:
            schools.append(School(int(school["Id"]), school["Name"], school["Ort"]))
        districts.append(District(int(district["Id"]), district["Name"], schools))

    return districts
