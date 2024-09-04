from dataclasses import dataclass


@dataclass
class URL:
    """
    Collection of various URLs.
    """

    base = "https://start.schulportal.hessen.de/"
    login = "https://login.schulportal.hessen.de/"
    connect = "https://connect.schulportal.hessen.de/"
    schools = "https://startcache.schulportal.hessen.de/exporteur.php"
    start = "https://start.schulportal.hessen.de/startseite.php"
