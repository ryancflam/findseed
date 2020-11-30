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


def sign(value):
    return -1 if value < 0 else 0 if value == 0 else 1


def errorEmbed(error, message):
    return Embed(
        title=f":no_entry: {error or 'Error'}",
        colour=Colour.red(),
        description=message
    )


def formatting(text):
    output = "```\n" + text[:2042] + "```"
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
    return value * 9 / 5 + 32


def degreesToDirection(value):
    if not 11.24 <= value <= 348.75:
        return "N"
    if 11.25 <= value <= 33.74:
        return "NNE"
    if 33.75 <= value <= 56.24:
        return "NE"
    if 56.25 <= value <= 78.74:
        return "ENE"
    if 78.75 <= value <= 101.24:
        return "E"
    if 101.25 <= value <= 123.74:
        return "ESE"
    if 123.75 <= value <= 146.24:
        return "SE"
    if 146.25 <= value <= 168.74:
        return "SSE"
    if 168.75 <= value <= 191.24:
        return "S"
    if 191.25 <= value <= 213.74:
        return "SSW"
    if 213.75 <= value <= 236.24:
        return "SW"
    if 236.25 <= value <= 258.74:
        return "WSW"
    if 258.75 <= value <= 281.24:
        return "W"
    if 281.24 <= value <= 303.74:
        return "WNW"
    if 303.75 <= value <= 326.24:
        return "NW"
    return "NNW"


async def reactionRemove(reaction, user):
    try:
        await reaction.remove(user)
    except:
        return


async def getRequest(url, headers=None, params=None, timeout=None):
    async with AsyncClient() as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
        if res.status_code != 200:
            return None
    return res


async def getImage(url, headers=None, params=None, timeout=None):
    async with AsyncClient() as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
        if res.status_code != 200:
            return None
    return BytesIO(res.content)


async def postRequest(url, data=None, headers=None, timeout=None):
    async with AsyncClient() as session:
        res = await session.post(url, data=data, headers=headers, timeout=timeout)
        if res.status_code != 200:
            return None
    return res


async def decodeQR(link):
    url = f"http://api.qrserver.com/v1/read-qr-code/?fileurl={link}"
    res = await getRequest(url)
    return res.json()[0]["symbol"][0]["data"]
