import datetime
from dataclasses import dataclass
from urllib.parse import urljoin
import re

from ..module import Module
from ...core.helper.url import URL


@dataclass
class SubstitutionPlan:
    @dataclass
    class Substitution:
        type: str
        substitute: str
        teacher: str
        hours: str
        classes: str
        subject: str
        room: str
        notice: str

    date: datetime.date
    #info: str
    substitutions: list[Substitution]


class SubstitutionModule(Module):
    _name = 'substitution'
    _link = urljoin(URL.index, 'vertretungsplan.php')

    def _get_dates(self) -> set[str]:
        response = self._request.get(self._link)
        return set([date.group(1) for date in re.finditer(r'data-tag="(\d{2}\.\d{2}\.\d{4})"', response.text)])

    def _fetch_plan(self, date: str) -> SubstitutionPlan:
        data = {"ganzerPlan": "true", "tag": date}
        response = self._request.post(self._link, data=data)

        return SubstitutionPlan(
            date=datetime.datetime.strptime(date, "%d.%m.%Y").date(),
            substitutions=[SubstitutionPlan.Substitution(
                type=substitution["Art"],
                substitute=substitution["Vertreter"],
                teacher=substitution["Lehrer"],
                hours=substitution["Stunde"],
                classes=substitution["Klasse"],
                subject=substitution["Fach"],
                room=substitution["Raum"],
                notice=substitution["Hinweis"] if substitution["Hinweis"] else None,
            ) for substitution in response.json()]
        )

    def get(self) -> list[SubstitutionPlan]:
        dates = self._get_dates()

        plans = []

        for date in dates:
            plans.append(self._fetch_plan(date))

        return plans
