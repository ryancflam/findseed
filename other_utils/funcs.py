from datetime import date, datetime
from io import BytesIO
from json import dump, load
from os import path

from discord import Embed, File
from httpx import AsyncClient, get


def getPath():
    return path.dirname(path.realpath(__file__))[:-12]


def readJson(pathstr):
    with open(f"{getPath()}/{pathstr}", "r", encoding="utf-8") as f:
        data = load(f)
    f.close()
    return data


def dumpJson(pathstr, data):
    with open(f"{getPath()}/{pathstr}", "w") as f:
        dump(data, f, sort_keys=True, indent=4)
    f.close()


def userNotBlacklisted(client, message):
    data = readJson("data/blacklist.json")
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
    return -1 if value < 0 else 0 if not value else 1


def errorEmbed(error, message):
    return Embed(title=f":no_entry: {error or 'Error'}", colour=0xe74c3c, description=message)


def formatting(text, limit: int=2048):
    output = "```\n" + text[:limit - 7] + "```"
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
    return "{:,} day{}, {} hour{}".format(days, "" if days == 1 else "s", hours, "" if hours == 1 else "s") + \
           f", {minutes} minute{'' if minutes == 1 else 's'}, and {seconds} second{'' if seconds == 1 else 's'}"


def monthNumberToName(number):
    try:
        return date(1900, int(number), 1).strftime("%B")
    except Exception:
        raise Exception("Invalid month.")


def monthNameToNumber(name: str):
    if name.casefold().startswith("ja"):
        return "1"
    elif name.casefold().startswith("f"):
        return "2"
    elif name.casefold().startswith("mar"):
        return "3"
    elif name.casefold().startswith("ap"):
        return "4"
    elif name.casefold().startswith("may"):
        return "5"
    elif name.casefold().startswith("jun"):
        return "6"
    elif name.casefold().startswith("jul"):
        return "7"
    elif name.casefold().startswith("au"):
        return "8"
    elif name.casefold().startswith("s"):
        return "9"
    elif name.casefold().startswith("o"):
        return "10"
    elif name.casefold().startswith("n"):
        return "11"
    elif name.casefold().startswith("d"):
        return "12"
    else:
        raise Exception("Invalid month.")


def celsiusToFahrenheit(value):
    return value * 9 / 5 + 32


def timeStrToDatetime(datestr: str):
    dateFilter = datestr.split(".")
    if len(dateFilter) > 1:
        datestr = dateFilter[0] + "Z"
    dateObj = datetime.strptime(datestr.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
    return f"{dateObj.date()} {dateObj.time()}"


def getTickers():
    tickers = {}
    res = get("https://api.coingecko.com/api/v3/coins/list")
    data = res.json()
    for i in data:
        tickers[i["symbol"]] = i["id"]
    return tickers


async def readTxt(message):
    attachment = await message.attachments[0].read()
    return attachment.decode("utf-8")


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


async def sendImage(ctx, url: str, name: str="image.png", message=None):
    await ctx.send(message, file=File(await getImage(url), name))


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
