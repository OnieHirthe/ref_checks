import datetime as dt
from pytz import UTC

def NOW():
    return dt.datetime.now().replace(tzinfo=UTC)

def today():
    return dt.date.today()

def year():
    return NOW().year
