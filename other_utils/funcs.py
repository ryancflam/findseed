from os import path
from io import BytesIO
from json import load
from httpx import AsyncClient
from datetime import datetime

from discord import Embed


def getPath():
    return path.dirname(path.realpath(__file__))[:-12]


def userNotBlacklisted(client, message):
    with open(f"{getPath()}/data/blacklist.json", "r", encoding="utf-8") as f:
        data = load(f)
    f.close()
    serverList = list(data["servers"])
    userList = list(data["users"])
    allowed = True
    for serverID in serverList:
        server = client.get_guild(serverID)
        if server:
            member = server.get_member(message.author.id)
            if member:
                allowed = False
                break
    return allowed and message.author.id not in userList and \
        (not message.guild or message.guild.id not in serverList)


def sign(value):
    return -1 if value < 0 else 0 if value == 0 else 1


def errorEmbed(error, message):
    return Embed(title=f":no_entry: {error or 'Error'}", colour=0xe74c3c, description=message)


def formatting(text, limit: int=2048):
    output = "```\n" + text[:limit - 6] + "```"
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
    return f"{days} day{'' if days==1 else 's'}, {hours} hour{'' if hours==1 else 's'}, {minutes}" + \
           f" minute{'' if minutes==1 else 's'}, and {seconds} second{'' if seconds==1 else 's'}"


def monthNumberToName(number):
    if int(number) == 1:
        return "January"
    if int(number) == 2:
        return "February"
    if int(number) == 3:
        return "March"
    if int(number) == 4:
        return "April"
    if int(number) == 5:
        return "May"
    if int(number) == 6:
        return "June"
    if int(number) == 7:
        return "July"
    if int(number) == 8:
        return "August"
    if int(number) == 9:
        return "September"
    if int(number) == 10:
        return "October"
    if int(number) == 11:
        return "November"
    if int(number) == 12:
        return "December"


def monthNameToNumber(name: str):
    if name.casefold().startswith("ja"):
        return "1"
    if name.casefold().startswith("f"):
        return "2"
    if name.casefold().startswith("mar"):
        return "3"
    if name.casefold().startswith("ap"):
        return "4"
    if name.casefold().startswith("may"):
        return "5"
    if name.casefold().startswith("jun"):
        return "6"
    if name.casefold().startswith("jul"):
        return "7"
    if name.casefold().startswith("au"):
        return "8"
    if name.casefold().startswith("s"):
        return "9"
    if name.casefold().startswith("o"):
        return "10"
    if name.casefold().startswith("n"):
        return "11"
    if name.casefold().startswith("d"):
        return "12"


def celsiusToFahrenheit(value):
    return value * 9 / 5 + 32


def timeStrToDatetime(date: str):
    dateFilter = date.split(".")
    if len(dateFilter) > 1:
        date = dateFilter[0] + "Z"
    dateObj = datetime.strptime(date.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
    return f"{dateObj.date()} {dateObj.time()}"


async def reactionRemove(reaction, user):
    try:
        await reaction.remove(user)
    except:
        return


async def getRequest(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return res


async def getImage(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return BytesIO(res.content)


async def postRequest(url, data=None, headers=None, timeout=None, verify=True, json=None):
    async with AsyncClient(verify=verify) as session:
        res = await session.post(url, data=data, headers=headers, timeout=timeout, json=json)
    return res


async def decodeQR(link):
    res = await getRequest(
        "http://api.qrserver.com/v1/read-qr-code",
        params={"fileurl": link}
    )
    return res.json()[0]["symbol"][0]["data"]
