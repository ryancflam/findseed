from datetime import date, datetime, timedelta

from dateutil import parser
from numpy import array

from src.utils.funcs.math_and_numbers import oneIn


def formatting(text, limit: int=2048):
    output = "```\n" + text[:limit - 7] + "```"
    if output == "``````":
        raise Exception
    return output


def formatCogName(cog):
    return cog.casefold().replace(" ", "_").replace(".py", "")


def replaceCharacters(string, toreplace, replaceto: str=""):
    for char in set(toreplace):
        string = string.replace(char, replaceto)
    return string


def asciiIgnore(text):
    return text.encode("ascii", "ignore").decode("utf-8")


def multiString(string, limit: int=2000):
    return array([string[i:i + limit] for i in range(0, len(string), limit)])


def weirdCase(text):
    res = ""
    for char in text.casefold():
        res += char.upper() if oneIn(2) else char
    return res


def timeStr(d, h, m, s, ms):
    return f"{d if d else ''}{'d ' if d else ''}{h if h else ''}{'h ' if h else ''}" + \
           f"{m}m {s}s {ms if ms else ''}{'ms ' if ms else ''}".strip()


def minSecs(now, before):
    d, h, m, s, _ = timeDifferenceStr(now, before, noStr=True)
    return m + (h * 60) + (d * 1440), s


def timeDifferenceStr(newTime, oldTime, noStr=False):
    seconds = newTime - oldTime
    days = seconds // 86400
    seconds = seconds - (days * 86400)
    hours = seconds // 3600
    seconds = seconds - (hours * 3600)
    minutes = seconds // 60
    seconds = seconds - (minutes * 60)
    if noStr:
        milli = (seconds - int(seconds)) * 1000
        return int(days), int(hours), int(minutes), int(seconds), int(round(milli, 0))
    days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
    return "{:,} day{}, {} hour{}".format(days, "" if days == 1 else "s", hours, "" if hours == 1 else "s") + \
           f", {minutes} minute{'' if minutes == 1 else 's'}, and {seconds} second{'' if seconds == 1 else 's'}"


def weekdayNumberToName(number: int):
    if number == 0:
        return "Monday"
    if number == 1:
        return "Tuesday"
    if number == 2:
        return "Wednesday"
    if number == 3:
        return "Thursday"
    if number == 4:
        return "Friday"
    if number == 5:
        return "Saturday"
    return "Sunday"


def monthNumberToName(number):
    try:
        return date(1900, int(number), 1).strftime("%B")
    except Exception:
        raise Exception("Invalid month.")


def monthNameToNumber(name: str):
    name = name.casefold()
    if name.startswith("ja"):
        return "1"
    if name.startswith("f"):
        return "2"
    if name.startswith("mar"):
        return "3"
    if name.startswith("ap"):
        return "4"
    if name.startswith("may"):
        return "5"
    if name.startswith("jun"):
        return "6"
    if name.startswith("jul"):
        return "7"
    if name.startswith("au"):
        return "8"
    if name.startswith("s"):
        return "9"
    if name.startswith("o"):
        return "10"
    if name.startswith("n"):
        return "11"
    if name.startswith("d"):
        return "12"
    raise Exception("Invalid month.")


def dateBirthday(day: int, month: int, year: int, noBD=False):
    nowt = datetime.now()
    return ("`%s %s %s`" % (day, monthNumberToName(month), year)) \
           + (" :birthday:" if day == nowt.day and month == nowt.month and not noBD else "")


def timeStrToDatetime(datestr: str):
    datestr = datestr.split(" ", 1)
    if len(datestr) > 1:
        datestr = datestr[0] + "T" + datestr[1]
    else:
        datestr = datestr[0]
    if "+" not in datestr and "-" not in datestr and not datestr.endswith("Z"):
        datestr += "Z"
    datestr = datestr.replace("Z", "+00:00")
    if "+" in datestr:
        timezone = datestr.rsplit("+", 1)[1]
        neg = False
    else:
        timezone = datestr.rsplit("-", 1)[1]
        neg = True
    hour, minute = timezone.split(":")
    timezone = (int(hour) * 3600 + int(minute) * 60) * (1 if neg else -1)
    dateObj = parser.parse(datestr) + timedelta(seconds=timezone)
    return dateObj.strftime("%Y-%m-%d %H:%M:%S")
