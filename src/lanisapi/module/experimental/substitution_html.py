import datetime
from urllib.parse import urljoin
import re

from ..module import StandardModule
from ..standard.substitution import SubstitutionPlan
from ...core.helper.url import URL


# TODO: ADD SUPPORT FOR HTML PARSING

class SubstitutionHTMLModule(StandardModule):
    name = 'substitution'
    link = urljoin(URL.index, 'vertretungsplan.php')

    def _get_dates(self):
        response = self.request.get(self.link)
        return set([date.group(1) for date in re.finditer(r'data-tag="(\d{2}\.\d{2}\.\d{4})"', response.text)])

    def _fetch_plan(self, date: str):
        data = {"ganzerPlan": "true", "tag": date}
        response = self.request.post(self.link, data=data)

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

    def get(self):
        dates = self._get_dates()

        plans = []

        for date in dates:
            plans.append(self._fetch_plan(date))

        return plans
