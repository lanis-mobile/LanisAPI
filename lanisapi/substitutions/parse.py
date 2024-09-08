from datetime import datetime
from dataclasses import dataclass


@dataclass
class Substitution:
    """A single substitution element."""

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
class SubstitutionDay:
    """A day of substitutions."""

    date: datetime.date
    substitutions: list[Substitution]


def parse_substitutions(substitutions: dict) -> SubstitutionDay:
    """
    Parses a JSON of substitutions and returns a handy dataclass instance.

    :param substitutions: A day of substitutions in JSON, probably gotten by :func:`get_substitutions`.
    :return: A :class:`SubstitutionDay` instance.
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

    return SubstitutionDay(
        date=datetime.strptime(substitutions["date"], "%d.%m.%Y").date(),
        substitutions=substitution_elements
    )
