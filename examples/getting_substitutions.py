from lanisapi import Session, Account, get_school_id, get_applet_availability
from lanisapi.substitutions import get_substitution_dates, get_substitutions, parse_substitutions, substitution_link


def main():
    request = Session(Account(get_school_id("Testschule MH", "Verwaltung, LA, Schulamt"), "max.mustermann", "123456789")).request
    if get_applet_availability(substitution_link, request):
        substitution_dates = get_substitution_dates(request)
        if not substitution_dates:
            print("No substitutions found.")

        print(parse_substitutions(get_substitutions(substitution_dates[0], request)))
    else:
        print("The substitution applet is not supported by this account.")


if __name__ == '__main__':
    main()
