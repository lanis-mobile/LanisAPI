"""With this script you can get all schools that have Lanis and it has the School dataclass."""

import json
import os
from dataclasses import dataclass

from ..constants import LOGGER, URL
from ..helpers.request import Request


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

def _get_schools(save: bool) -> list[dict[str, str]]:
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

    # `a`: `schoollist` = just means to get the schoollist.
    response = Request.get(URL.schools, params={"a": "schoollist"})

    if not response:
        return None

    response = response.json()

    schools = []

    # We don't want the categories only the schools.
    for group in response:
        for school in group["Schulen"]:
            schools.append(school)

    if save is True:
        with open("schools.json", "w") as file:
                json.dump(schools, file)

    LOGGER.info("Get schools: Successfully got schools.")

    return schools
