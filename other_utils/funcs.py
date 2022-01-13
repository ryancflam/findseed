import time
from asyncio import TimeoutError, sleep
from calendar import monthrange
from datetime import date, datetime, timedelta
from dateutil import parser
from io import BytesIO
from json import JSONDecodeError, dump, load
from os import path
from re import split

from discord import Embed, File, utils
from httpx import AsyncClient, get

from other_utils.item_cycle import ItemCycle


def getPath():
    return path.dirname(path.realpath(__file__))[:-12]


def readTxtLines(pathstr):
    with open(f"{getPath()}/{pathstr}", "r", encoding="utf-8") as f:
        lines = f.readlines()
    f.close()
    return [i[:-1] for i in lines if i]


def readJson(pathstr):
    with open(f"{getPath()}/{pathstr}", "r", encoding="utf-8") as f:
        data = load(f)
    f.close()
    return data


def dumpJson(pathstr, data):
    with open(f"{getPath()}/{pathstr}", "w") as f:
        dump(data, f, sort_keys=True, indent=4)
    f.close()


def replaceCharacters(string, toreplace: list, replaceto: str=""):
    for char in toreplace:
        string = string.replace(char, replaceto)
    return string


def multiString(string, n: int=2000):
    return [string[i:i + n] for i in range(0, len(string), n)]


def commandIsOwnerOnly(command):
    return "<function is_owner.<locals>.predicate" in [str(i).split(" at")[0] for i in command.checks]


def commandsListEmbed(client, menu: int=0):
    e = Embed(title=f"{'Hidden' if menu == 1 else 'Bot Owner' if menu == 2 else client.user.name} Commands")
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
    zero = f", or {client.command_prefix}category <category> for more information about a specific category"
    e.set_footer(text=f"Use {client.command_prefix}help <command> for help with a specific command{zero if not menu else ''}.")
    return e


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
    return removeDotZero("{:,}".format(sats)) + unit


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


def getZodiacInfo(zodiac: str):
    if zodiac.casefold().startswith("cap"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927265871024513034/unknown.png", \
            "December 22nd to January 19th", "Capricorn"
    elif zodiac.casefold().startswith("aq"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927266052985978960/unknown.png", \
            "January 20th to February 18th", "Aquarius"
    elif zodiac.casefold().startswith("p"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266217725657128/unknown.png", \
            "February 19th to March 20th", "Pisces"
    elif zodiac.casefold().startswith("ar"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266309664825374/unknown.png", \
            "March 21st to April 19th", "Aries"
    elif zodiac.casefold().startswith("t"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266400807030854/unknown.png", \
            "April 20th to May 20th", "Taurus"
    elif zodiac.casefold().startswith("g"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266546101928056/unknown.png", \
            "May 21st to June 20th", "Gemini"
    elif zodiac.casefold().startswith("can"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266890823401542/unknown.png", \
            "June 21st to July 22nd", "Cancer"
    elif zodiac.casefold().startswith("le"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266982846427176/unknown.png", \
            "July 23rd to August 22nd", "Leo"
    elif zodiac.casefold().startswith("v"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267049380651078/unknown.png", \
            "August 23rd to September 22nd", "Virgo"
    elif zodiac.casefold().startswith("li"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927267136232128552/unknown.png", \
            "September 23rd to October 22nd", "Libra"
    elif zodiac.casefold().startswith("sc"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267220839596032/unknown.png", \
            "October 23rd to November 21st", "Scorpio"
    elif zodiac.casefold().startswith("sa"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267312246075392/unknown.png", \
            "November 22nd to December 21st", "Sagittarius"
    else:
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
    timezone = (int(hour) * 3600 + int(minute) * 60) * (-1 if neg else 1)
    dateObj = parser.parse(datestr) + timedelta(seconds=timezone)
    return f"{dateObj.date()} {dateObj.time()}"


def musicalNotes():
    return ["C", "C♯", "D", "E♭", "E", "F", "F♯", "G", "G♯", "A", "B♭", "B"]


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
            time.sleep(30)


async def readTxtAttachment(message):
    attachment = await message.attachments[0].read()
    return attachment.decode("utf-8")


async def reactionRemove(reaction, user):
    try:
        await reaction.remove(user)
    except:
        return


async def removeReactionsFromCache(client, msg):
    for reaction in list(utils.get(client.cached_messages, id=msg.id).reactions):
        async for user in reaction.users():
            await reactionRemove(reaction, user)


async def nextPrevPageOptions(msg, allpages: int):
    await msg.add_reaction("🚫")
    if allpages > 1:
        await msg.add_reaction("⏮")
        await msg.add_reaction("⏭")


async def nextOrPrevPage(client, ctx, msg, allpages: int, page: int):
    try:
        reaction, user = await client.wait_for(
            "reaction_add",
            check=lambda r, u: (str(r.emoji) == "⏮" or str(r.emoji) == "⏭" or str(r.emoji) == "🚫")
                               and u == ctx.author and r.message == msg, timeout=300
        )
    except TimeoutError:
        await removeReactionsFromCache(client, msg)
        return None, 0
    success = False
    if str(reaction.emoji) == "⏭":
        await reactionRemove(reaction, user)
        if page < allpages:
            page += 1
            success = True
    elif str(reaction.emoji) == "⏮":
        await reactionRemove(reaction, user)
        if page > 1:
            page -= 1
            success = True
    else:
        await msg.edit(content="Deleting message...", embed=None)
        await sleep(1)
        await msg.delete()
        success = None
    return success, page


def reloadCog(client, cog):
    try:
        cog = cog.casefold().replace(' ', '_').replace('.py', '')
        client.reload_extension(f"cogs.{cog}")
        print(f"Reloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def loadCog(client, cog):
    try:
        cog = cog.casefold().replace(' ', '_').replace('.py', '')
        client.load_extension(f"cogs.{cog}")
        print(f"Loaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def unloadCog(client, cog):
    try:
        cog = cog.casefold().replace(' ', '_').replace('.py', '')
        client.unload_extension(f"cogs.{cog}")
        print(f"Unloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


async def getRequest(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return res


async def getImage(url, headers=None, params=None, timeout=None, verify=True):
    async with AsyncClient(verify=verify) as session:
        res = await session.get(url, headers=headers, params=params, timeout=timeout)
    return BytesIO(res.content)


async def sendImage(ctx, url: str, name: str="image.png", message=None):
    await ctx.reply(message, file=File(await getImage(url), name))


async def sendEmbedToChannel(channel: int, embed):
    try:
        await channel.send(embed=embed)
    except Exception as ex:
        print(ex)


async def postRequest(url, data=None, headers=None, timeout=None, verify=True, json=None):
    async with AsyncClient(verify=verify) as session:
        res = await session.post(url, data=data, headers=headers, timeout=timeout, json=json)
    return res


async def decodeQR(link):
    res = await getRequest("http://api.qrserver.com/v1/read-qr-code", params={"fileurl": link})
    return res.json()[0]["symbol"][0]["data"]
