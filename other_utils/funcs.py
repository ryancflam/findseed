from calendar import monthrange
from datetime import date, datetime
from io import BytesIO
from json import dump, load, JSONDecodeError
from os import path
from time import sleep

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


def removeDotZero(valuestr):
    valuestr = str(valuestr)
    while valuestr.endswith(".0"):
        valuestr = valuestr[:-2]
    return valuestr


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


def degreesToDirection(value):
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


def weekdayNumberToName(number):
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


def valueToOrdinal(n):
    n = int(n)
    if 11 <= (n % 100) <= 13:
        ordinal = "th"
    else:
        ordinal = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return f"{str(n)}{ordinal}"


def dateToZodiac(datestr: str, ac=False):
    month, day = datestr.split(" ")
    try:
        day = int(day)
    except:
        day = int(day[:-2])
    month = monthNumberToName(monthNameToNumber(month))
    if month == "December" and day > 21 or month == "January" and day < (20 if ac else 22):
        return "Capricorn"
    if month == "January" and day > (19 if ac else 21) or month == "February" and day < 19:
        return "Aquarius"
    if month == "February" and day > 18 or month == "March" and day < 21:
        return "Pisces"
    if month == "March" and day > 20 or month == "April" and day < 20:
        return "Aries"
    if month == "April" and day > 19 or month == "May" and day < 21:
        return "Taurus"
    if month == "May" and day > 20 or month == "June" and day < (22 if ac else 21):
        return "Gemini"
    if month == "June" and day > (21 if ac else 20) or month == "July" and day < 23:
        return "Cancer"
    if month == "July" and day > 22 or month == "August" and day < 23:
        return "Leo"
    if month == "August" and day > 22 or month == "September" and day < 23:
        return "Virgo"
    if month == "September" and day > 22 or month == "October" and day < (24 if ac else 23):
        return "Libra"
    if month == "October" and day > (23 if ac else 22) or month == "November" and day < (23 if ac else 22):
        return "Scorpio"
    if month == "November" and day > (22 if ac else 21) or month == "December" and day < 22:
        return "Sagittarius"


def yearToChineseZodiac(year):
    year = int(year)
    if not (year - 2000) % 12:
        return "Dragon (龍)"
    if (year - 2000) % 12 == 1:
        return "Snake (蛇)"
    if (year - 2000) % 12 == 2:
        return "Horse (馬)"
    if (year - 2000) % 12 == 3:
        return "Goat (羊)"
    if (year - 2000) % 12 == 4:
        return "Monkey (猴)"
    if (year - 2000) % 12 == 5:
        return "Rooster (雞)"
    if (year - 2000) % 12 == 6:
        return "Dog (狗)"
    if (year - 2000) % 12 == 7:
        return "Pig (豬)"
    if (year - 2000) % 12 == 8:
        return "Rat (鼠)"
    if (year - 2000) % 12 == 9:
        return "Ox (牛)"
    if (year - 2000) % 12 == 10:
        return "Tiger (虎)"
    return "Rabbit (兔)"


def leapYear(year):
    a = int(year)
    if a <= 1582:
        return None
    elif not a % 4:
        if not a % 100:
            if not a % 400:
                return True
            else:
                return False
        else:
            return True
    else:
        return False


def celsiusToFahrenheit(value):
    return value * 9 / 5 + 32


def timeStrToDatetime(datestr: str):
    dateFilter = datestr.split(".")
    if len(dateFilter) > 1:
        datestr = dateFilter[0] + "Z"
    dateObj = datetime.strptime(datestr.replace("T", " ").replace("Z", ""), "%Y-%m-%d %H:%M:%S")
    return f"{dateObj.date()} {dateObj.time()}"


def getTickers():
    while True:
        try:
            tickers = {}
            res = get("https://api.coingecko.com/api/v3/coins/list")
            data = res.json()
            for i in data:
                tickers[i["symbol"]] = i["id"]
            return tickers
        except JSONDecodeError:
            sleep(30)


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
