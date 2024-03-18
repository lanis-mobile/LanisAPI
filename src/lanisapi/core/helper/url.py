from dataclasses import dataclass
from urllib.parse import urljoin


@dataclass
class URL:
    base = "https://start.schulportal.hessen.de/"
    index = urljoin(base, "index.php")
    login = "https://login.schulportal.hessen.de/"
    connect = "https://connect.schulportal.hessen.de/"
