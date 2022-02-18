from re import split

from PIL import Image
from pyzbar.pyzbar import decode

from src.utils.funcs.http_requests import getImageFile
from src.utils.funcs.math_and_numbers import randomHex
from src.utils.funcs.string_manipulation import monthNameToNumber, monthNumberToName
from src.utils.item_cycle import ItemCycle

MUSICAL_NOTES = ["C", "C♯", "D", "E♭", "E", "F", "F♯", "G", "G♯", "A", "B♭", "B"]


def noteFinder(raw):
    cycle = ItemCycle(MUSICAL_NOTES)
    noteandoctave = split(r"(^[^\d]+)", raw)[1:]
    octave = int(noteandoctave[1])
    flatsharp = noteandoctave[0][1:].casefold().replace("#", "♯").replace("b", "♭")
    if flatsharp.endswith("-"):
        flatsharp = flatsharp[:-1]
        octave *= -1
    cycle.updateIndex(MUSICAL_NOTES.index(raw[:1].upper()))
    if flatsharp:
        for i in flatsharp:
            if i == "♯":
                cycle.nextItem()
                if MUSICAL_NOTES[cycle.getIndex()] == "C":
                    octave += 1
            else:
                cycle.previousItem()
                if MUSICAL_NOTES[cycle.getIndex()] == "B":
                    octave -= 1
    return MUSICAL_NOTES[cycle.getIndex()] + str(octave), cycle.getIndex() + octave * 12


def getZodiacInfo(zodiac: str):
    zodiac = zodiac.casefold()
    if zodiac.startswith("cap"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927265871024513034/unknown.png", \
            "December 22nd to January 19th", "Capricorn"
    if zodiac.startswith("aq"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927266052985978960/unknown.png", \
            "January 20th to February 18th", "Aquarius"
    if zodiac.startswith("p"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266217725657128/unknown.png", \
            "February 19th to March 20th", "Pisces"
    if zodiac.startswith("ar"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266309664825374/unknown.png", \
            "March 21st to April 19th", "Aries"
    if zodiac.startswith("t"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266400807030854/unknown.png", \
            "April 20th to May 20th", "Taurus"
    if zodiac.startswith("g"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266546101928056/unknown.png", \
            "May 21st to June 20th", "Gemini"
    if zodiac.startswith("can"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266890823401542/unknown.png", \
            "June 21st to July 22nd", "Cancer"
    if zodiac.startswith("le"):
        return "https://media.discordapp.net/attachments/771698457391136798/927266982846427176/unknown.png", \
            "July 23rd to August 22nd", "Leo"
    if zodiac.startswith("v"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267049380651078/unknown.png", \
            "August 23rd to September 22nd", "Virgo"
    if zodiac.startswith("li"):
        return "https://cdn.discordapp.com/attachments/771698457391136798/927267136232128552/unknown.png", \
            "September 23rd to October 22nd", "Libra"
    if zodiac.startswith("sc"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267220839596032/unknown.png", \
            "October 23rd to November 21st", "Scorpio"
    if zodiac.startswith("sa"):
        return "https://media.discordapp.net/attachments/771698457391136798/927267312246075392/unknown.png", \
            "November 22nd to December 21st", "Sagittarius"
    raise Exception("Valid options:\n\n" + ", ".join(
        f"`{dateToZodiac(monthNumberToName(i) + ' 1')}`" for i in range(1, 13)
    ))


def dateToZodiac(datestr: str, ac: bool=False):
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


def githubRepoPic(repo):
    return f"https://opengraph.githubassets.com/{randomHex(64)}/{repo}"


async def decodeQR(link):
    img = Image.open(await getImageFile(link, file=False))
    data = decode(img)
    img.close()
    res = ""
    for i in data:
        res += i.data.decode("utf-8") + "\n"
    return res[:-1] if res else None
