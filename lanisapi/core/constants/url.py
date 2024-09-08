from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class URL:
    """
    Collection of various URLs.
    """

    base = "https://start.schulportal.hessen.de/"
    login = "https://login.schulportal.hessen.de/"
    connect = "https://connect.schulportal.hessen.de/"
    schools = "https://startcache.schulportal.hessen.de/exporteur.php"

    start = urljoin(base, "startseite.php")
    substitutions = urljoin(base, "vertretungsplan.php")
