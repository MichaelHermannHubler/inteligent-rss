import sqlite3
import datetime

def adapt_timeobj(timeobj):
    return ((3600*timeobj.hour + 60*timeobj.minute + timeobj.second)*10**6 
            + timeobj.microsecond)

def convert_timeobj(val):
    val = int(val)
    hour, val = divmod(val, 3600*10**6)
    minute, val = divmod(val, 60*10**6)
    second, val = divmod(val, 10**6)
    microsecond = int(val)
    return datetime.time(hour, minute, second, microsecond)


