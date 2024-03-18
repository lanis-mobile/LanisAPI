from urllib.parse import urljoin

from ..module import StandardModule
from ...core.helper.url import URL


class SubstitutionModule(StandardModule):
    name = 'substitution'
    link = urljoin(URL.index, 'vertretungsplan.php')

    def get(self):
        print("test")
