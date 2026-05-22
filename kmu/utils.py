import datetime as dt
from django.utils.timezone import now as NOW

def today():
    return dt.date.today()

def year():
    return NOW().year
