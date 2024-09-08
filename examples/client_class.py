from lanisapi import Session, get_applet_availability
from lanisapi.substitutions import substitution_link, get_substitution_dates, parse_substitutions, get_substitutions, SubstitutionDay


class LanisClient:
    """An example client so that you don't need to pass request all the time and save other things."""

    def __init__(self, session: Session):
        self.account = session.account
        self.request = session.request
        self.token = session.token

    def get_substitutions(self) -> list[SubstitutionDay]:
        if get_applet_availability(substitution_link, self.request):
            substitutions = []
            for date in get_substitution_dates(self.request):
                substitutions.append(parse_substitutions(get_substitutions(date, self.request)))

            return substitutions
        else:
            return []
