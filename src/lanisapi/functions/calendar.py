"""This script includes classes and functions about the 'Kalender' page."""

import calendar
from dataclasses import dataclass
from datetime import datetime
from functools import partial
from typing import Callable

from ..constants import LOGGER, URL
from ..helpers.request import Request


@dataclass
class Calendar:
    """The calendar page in a data type.

    Parameters
    ----------
    start : datetime.datetime
        Start date and time of the calendar.
    end : datetime.datetime
        End date and time of the calendar.
    events : list[Calendar] or list[dict[str, any]]
        Use `events` to access the most important properties.
        It is either in `Calendar` or `JSON` format.
        When it is in JSON format it has all, including unnecessary ones, properties.
    """

    @dataclass
    class Event:
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
        responsible : Callable
            The person who is responsible for this event.
            You need to call this first, then it returns (hopefully) a string.
        """

        title: str
        description: str
        place: str
        start: datetime
        end: datetime
        whole_day: bool
        responsible: Callable

    start: datetime
    end: datetime
    events: list[Event] | list[dict[str, any]] = None


def _get_responsible(id: str) -> str:
    """Get the responsible person of an event.

    Parameters
    ----------
    id : str
        The id of the calendar event, if None just return None.

    Returns
    -------
    str
    """
    if not id:
        return None

    data = {
        "f": "getEvent",
        "id": id,
    }

    response = Request.post(URL.calendar, data=data)

    return response.json()["properties"]["verantwortlich"]


def _get_calendar_month(json: bool = False) -> Calendar:
    """Use the _get_calendar() function but only returns all events of the current month.

    Returns
    -------
    Calendar
        `Calendar` with `Event`
    """
    today = datetime.today()

    # calendar.monthrange returns two days (current and last).
    _, last_day = calendar.monthrange(
        int(today.strftime("%Y")), int(today.strftime("%-m"))
    )

    last_date = today.replace(day=last_day)
    first_date = today.replace(day=1)

    return _get_calendar(first_date, last_date, json=json)


def _get_calendar(start: datetime, end: datetime, json: bool = False) -> Calendar:
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
        `Calendar` with `Event` or JSON.
    """
    # `f` Functions ### Associated script = /module/kalender/js/kalender.js

    ### Getting all events.
    # `f`: `getEvents` = We want all events in JSON format.
    # `start` = From when do we want to start getting events, also includes events that start earlier then `start`.
    #           Format: Year-Month-Day - 2023-10-30
    # `end` = Like start but ending date, also includes events that end later then `end`.

    # -- Unknown:
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

    data = {
        "f": "getEvents",
        "start": start.strftime("%Y-%m-%d"),
        "end": end.strftime("%Y-%m-%d"),
    }

    calendar_raw_data = Request.post(URL.calendar, data=data)

    # Just lazily return JSON.
    if json:
        calendar = Calendar(start, end, events=[])
        for event in calendar_raw_data.json():
            calendar.events.append(event)

        LOGGER.info("Get calendar: Successfully got calendar in JSON format.")

        return calendar

    # Get JSON and map it to `Calendar` data class.
    calendar = Calendar(start, end, events=[])
    for data in calendar_raw_data.json():
        # If data["Verantwortlich"] doesn't even exist, we can just return None when called.
        try:
            responsible = (
                partial(_get_responsible, id=data["Id"])
                if data["Verantwortlich"]
                else partial(_get_responsible, id=None)
            )
        except KeyError:
            responsible = partial(_get_responsible, id=None)

        calendar_data = Calendar.Event(
            title=data["title"],
            description=data["description"],
            place=data["Ort"],
            start=datetime.strptime(data["Anfang"], "%Y-%m-%d %H:%M:%S"),
            end=datetime.strptime(data["Ende"], "%Y-%m-%d %H:%M:%S"),
            whole_day=data["allDay"],
            responsible=responsible,
        )
        calendar.events.append(calendar_data)

    LOGGER.info("Get calendar: Successfully got calendar.")

    return calendar
