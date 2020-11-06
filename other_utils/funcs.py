import ast
from os import path
from httpx import AsyncClient
from io import BytesIO
from random import randint

from discord import Embed, Colour


def getPath():
    return path.dirname(path.realpath(__file__))[:-12]


def randomEyes():
    eyes = 0
    for _ in range(12):
        luckyNumber = randint(1, 10)
        if luckyNumber == 1:
            eyes += 1
    return eyes


def errorEmbed(error, message):
    if error is None:
        error = "Error"
    e = Embed(
        title=f":no_entry: {error}",
        colour=Colour.red(),
        description=message
    )
    return e


def formatting(text):
    output = "```" + text[:2042] + "```"
    if output == "``````":
        raise Exception
    return output


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
        return int(hours), int(minutes), int(seconds), int(round(milli, 0))
    days, hours, minutes, seconds = int(days), int(hours), int(minutes), int(seconds)
    formatted = f"{days} day{'' if days==1 else 's'}, {hours} hour{'' if hours==1 else 's'}, {minutes}" + \
                f" minute{'' if minutes==1 else 's'}, and {seconds} second{'' if seconds==1 else 's'}"
    return formatted


def insertReturns(body):
    if isinstance(body[-1], ast.Expr):
        body[-1] = ast.Return(body[-1].value)
        ast.fix_missing_locations(body[-1])
    if isinstance(body[-1], ast.If):
        insertReturns(body[-1].body)
        insertReturns(body[-1].orelse)
    if isinstance(body[-1], ast.With):
        insertReturns(body[-1].body)


def celsiusToFahrenheit(value):
    return (value * 9/5) + 32


def degreesToDirection(value):
    if not 11.24 <= value <= 348.75:
        return "N"
    elif 11.25 <= value <= 33.74:
        return "NNE"
    elif 33.75 <= value <= 56.24:
        return "NE"
    elif 56.25 <= value <= 78.74:
        return "ENE"
    elif 78.75 <= value <= 101.24:
        return "E"
    elif 101.25 <= value <= 123.74:
        return "ESE"
    elif 123.75 <= value <= 146.24:
        return "SE"
    elif 146.25 <= value <= 168.74:
        return "SSE"
    elif 168.75 <= value <= 191.24:
        return "S"
    elif 191.25 <= value <= 213.74:
        return "SSW"
    elif 213.75 <= value <= 236.24:
        return "SW"
    elif 236.25 <= value <= 258.74:
        return "WSW"
    elif 258.75 <= value <= 281.24:
        return "W"
    elif 281.24 <= value <= 303.74:
        return "WNW"
    elif 303.75 <= value <= 326.24:
        return "NW"
    else:
        return "NNW"


async def reactionRemove(reaction, user):
    try:
        await reaction.remove(user)
    except:
        return


async def getRequest(url, headers=None, params=None, timeout=None):
    if headers is None:
        headers = {}
    async with AsyncClient() as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return res


async def getImage(url, headers=None, params=None, timeout=None):
    if headers is None:
        headers = {}
    async with AsyncClient() as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
        if res.status_code != 200:
            return None
        return BytesIO(res.content)
