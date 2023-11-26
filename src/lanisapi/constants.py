"""This script has various global constants."""

import logging
from dataclasses import dataclass
from typing import TypeAlias
from urllib.parse import urljoin

LOGGER = logging.getLogger("LanisClient")

logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(name)s   %(message)s")

JSON: TypeAlias = dict[str, any]

@dataclass
class URL:
    """Contain various constant URLs."""

    base = "https://start.schulportal.hessen.de/"
    index = urljoin(base, "index.php")
    conversations = urljoin(base, "nachrichten.php")
    tasks = urljoin(base, "meinunterricht.php")
    calendar = urljoin(base, "kalender.php")
    substitution_plan = urljoin(base, "vertretungsplan.php")
    schools = urljoin("https://startcache.schulportal.hessen.de/", "exporteur.php")
    encryption = urljoin(base, "ajax.php")
    login = "https://login.schulportal.hessen.de/"
