import re as regex

MONTH_SWITCHER = {
    'JAN': 1, 'FEB': 2, 'MAR': 3,
    'APR': 4, 'MAY': 5, 'JUN': 6,
    'JUL': 7, 'AUG': 8, 'SEP': 9,
    'OCT': 10, 'NOV': 11, 'DEC': 12
}

GEDCOM_DATE_REGEX = '^(0?[1-9]|[1-2][0-9]|3[0-1]) ([A-Z]{3}) ([1-9]{1}[0-9]{2,3})$'

def parseId(rawId):
    return rawId.replace('@', '').strip()

def parseDate(event):
    date = event.getChildByTag('DATE')
    if date is None:
        return None

    match = regex.match(GEDCOM_DATE_REGEX, date.getValue())

    if match is None:
        return None

    day, month, year = match.groups()

    month_parsed = MONTH_SWITCHER.get(month, 0)

    return (int(year), month_parsed, int(day))

def parseLocation(event):
    location = []
    place = event.getChildByTag('PLAC')
    if place is not None:
        location.append(place.getValue())

    address = event.getChildByTag('ADDR')
    if address is not None:
        location.append(address.getValue())

    return ', '.join(location)
