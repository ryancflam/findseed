from binascii import b2a_hex
from calendar import monthrange
from os import urandom
from random import randint

from numpy import min

from src.utils.safe_eval import SafeEval

KELVIN = 273.15


def strictRounding(value: float):
    return int(value) + (0 if value.is_integer() else 1)


def removeDotZero(value):
    try:
        valuestr = "{:,}".format(value)
    except:
        valuestr = str(value)
    while valuestr.endswith(".0"):
        valuestr = valuestr[:-2]
    return valuestr


def oneIn(odds: int):
    return False if odds < 1 else not randint(0, odds - 1)


def randomHex(digits: int):
    return b2a_hex(urandom(digits)).decode("utf-8")[:digits]


def evalMath(inp: str):
    ans = SafeEval(inp).result()
    if ans[0]:
        return ans[1]
    elif "ZeroDivisionError" in ans[1]:
        raise ZeroDivisionError("You cannot divide by zero!")
    raise Exception(ans[1])


def degreesToDirection(value: float):
    if not 11.25 < value <= 348.75:
        return "N"
    if 11.25 < value <= 33.75:
        return "NNE"
    if 33.75 < value <= 56.25:
        return "NE"
    if 56.25 < value <= 78.75:
        return "ENE"
    if 78.75 < value <= 101.25:
        return "E"
    if 101.25 < value <= 123.75:
        return "ESE"
    if 123.75 < value <= 146.25:
        return "SE"
    if 146.25 < value <= 168.75:
        return "SSE"
    if 168.75 < value <= 191.25:
        return "S"
    if 191.25 < value <= 213.75:
        return "SSW"
    if 213.75 < value <= 236.25:
        return "SW"
    if 236.25 < value <= 258.75:
        return "WSW"
    if 258.75 < value <= 281.25:
        return "W"
    if 281.25 < value <= 303.75:
        return "WNW"
    if 303.75 < value <= 326.25:
        return "NW"
    return "NNW"


def btcOrSat(sats):
    sats = int(sats)
    if -10000 < sats < 10000:
        unit = " sat."
    else:
        sats = round(sats * 0.00000001, 8)
        unit = " BTC"
    return removeDotZero(sats) + unit


def dateDifference(dateobj, dateobj2):
    years = dateobj2.year - dateobj.year
    months = dateobj2.month - dateobj.month
    daysfinal = dateobj2.day - dateobj.day
    if dateobj.day > dateobj2.day and dateobj.month > dateobj2.month:
        months = 11 - (dateobj.month - dateobj2.month)
        daysfinal = monthrange(dateobj.year, dateobj.month)[1] - (dateobj.day - dateobj2.day)
        years -= 1
    elif dateobj.day > dateobj2.day and dateobj.month == dateobj2.month:
        daysfinal = 31 - (dateobj.day - dateobj2.day)
        months = 12 if not months else months
        months -= 1
        years -= 1
    elif dateobj.day <= dateobj2.day and dateobj.month > dateobj2.month:
        months += 12
        years -= 1
    elif dateobj.day > dateobj2.day and dateobj.month < dateobj2.month:
        daysfinal = monthrange(dateobj.year, dateobj.month)[1] + daysfinal
        months = 12 if not months else months
        months -= 1
    return years, months, daysfinal, years * 12 + months, (dateobj2 - dateobj).days


def valueToOrdinal(n):
    n = int(n)
    return str(n) + ("th" if 11 <= (n % 100) <= 13 else ["th", "st", "nd", "rd", "th"][min([n % 10, 4])])


def leapYear(year):
    year = int(year)
    if year <= 1582:
        return None
    elif not year % 4:
        if not year % 100:
            if not year % 400:
                return True
            return False
        return True
    return False


def celsiusToFahrenheit(value: float):
    return value * 9 / 5 + 32


def fahrenheitToCelsius(value: float):
    return (value - 32) * 5 / 9


def stacksAndExcess(total: int, stackMax: int=64):
    stacks = total / stackMax
    return int(stacks), total - stackMax * int(stacks)
