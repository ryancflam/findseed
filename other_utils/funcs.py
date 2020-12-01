from os import path
from httpx import AsyncClient
from io import BytesIO

from discord import Embed, Colour


def getPath():
    return path.dirname(path.realpath(__file__))[:-12]


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


def celsiusToFahrenheit(value):
    return value * 9 / 5 + 32


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
