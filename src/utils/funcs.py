from calendar import monthrange
from datetime import date, datetime, timedelta
from io import BytesIO
from json import JSONDecodeError, dumps, loads
from os import path
from random import randint
from re import split
from time import sleep, time

from aiofiles import open
from aiofiles.os import remove
from dateutil import parser
from discord import Embed, File
from httpx import AsyncClient, get
from plotly import graph_objects as go

from src.utils.item_cycle import ItemCycle
from src.utils.safe_eval import SafeEval

tickers = {}
while True:
    try:
        cgres = get("https://api.coingecko.com/api/v3/coins/list")
        cgdata = cgres.json()
        for coin in cgdata:
            if coin["symbol"] not in tickers:
                tickers[coin["symbol"]] = coin["id"]
        break
    except JSONDecodeError:
        sleep(30)


def getPath():
    return path.dirname(path.realpath(__file__)).rsplit("src", 1)[0]


def kelvin():
    return 273.15


def musicalNotes():
    return ["C", "C♯", "D", "E♭", "E", "F", "F♯", "G", "G♯", "A", "B♭", "B"]


def numberEmojis():
    return {0: ":zero:", 1: ":one:", 2: ":two:", 3: ":three:", 4: ":four:",
            5: ":five:", 6: ":six:", 7: ":seven:", 8: ":eight:", 9: ":nine:"}


def printError(ctx, error):
    print(f"Error ({ctx.command.name}): {error}")


def oneIn(odds: int):
    return False if odds < 1 else not randint(0, odds - 1)


def evalMath(inp: str):
    ans = SafeEval(inp).result()
    if ans[0]:
        return ans[1]
    elif "ZeroDivisionError" in ans[1]:
        raise ZeroDivisionError("You cannot divide by zero!")
    raise Exception(ans[1])


def replaceCharacters(string, toreplace: list, replaceto: str=""):
    for char in toreplace:
        string = string.replace(char, replaceto)
    return string


def multiString(string, n: int=2000):
    return [string[i:i + n] for i in range(0, len(string), n)]


def commandIsOwnerOnly(command):
    return "<function is_owner.<locals>.predicate" in [str(i).split(" at")[0] for i in command.checks]


def commandIsEE(command):
    return command.cog.qualified_name == "Easter Eggs"


def commandsListEmbed(client, menu: int=0):
    e = Embed(title=f"{'Miscellaneous' if menu == 1 else 'Bot Owner' if menu == 2 else client.user.name} Commands")
    cmds = 0
    for cog in sorted(client.cogs):
        commandsList = list(filter(
            lambda x: (x.hidden and x.cog_name != "Easter Eggs" and not commandIsOwnerOnly(x)) if menu == 1
            else commandIsOwnerOnly(x) if menu == 2
            else not x.hidden,
            sorted(client.get_cog(cog).get_commands(), key=lambda y: y.name)
        ))
        value = ", ".join(f"`{client.command_prefix}{str(command)}`" for command in commandsList)
        if value:
            e.add_field(name=cog + " ({:,})".format(len(commandsList)), value=value, inline=False)
            cmds += len(commandsList)
    e.title += " ({:,})".format(cmds)
    if menu == 1:
        e.description = "Miscellaneous commands hidden from the main commands menu."
    elif menu == 2:
        e.description = "Bot owner commands."
    zero = f", or {client.command_prefix}category <category> for more information about a specific category"
    e.set_footer(text=f"Use {client.command_prefix}help <command> for help with a specific command{zero if not menu else ''}.")
    return e


def weirdCase(text):
    res = ""
    for char in text.casefold():
        res += char.upper() if oneIn(2) else char
    return res


def sign(value):
    return -1 if value < 0 else 0 if not value else 1


def strictRounding(value: float):
    return int(value) + (0 if value == int(value) else 1)


def removeDotZero(value):
    try:
        valuestr = "{:,}".format(value)
    except:
        valuestr = str(value)
    while valuestr.endswith(".0"):
        valuestr = valuestr[:-2]
    return valuestr


def errorEmbed(error, message):
    return Embed(title=f":no_entry: {error or 'Error'}", colour=0xe74c3c, description=message)


def removeMention(userID):
    userID = str(userID)
    if userID.startswith("<@!") and userID.endswith(">"):
        userID = userID[3:-1]
    elif userID.startswith("<@") and userID.endswith(">"):
        userID = userID[2:-1]
    return userID


def formatting(text, limit: int=2048):
    output = "```\n" + text[:limit - 7] + "```"
    if output == "``````":
        raise Exception
    return output


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


def dateBirthday(day: int, month: int, year: int):
    nowt = datetime.now()
    return ("`%s %s %s`" % (day, monthNumberToName(month), year)) \
           + (" :birthday:" if day == nowt.day and month == nowt.month else "")


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
    raise Exception("Invalid month.")


def valueToOrdinal(n):
    n = int(n)
    if 11 <= (n % 100) <= 13:
        ordinal = "th"
    else:
        ordinal = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return f"{str(n)}{ordinal}"


def getZodiacInfo(zodiac: str):
    if zodiac.casefold().startswith("cap"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927265871024513034/unknown.png", \
            "December 22nd to January 19th", "Capricorn"
    if zodiac.casefold().startswith("aq"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927266052985978960/unknown.png", \
            "January 20th to February 18th", "Aquarius"
    if zodiac.casefold().startswith("p"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266217725657128/unknown.png", \
            "February 19th to March 20th", "Pisces"
    if zodiac.casefold().startswith("ar"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266309664825374/unknown.png", \
            "March 21st to April 19th", "Aries"
    if zodiac.casefold().startswith("t"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266400807030854/unknown.png", \
            "April 20th to May 20th", "Taurus"
    if zodiac.casefold().startswith("g"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266546101928056/unknown.png", \
            "May 21st to June 20th", "Gemini"
    if zodiac.casefold().startswith("can"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266890823401542/unknown.png", \
            "June 21st to July 22nd", "Cancer"
    if zodiac.casefold().startswith("le"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266982846427176/unknown.png", \
            "July 23rd to August 22nd", "Leo"
    if zodiac.casefold().startswith("v"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267049380651078/unknown.png", \
            "August 23rd to September 22nd", "Virgo"
    if zodiac.casefold().startswith("li"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927267136232128552/unknown.png", \
            "September 23rd to October 22nd", "Libra"
    if zodiac.casefold().startswith("sc"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267220839596032/unknown.png", \
            "October 23rd to November 21st", "Scorpio"
    if zodiac.casefold().startswith("sa"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267312246075392/unknown.png", \
            "November 22nd to December 21st", "Sagittarius"
    raise Exception("Valid options:\n\n" + ", ".join(f"`{dateToZodiac(monthNumberToName(i) + ' 1')}`" for i in range(1, 13)))


def dateToZodiac(datestr: str, ac=False):
    month, day = datestr.split(" ")
    try:
        day = int(day)
    except:
        day = int(day[:-2])
    month = monthNumberToName(monthNameToNumber(month))
    if month == "December" and day > 21 or month == "January" and day < 20:
        return "Capricorn"
    if month == "January" and day > 19 or month == "February" and day < 19:
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


def fahrenheitToCelsius(value):
    return (value - 32) * 5 / 9


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


def noteFinder(rawNote):
    cycle = ItemCycle(musicalNotes())
    noteandoctave = split(r"(^[^\d]+)", rawNote)[1:]
    octave = int(noteandoctave[1])
    flatsharp = noteandoctave[0][1:].casefold().replace("#", "♯").replace("b", "♭")
    if flatsharp.endswith("-"):
        flatsharp = flatsharp[:-1]
        octave *= -1
    cycle.updateIndex(musicalNotes().index(rawNote[:1].upper()))
    if flatsharp:
        for i in flatsharp:
            if i == "♯":
                cycle.nextItem()
                if musicalNotes()[cycle.getIndex()] == "C":
                    octave += 1
            else:
                cycle.previousItem()
                if musicalNotes()[cycle.getIndex()] == "B":
                    octave -= 1
    return musicalNotes()[cycle.getIndex()] + str(octave), cycle.getIndex() + octave * 12


def reloadCog(client, cog):
    try:
        cog = cog.casefold().replace(' ', '_').replace('.py', '')
        client.reload_extension(f"src.discord_cogs.{cog}")
        print(f"Reloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def loadCog(client, cog):
    try:
        cog = cog.casefold().replace(' ', '_').replace('.py', '')
        client.load_extension(f"src.discord_cogs.{cog}")
        print(f"Loaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def unloadCog(client, cog):
    try:
        cog = cog.casefold().replace(' ', '_').replace('.py', '')
        client.unload_extension(f"src.discord_cogs.{cog}")
        print(f"Unloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


async def deleteTempFile(file: str):
    if path.exists(f"{getPath()}/temp/{file}"):
        await remove(f"{getPath()}/temp/{file}")


async def readTxtAttachment(message):
    attach = message.attachments[0]
    filename = f"{time()}-{attach.filename}"
    filepath = f"{getPath()}/temp/{filename}"
    await attach.save(filepath)
    try:
        content = await readTxt("temp/" + filename)
    except:
        content = None
    await deleteTempFile(filename)
    return content


async def readTxt(pathstr, lines=False):
    async with open(f"{getPath()}/{pathstr}", "r", encoding="utf-8") as f:
        if lines:
            lines = await f.readlines()
            content = [i[:-1] for i in lines if i[:-1]]
        else:
            content = await f.read()
    await f.close()
    return content


async def readJson(pathstr):
    async with open(f"{getPath()}/{pathstr}", "r", encoding="utf-8") as f:
        data = await f.read()
    await f.close()
    return loads(data)


async def dumpJson(pathstr, data):
    async with open(f"{getPath()}/{pathstr}", "w") as f:
        await f.write(dumps(data, sort_keys=True, indent=4))
    await f.close()


async def generateJson(name, data: dict):
    if not path.exists(f"{getPath()}/data/{name}.json"):
        await dumpJson(f"data/{name}.json", data)
        print(f"Generated file: {name}.json")


async def easterEggsPredicate(ctx):
    return ctx.guild and ctx.guild.id in (await readJson("data/easter_eggs.json"))["servers"]


async def getRequest(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return res


async def getImage(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return BytesIO(res.content)


async def sendImage(ctx, url: str, name: str="image.png", message=None):
    try:
        await ctx.reply(message, file=File(await getImage(url), name))
    except:
        try:
            await ctx.send(message, file=File(await getImage(url), name))
        except Exception as ex:
            printError(ctx, ex)


async def sendEmbedToChannels(embed: Embed, channellist: list):
    for channel in channellist:
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass


async def sendTime(ctx, mins, secs):
    await ctx.send(
        "`Elapsed time: {:,} minute{} and {} second{}.`".format(mins, "" if mins == 1 else "s", secs, "" if secs == 1 else "s")
    )


async def postRequest(url, data=None, headers=None, timeout=None, verify=True, json=None):
    async with AsyncClient(verify=verify) as session:
        res = await session.post(url, data=data, headers=headers, timeout=timeout, json=json)
    return res


async def decodeQR(link):
    res = await getRequest("http://api.qrserver.com/v1/read-qr-code", params={"fileurl": link})
    return res.json()[0]["symbol"][0]["data"]


async def userNotBlacklisted(client, message):
    if message.author.id in (await readJson("data/whitelist.json"))["users"]:
        return True
    data = await readJson("data/blacklist.json")
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
    return allowed and message.author.id not in userList \
           and (not message.guild or message.guild.id not in serverList)


async def testKaleido():
    print("Testing Kaleido...")
    try:
        go.Figure().write_image(f"{getPath()}/temp/test.png")
        await deleteTempFile("test.png")
        print("Kaleido installed and ready")
    except:
        raise Exception("Kaleido is not installed!")
