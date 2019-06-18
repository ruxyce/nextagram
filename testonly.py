def pretty_date(time=False):
    """
    Get a datetime object or a int() Epoch timestamp and return a
    pretty string like 'an hour ago', 'Yesterday', '3 months ago',
    'just now', etc
    """
    from datetime import datetime
    now = datetime.now()
    if type(time) is int:
        diff = now - datetime.fromtimestamp(time)
    elif isinstance(time,datetime):
        diff = now - time
    elif not time:
        diff = now - now
    second_diff = diff.seconds
    day_diff = diff.days

    if day_diff < 0:
        return ''

    if day_diff == 0:
        if second_diff < 10:
            return "just now"
        if second_diff < 60:
            return str(second_diff) + " seconds ago"
        if second_diff < 120:
            return "a minute ago"
        if second_diff < 3600:
            return str(second_diff / 60) + " minutes ago"
        if second_diff < 7200:
            return "an hour ago"
        if second_diff < 86400:
            return str(second_diff / 3600) + " hours ago"
    if day_diff == 1:
        return "Yesterday"
    if day_diff < 7:
        return str(day_diff) + " days ago"
    if day_diff < 31:
        return str(day_diff / 7) + " weeks ago"
    if day_diff < 365:
        return str(day_diff / 30) + " months ago"
    return str(day_diff / 365) + " years ago"

# print(pretty_date('2019-06-14 13:02:16.247693'))

import re
import timeit

allowed = "abcdefghijklmnopqrstuvwxyz0123456789._"

pattern2 = "^[a-z0.9._]{5,20}$"
pattern = "^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$"

print(timeit.Timer("all(c in 'abcdefghijklmnopqrstuvwxyz0123456789._' for c in 'hohohaha')").timeit())

print(timeit.Timer("re.match('^[a-z0.9._]{5,20}$','hohohaha')", "import re").timeit())