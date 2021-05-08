from json import load
from random import choice
from datetime import datetime

from discord import Embed
from discord.ext import commands

from other_utils import funcs

ASSETS_PATH = f"{funcs.getPath()}/assets/animal_crossing"
AC_LOGO = "https://media.discordapp.net/attachments/771698457391136798/" + \
          "774269252232413204/dd98bnh-cdaa0e7e-c5f1-45f9-99fb-5a22d3c2974b.png"


class AnimalCrossing(commands.Cog, name="Animal Crossing", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.art = load(open(f"{ASSETS_PATH}/art.json", "r", encoding="utf8"))
        self.bugs = load(open(f"{ASSETS_PATH}/bugs.json", "r", encoding="utf8"))
        self.fish = load(open(f"{ASSETS_PATH}/fish.json", "r", encoding="utf8"))
        self.fossils = load(open(f"{ASSETS_PATH}/fossils.json", "r", encoding="utf8"))
        self.sea = load(open(f"{ASSETS_PATH}/sea_creatures.json", "r", encoding="utf8"))
        self.villagers = load(open(f"{ASSETS_PATH}/villagers.json", "r", encoding="utf8"))

    @staticmethod
    def findData(data: dict, name: str):
        try:
            return data[name.casefold().replace(" ", "_").replace("'", "").replace("‘", "").replace("’", "")]
        except KeyError:
            raise Exception("Not found, please check your spelling.")

    @staticmethod
    def isArrivingOrLeaving(monthsstr, month, mode):
        args = monthsstr.split(" & ")
        for i in range(len(args)):
            args[i] = args[i].split("-")
            if args[i][mode] == month:
                return True
        return False

    def addCritter(self, data: dict, month, mode):
        north, south = [], []
        for i in data:
            if self.isArrivingOrLeaving(data[i]["availability"]["month-northern"], month, mode):
                north.append(i.replace("_", " ").title())
            if self.isArrivingOrLeaving(data[i]["availability"]["month-southern"], month, mode):
                south.append(i.replace("_", " ").title())
        return sorted(north), sorted(south)

    def crittersListEmbed(self, month, mode: int=0):
        e = Embed(
            title=f"Critters {'Arriving in' if mode == 0 else 'Leaving After'} {funcs.monthNumberToName(month)}"
        ).set_thumbnail(url=AC_LOGO)
        nbugs, sbugs = self.addCritter(self.bugs, month, mode)
        nfish, sfish = self.addCritter(self.fish, month, mode)
        nsea, ssea = self.addCritter(self.sea, month, mode)
        if nbugs:
            e.add_field(name="Bugs (Northern)", value=", ".join(f"`{bug}`" for bug in nbugs))
        if nfish:
            e.add_field(name="Fish (Northern)", value=", ".join(f"`{fish}`" for fish in nfish))
        if nsea:
            e.add_field(name="Sea Creatures (Northern)", value=", ".join(f"`{sea}`" for sea in nsea))
        if sbugs:
            e.add_field(name="Bugs (Southern)", value=", ".join(f"`{bug}`" for bug in sbugs))
        if sfish:
            e.add_field(name="Fish (Southern)", value=", ".join(f"`{fish}`" for fish in sfish))
        if ssea:
            e.add_field(name="Sea Creatures (Southern)", value=", ".join(f"`{sea}`" for sea in ssea))
        if not nbugs and not nfish and not nsea and not sbugs and not sfish and not ssea:
            e = funcs.errorEmbed(None, "Invalid month.")
        e.set_footer(
            text=f"Use {self.client.command_prefix}acbug, {self.client.command_prefix}acfish, or " + \
                 f"{self.client.command_prefix}acsea for specific critter information."
        )
        return e

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acnew", description="Returns a list of critters arriving in a " + \
                                                "particular month in Animal Crossing: New Horizons.",
                      aliases=["acn", "acarriving", "acarrive"], usage="[month]")
    async def acnew(self, ctx, month=""):
        month = month or str(datetime.now().month)
        try:
            _ = int(month)
        except ValueError:
            month = funcs.monthNameToNumber(month)
        await ctx.send(embed=self.crittersListEmbed(month))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acleaving", description="Returns a list of critters leaving after a " + \
                                                    "particular month in Animal Crossing: New Horizons.",
                      aliases=["acl", "acleave"], usage="[month]")
    async def acleaving(self, ctx, month=""):
        month = month or str(datetime.now().month)
        try:
            _ = int(month)
        except ValueError:
            month = funcs.monthNameToNumber(month)
        await ctx.send(embed=self.crittersListEmbed(month, mode=-1))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acart", description="Shows information about an Animal Crossing: New Horizons artwork.",
                      aliases=["art", "acnhart", "artwork", "acartwork", "acnhartwork", "aca"], usage="<artwork name>")
    async def acart(self, ctx, *, art):
        try:
            artdata = self.findData(self.art, art)
            e = Embed(title=artdata["name"]["name-USen"].title(), description=artdata["museum-desc"])
            e.add_field(name="Has Fake", value=f"`{str(artdata['hasFake'])}`")
            e.add_field(name="Buy Price", value="`{:,}`".format(artdata['buy-price']))
            e.add_field(name="Sell Price", value="`{:,}`".format(artdata['sell-price']))
            e.set_image(url=artdata["image_uri"])
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acbug", description="Shows information about an Animal Crossing: New Horizons bug.",
                      aliases=["bug", "acnhbug", "acb"], usage="<bug name>")
    async def acbug(self, ctx, *, bug):
        try:
            bugdata = self.findData(self.bugs, bug)
            northmonths = bugdata["availability"]["month-northern"] if bugdata["availability"]["month-northern"] != "" \
                          else "All Year"
            southmonths = bugdata["availability"]["month-southern"] if bugdata["availability"]["month-southern"] != "" \
                          else "All Year"
            time = bugdata["availability"]["time"] if bugdata["availability"]["time"] != "" else "All Day"
            e = Embed(description=bugdata["museum-phrase"])
            try:
                catchphrases = bugdata["alt-catch-phrase"]
                catchphrases.append(bugdata["catch-phrase"])
            except:
                catchphrases = [bugdata["catch-phrase"]]
            e.set_footer(text='"{}"'.format(choice(catchphrases)))
            e.set_author(name=bugdata["name"]["name-USen"].title().replace("'S", "'s"), icon_url=bugdata["icon_uri"])
            e.add_field(name="Location", value=f"`{bugdata['availability']['location']}`")
            e.add_field(name="Rarity", value=f"`{bugdata['availability']['rarity']}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value="`{:,}`".format(bugdata['price']))
            e.add_field(name="Sell Price (Flick)", value="`{:,}`".format(bugdata['price-flick']))
            e.set_image(url=bugdata["image_uri"])
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acfish", description="Shows information about an Animal Crossing: New Horizons fish.",
                      aliases=["fish", "acnhfish", "acf"], usage="<fish name>")
    async def acfish(self, ctx, *, fish):
        try:
            fishdata = self.findData(self.fish, fish)
            northmonths = fishdata["availability"]["month-northern"] if fishdata["availability"]["month-northern"] != "" \
                          else "All Year"
            southmonths = fishdata["availability"]["month-southern"] if fishdata["availability"]["month-southern"] != "" \
                          else "All Year"
            time = fishdata["availability"]["time"] if fishdata["availability"]["time"] != "" else "All Day"
            e = Embed(description=fishdata["museum-phrase"])
            try:
                catchphrases = fishdata["alt-catch-phrase"]
                catchphrases.append(fishdata["catch-phrase"])
            except:
                catchphrases = [fishdata["catch-phrase"]]
            e.set_footer(text='"{}"'.format(choice(catchphrases)))
            e.set_author(name=fishdata["name"]["name-USen"].title().replace("'S", "'s"), icon_url=fishdata["icon_uri"])
            e.add_field(name="Shadow",value=f"`{fishdata['shadow']}`")
            e.add_field(name="Location", value=f"`{fishdata['availability']['location']}`")
            e.add_field(name="Rarity", value=f"`{fishdata['availability']['rarity']}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value="`{:,}`".format(fishdata['price']))
            e.add_field(name="Sell Price (C.J.)", value="`{:,}`".format(fishdata['price-cj']))
            e.set_image(url=fishdata["image_uri"])
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acfossil", description="Shows information about an Animal Crossing: New Horizons fossil.",
                      aliases=["fossil", "acnhfossil"], usage="<fossil name>")
    async def acfossil(self, ctx, *, fossil):
        try:
            fossildata = self.findData(self.fossils, fossil)
            e = Embed(title=fossildata["name"]["name-USen"].title().replace("'S", "'s"),
                      description=fossildata["museum-phrase"])
            e.add_field(name="Sell Price", value="`{:,}`".format(fossildata['price']))
            e.add_field(name="Part Of", value=f"`{fossildata['part-of'].title()}`")
            e.set_image(url=fossildata["image_uri"])
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acsea", description="Shows information about an Animal Crossing: New Horizons sea creature.",
                      aliases=["sea", "acnhsea", "sc", "acsc", "acnhsc", "acs"], usage="<sea creature name>")
    async def acsea(self, ctx, *, sea):
        try:
            seadata = self.findData(self.sea, sea)
            northmonths = seadata["availability"]["month-northern"] if seadata["availability"]["month-northern"] != "" \
                          else "All Year"
            southmonths = seadata["availability"]["month-southern"] if seadata["availability"]["month-southern"] != "" \
                          else "All Year"
            time = seadata["availability"]["time"] if seadata["availability"]["time"] != "" else "All Day"
            e = Embed(description=seadata["museum-phrase"])
            e.set_footer(text='"{}"'.format(seadata["catch-phrase"]))
            e.set_author(name=seadata["name"]["name-USen"].title().replace("'S", "'s"), icon_url=seadata["icon_uri"])
            e.add_field(name="Shadow",value=f"`{seadata['shadow']}`")
            e.add_field(name="Speed",value=f"`{seadata['speed']}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value="`{:,}`".format(seadata["price"]))
            e.set_image(url=seadata["image_uri"])
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acvillager", description="Shows information about an Animal Crossing: New Horizons villager.",
                      aliases=["villager", "acnhvillager", "acv", "vil", "acvil", "acnhvil"], usage="<villager name>")
    async def acvillager(self, ctx, *, villager):
        try:
            found, villagerdata = False, None
            for villagerID in list(self.villagers):
                villagerdata = self.villagers[villagerID]
                if villagerdata["name"]["name-USen"].casefold().replace(" ", "_") \
                        == villager.casefold().replace(" ", "_").replace("‘", "'").replace("’", "'"):
                    found = True
                    break
            if not found:
                return await ctx.send(embed=funcs.errorEmbed(None, "Not found, please check your spelling."))
            e = Embed(description='"' + villagerdata["saying"] + '"')
            e.set_author(name=villagerdata["name"]["name-USen"].title(), icon_url=villagerdata["icon_uri"])
            e.set_image(url=villagerdata["image_uri"])
            e.set_thumbnail(url=AC_LOGO)
            e.add_field(name="Personality", value=f"`{villagerdata['personality']}`")
            e.add_field(name="Birthday", value=f"`{villagerdata['birthday-string']}`")
            e.add_field(name="Species", value="`{}`".format(f'{villagerdata["species"]} ({villagerdata["subtype"]})'))
            e.add_field(name="Gender", value=f"`{villagerdata['gender']}`")
            e.add_field(name="Hobby", value=f"`{villagerdata['hobby']}`")
            e.add_field(name="Initial Phrase", value='`"{}"`'.format(villagerdata["catch-phrase"]))
        except Exception as ex:
            e = funcs.errorEmbed(None, f"An error occurred - {ex}")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(AnimalCrossing(client))
