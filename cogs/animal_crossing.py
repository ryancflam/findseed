from json import load

from discord import Embed
from discord.ext import commands

from other_utils import funcs

ASSETS_PATH = f"{funcs.getPath()}/assets/animal_crossing"
AC_LOGO = "https://media.discordapp.net/attachments/771698457391136798/" + \
          "774269252232413204/dd98bnh-cdaa0e7e-c5f1-45f9-99fb-5a22d3c2974b.png"


class AnimalCrossing(commands.Cog, name="Animal Crossing"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.art = load(open(f"{ASSETS_PATH}/art.json", "r", encoding="utf8"))
        self.bugs = load(open(f"{ASSETS_PATH}/bugs.json", "r", encoding="utf8"))
        self.fish = load(open(f"{ASSETS_PATH}/fish.json", "r", encoding="utf8"))
        self.fossils = load(open(f"{ASSETS_PATH}/fossils.json", "r", encoding="utf8"))
        self.sea = load(open(f"{ASSETS_PATH}/sea_creatures.json", "r", encoding="utf8"))
        self.villagers = load(open(f"{ASSETS_PATH}/villagers.json", "r", encoding="utf8"))

    @staticmethod
    def findData(data, datatype: str):
        try:
            return data[datatype.casefold().replace(" ", "_").replace("'", "").replace("‘", "").replace("’", "")]
        except KeyError:
            raise Exception("Not found, please check your spelling.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acart", description="Shows information about an Animal Crossing: New Horizons artwork.",
                      aliases=["art", "acnhart", "artwork", "acartwork", "acnhartwork", "aca"], usage="<artwork name>")
    async def acart(self, ctx, *, art):
        try:
            artdata = self.findData(self.art, art)
            artname = artdata["name"]["name-USen"].title()
            hasFake = str(artdata["hasFake"])
            buyPrice = str(artdata["buy-price"])
            sellPrice = str(artdata["sell-price"])
            img = artdata["image_uri"]
            desc = artdata["museum-desc"]
            e = Embed(title=artname, description=desc)
            e.add_field(name="Has Fake", value=f"`{hasFake}`")
            e.add_field(name="Buy Price", value=f"`{buyPrice}`")
            e.add_field(name="Sell Price", value=f"`{sellPrice}`")
            e.set_image(url=img)
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
            bugname = bugdata["name"]["name-USen"].title().replace("'S", "'s")
            northmonths = bugdata["availability"]["month-northern"] if bugdata["availability"]["month-northern"] != "" \
                else "All Year"
            southmonths = bugdata["availability"]["month-southern"] if bugdata["availability"]["month-southern"] != "" \
                else "All Year"
            time = bugdata["availability"]["time"] if bugdata["availability"]["time"] != "" else "All Day"
            price = bugdata["price"]
            flickprice = bugdata["price-flick"]
            catch = '"{}"'.format(bugdata["catch-phrase"])
            location = bugdata["availability"]["location"]
            rarity = bugdata["availability"]["rarity"]
            img = bugdata["image_uri"]
            e = Embed(title=bugname, description=catch)
            e.add_field(name="Location", value=f"`{location}`")
            e.add_field(name="Rarity", value=f"`{rarity}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value=f"`{price}`")
            e.add_field(name="Sell Price (Flick)", value=f"`{flickprice}`")
            e.set_image(url=img)
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
            fishname = fishdata["name"]["name-USen"].title().replace("'S", "'s")
            northmonths = fishdata["availability"]["month-northern"] if fishdata["availability"]["month-northern"] != "" \
                else "All Year"
            southmonths = fishdata["availability"]["month-southern"] if fishdata["availability"]["month-southern"] != "" \
                else "All Year"
            time = fishdata["availability"]["time"] if fishdata["availability"]["time"] != "" else "All Day"
            price = fishdata["price"]
            cjprice = fishdata["price-cj"]
            catch = '"{}"'.format(fishdata["catch-phrase"])
            location = fishdata["availability"]["location"]
            rarity = fishdata["availability"]["rarity"]
            shadow = fishdata["shadow"]
            img = fishdata["image_uri"]
            e = Embed(title=fishname, description=catch)
            e.add_field(name="Shadow",value=f"`{shadow}`")
            e.add_field(name="Location", value=f"`{location}`")
            e.add_field(name="Rarity", value=f"`{rarity}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value=f"`{price}`")
            e.add_field(name="Sell Price (C.J.)", value=f"`{cjprice}`")
            e.set_image(url=img)
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
            fossilname = fossildata["name"]["name-USen"].title().replace("'S", "'s")
            price = fossildata["price"]
            phrase = fossildata["museum-phrase"]
            partof = fossildata["part-of"].title()
            img = fossildata["image_uri"]
            e = Embed(title=fossilname, description=phrase)
            e.add_field(name="Sell Price", value=f"`{price}`")
            e.add_field(name="Part Of", value=f"`{partof}`")
            e.set_image(url=img)
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
            seaname = seadata["name"]["name-USen"].title().replace("'S", "'s")
            price = seadata["price"]
            northmonths = seadata["availability"]["month-northern"] if seadata["availability"]["month-northern"] != "" \
                else "All Year"
            southmonths = seadata["availability"]["month-southern"] if seadata["availability"]["month-southern"] != "" \
                else "All Year"
            time = seadata["availability"]["time"] if seadata["availability"]["time"] != "" else "All Day"
            speed = seadata["speed"]
            shadow = seadata["shadow"]
            catch = '"{}"'.format(seadata["catch-phrase"])
            img = seadata["image_uri"]
            e = Embed(title=seaname, description=catch)
            e.add_field(name="Shadow",value=f"`{shadow}`")
            e.add_field(name="Speed",value=f"`{speed}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value=f"`{price}`")
            e.set_image(url=img)
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
                if villagerdata["name"]["name-USen"].casefold().replace(" ", "_") == villager.casefold().replace(" ", "_"):
                    found = True
                    break
            if not found:
                return await ctx.send(embed=funcs.errorEmbed(None, "Not found, please check your spelling."))
            villagername = villagerdata["name"]["name-USen"].title()
            personality = villagerdata["personality"]
            birth = villagerdata["birthday-string"]
            species = f'{villagerdata["species"]} ({villagerdata["subtype"]})'
            gender = villagerdata["gender"]
            phrase = villagerdata["catch-phrase"]
            saying = villagerdata["saying"]
            hobby = villagerdata["hobby"]
            image = villagerdata["image_uri"]
            e = Embed(title=f"{villagername}", description=f'"{saying}"')
            e.set_image(url=image)
            e.set_thumbnail(url=AC_LOGO)
            e.add_field(name="Personality", value=f"`{personality}`")
            e.add_field(name="Birthday", value=f"`{birth}`")
            e.add_field(name="Species", value=f"`{species}`")
            e.add_field(name="Gender", value=f"`{gender}`")
            e.add_field(name="Hobby", value=f"`{hobby}`")
            e.add_field(name="Initial Phrase", value='`"{}"`'.format(phrase))
        except Exception as ex:
            e = funcs.errorEmbed(None, f"An error occurred - {ex}")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(AnimalCrossing(client))
