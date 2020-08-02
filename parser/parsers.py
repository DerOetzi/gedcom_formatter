import re as regex

def parseDate(event):
    date = event.getChildByTag('DATE')
    if date is None:
        return None

    match = regex.match('^([0-9]{1,2}) ([A-Z]{3}) ([18|19|20]+[0-9]{2})$', date.getValue())

    if match is None:
        return None

    day, month, year = match.groups()

    return (year, month, day)

def parseLocation(event):
    location = []
    place = event.getChildByTag('PLAC')
    if place is not None:
        location.append(place.getValue())

    address = event.getChildByTag('ADDR')
    if address is not None:
        location.append(address.getValue())

    return ', '.join(location)
