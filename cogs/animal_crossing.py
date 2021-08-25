# Hidden category

from asyncio import TimeoutError
from datetime import datetime
from random import choice

from discord import Embed
from discord.ext import commands

from other_utils import funcs

AC_LOGO = "https://i.imgur.com/kbWPgBd.png"


class AnimalCrossing(commands.Cog, name="Animal Crossing", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.art = funcs.readJson("assets/animal_crossing/art.json")
        self.bugs = funcs.readJson("assets/animal_crossing/bugs.json")
        self.fish = funcs.readJson("assets/animal_crossing/fish.json")
        self.fossils = funcs.readJson("assets/animal_crossing/fossils.json")
        self.personalities = funcs.readJson("assets/animal_crossing/personalities.json")
        self.sea = funcs.readJson("assets/animal_crossing/sea_creatures.json")
        self.species = funcs.readJson("assets/animal_crossing/species.json")
        self.villagers = funcs.readJson("assets/animal_crossing/villagers.json")

    @staticmethod
    def findData(data: dict, name: str):
        try:
            return data[name.casefold().replace(" ", "_").replace("'", "").replace("‘", "")
                        .replace("’", "").replace("rock_head", "rock-head")]
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
        month = month or str(datetime.now().month)
        try:
            _ = int(month)
        except ValueError:
            try:
                month = funcs.monthNameToNumber(month)
            except Exception as ex:
                return funcs.errorEmbed(None, str(ex))
        try:
            e = Embed(
                title=f"Critters {'Arriving in' if not mode else 'Leaving After'} {funcs.monthNumberToName(month)}"
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
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        return e

    async def furnitureEmbed(self, ctx, ftype: str, name: str):
        name = name.replace(" ", "_").replace("‘", "'").replace("’", "'")
        try:
            res = await funcs.getRequest(f"https://acnhapi.com/v1/{ftype}/{name}")
            data = res.json()
            if len(data) > 1:
                await ctx.send(
                    "`Please select a number: {}`".format(
                        ", ".join(f"{str(var)} ({data[var]['variant']})" for var in range(len(data)))
                    )
                )
                try:
                    pchoice = await self.client.wait_for(
                        "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel, timeout=20
                    )
                    variant = int(pchoice.content) if -1 < int(pchoice.content) < len(data) else 0
                except (TimeoutError, ValueError):
                    variant = 0
            else:
                variant = 0
            tags = [
                i for i in [
                    "DIY" if data[variant]["isDIY"] else 0,
                    "Catalogue" if data[variant]["isCatalog"] else 0,
                    "Customisable Body" if data[variant]["canCustomizeBody"] else 0,
                    "Customisable Pattern" if data[variant]["canCustomizePattern"] else 0,
                    "Interactive" if data[variant]["isInteractive"] else 0,
                    "Outdoor" if data[variant]["isOutdoor"] else 0
                ] if i
            ]
            try:
                if data[variant]["isDoorDeco"]:
                    tags.append("Door Decoration")
            except:
                pass
            e = Embed(title=data[variant]["name"]["name-USen"])
            e.set_image(url=data[variant]["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
            e.add_field(name="Type", value="`{}`".format(data[variant]['tag'].title().replace("'S", "'s")))
            e.add_field(name="Source", value=f"`{data[variant]['source']}`")
            e.add_field(name="Size", value=f"`{data[variant]['size']}`")
            e.add_field(name="Version Added", value=f"`{data[variant]['version']}`")
            if tags:
                e.add_field(name="Tags", value=", ".join(f"`{i}`" for i in tags))
            if data[variant]["variant"]:
                e.add_field(name="Variant", value=f"`{data[variant]['variant']}`")
            if data[variant]["body-title"]:
                e.add_field(name="Body Title", value=f"`{data[variant]['body-title']}`")
            if data[variant]["pattern"]:
                e.add_field(name="Pattern", value=f"`{data[variant]['pattern']}`")
            if data[variant]["pattern-title"]:
                e.add_field(name="Pattern-Title", value=f"`{data[variant]['pattern-title']}`")
            if data[variant]["kit-cost"]:
                e.add_field(name="Kit Cost", value=f"`{data[variant]['kit-cost']}`")
            if data[variant]["color-1"]:
                e.add_field(name="Colour", value=f"`{data[variant]['color-1']}`")
            if data[variant]["color-2"]:
                e.add_field(name="Secondary Colour", value=f"`{data[variant]['color-2']}`")
            if data[variant]["hha-concept-1"]:
                e.add_field(
                    name="HHA Concept", value="`{}`".format(data[variant]['hha-concept-1'].title().replace("'S", "'s"))
                )
            if data[variant]["hha-concept-2"]:
                e.add_field(
                    name="Secondary HHA Concept", value="`{}`".format(data[variant]['hha-concept-2'].title().replace("'S", "'s"))
                )
            if data[variant]["hha-series"]:
                e.add_field(name="HHA Series", value="`{}`".format(data[variant]['hha-series'].title().replace("'S", "'s")))
            if data[variant]["hha-set"]:
                e.add_field(name="HHA Set", value="`{}`".format(data[variant]['hha-set'].title().replace("'S", "'s")))
            try:
                if data[variant]["speaker-type"]:
                    e.add_field(name="Speaker Type", value=f"`{data[variant]['speaker-type']}`")
            except:
                pass
            if data[variant]["lighting-type"]:
                e.add_field(name="Lighting Type", value=f"`{data[variant]['lighting-type']}`")
            if data[variant]["buy-price"]:
                e.add_field(name="Buy Price", value="`{:,}`".format(data[variant]["buy-price"]))
            e.add_field(name="Sell Price", value="`{:,}`".format(data[variant]["sell-price"]))
        except Exception:
            e = funcs.errorEmbed(
                None, "Not found, please check your spelling. Furniture names are case sensitive." + \
                      " (e.g. `acoustic guitar` or `Bunny Day arch`)\n\nOr is this even the right category? " + \
                      f"(houseware, wallmounted, misc)"
            )
        return e

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="acnew", description="Returns a list of critters arriving in a " + \
                                                "particular month in Animal Crossing: New Horizons.",
                      aliases=["acn", "acarriving", "acarrive"], usage="[month]")
    async def acnew(self, ctx, month=""):
        await ctx.send(embed=self.crittersListEmbed(month))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="acleaving", description="Returns a list of critters leaving after a " + \
                                                    "particular month in Animal Crossing: New Horizons.",
                      aliases=["acl", "acleave"], usage="[month]")
    async def acleaving(self, ctx, month=""):
        await ctx.send(embed=self.crittersListEmbed(month, mode=-1))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="acart", description="Shows information about an Animal Crossing: New Horizons artwork.",
                      aliases=["art", "acnhart", "artwork", "acartwork", "acnhartwork", "aca"], usage="<artwork name>")
    async def acart(self, ctx, *, art):
        try:
            artdata = self.findData(self.art, art.replace("(", "").replace(")", ""))
            e = Embed(title=artdata["name"]["name-USen"].title(), description=artdata["museum-desc"])
            e.add_field(name="Has Fake", value=f"`{str(artdata['hasFake'])}`")
            e.add_field(name="Buy Price", value="`{:,}`".format(artdata['buy-price']))
            e.add_field(name="Sell Price", value="`{:,}`".format(artdata['sell-price']))
            e.set_image(url=artdata["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
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
            e.set_footer(
                text='"{}"'.format(choice(catchphrases).replace('"', "'").replace("Walker ...", f"Walker {ctx.author.name}"))
            )
            e.set_author(name=bugdata["name"]["name-USen"].title().replace("'S", "'s"),
                         icon_url=bugdata["icon_uri"].replace("https", "http"))
            e.add_field(name="Location", value=f"`{bugdata['availability']['location']}`")
            e.add_field(name="Rarity", value=f"`{bugdata['availability']['rarity']}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value="`{:,}`".format(bugdata['price']))
            e.add_field(name="Sell Price (Flick)", value="`{:,}`".format(bugdata['price-flick']))
            e.set_image(url=bugdata["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
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
            e.set_footer(text='"{}"'.format(choice(catchphrases).replace('"', "'")))
            e.set_author(name=fishdata["name"]["name-USen"].title().replace("'S", "'s"),
                         icon_url=fishdata["icon_uri"].replace("https", "http"))
            e.add_field(name="Shadow",value=f"`{fishdata['shadow']}`")
            e.add_field(name="Location", value=f"`{fishdata['availability']['location']}`")
            e.add_field(name="Rarity", value=f"`{fishdata['availability']['rarity']}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value="`{:,}`".format(fishdata['price']))
            e.add_field(name="Sell Price (C.J.)", value="`{:,}`".format(fishdata['price-cj']))
            e.set_image(url=fishdata["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="acfossil", description="Shows information about an Animal Crossing: New Horizons fossil.",
                      aliases=["acnhfossil", "acfossils", "acnhfossils"], usage="<fossil name>")
    async def acfossil(self, ctx, *, fossil):
        try:
            fossildata = self.findData(self.fossils, fossil)
            e = Embed(title=fossildata["name"]["name-USen"].title().replace("'S", "'s"),
                      description=fossildata["museum-phrase"])
            e.add_field(name="Sell Price", value="`{:,}`".format(fossildata['price']))
            e.add_field(name="Part Of", value=f"`{fossildata['part-of'].title()}`")
            e.set_image(url=fossildata["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="acpersonality", usage="[personality type]",
                      aliases=["acp", "acnhpersonality", "acpersonalities", "acnhpersonalities"],
                      description="Shows information about an Animal Crossing: New Horizons villager personality.")
    async def acpersonality(self, ctx, *, personality: str=""):
        personality = personality.casefold().replace(" ", "").replace("-", "").replace("_", "").replace("uchi", "sisterly") \
                      .replace("bigsister", "sisterly").replace("snobby", "snooty").replace("grumpy", "cranky")
        if not personality:
            e = Embed(title="Animal Crossing Personality Types",
                      description="`cranky`, `jock`, `lazy`, `normal`, `peppy`, `sisterly`, `smug`, `snooty`")
            e.set_footer(text=f"Use {self.client.command_prefix}acpersonality <personality type> for more information.")
            e.set_thumbnail(url=AC_LOGO)
        else:
            try:
                personalitydata = self.findData(self.personalities, personality)
                e = Embed(title=personalitydata["name"],
                          description=personalitydata["desc"])
                e.add_field(name="Gender", value=f"`{personalitydata['gender']}`")
                e.add_field(name="Sleep Time", value=f"`{personalitydata['sleep-time']}`")
                e.add_field(name="Total Villagers", value=f"`{personalitydata['total']}`")
                e.add_field(name="Get Along With", value=", ".join(f"`{i}`" for i in personalitydata["get-along-with"]))
                if personalitydata["fight-with"]:
                    e.add_field(name="Fight With", value=", ".join(f"`{i}`" for i in personalitydata["fight-with"]))
                e.set_thumbnail(url=AC_LOGO)
            except Exception as ex:
                e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
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
            e.set_author(name=seadata["name"]["name-USen"].title().replace("'S", "'s"),
                         icon_url=seadata["icon_uri"].replace("https", "http"))
            e.add_field(name="Shadow",value=f"`{seadata['shadow']}`")
            e.add_field(name="Speed",value=f"`{seadata['speed']}`")
            e.add_field(name="Northern Months", value=f"`{northmonths}`")
            e.add_field(name="Southern Months", value=f"`{southmonths}`")
            e.add_field(name="Time", value=f"`{time}`")
            e.add_field(name="Sell Price", value="`{:,}`".format(seadata["price"]))
            e.set_image(url=seadata["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
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
            e.set_author(name=villagerdata["name"]["name-USen"].title(), icon_url=villagerdata["icon_uri"].replace("https", "http"))
            e.set_image(url=villagerdata["image_uri"].replace("https", "http"))
            e.set_thumbnail(url=AC_LOGO)
            e.add_field(
                name="Personality",
                value="`{}`".format(f'{villagerdata["personality"].replace("Uchi", "Sisterly")} ({villagerdata["subtype"]})')
            )
            e.add_field(name="Birthday", value=f"`{villagerdata['birthday-string']}`")
            e.add_field(name="Species", value=f"`{villagerdata['species']}`")
            e.add_field(name="Gender", value=f"`{villagerdata['gender']}`")
            e.add_field(name="Hobby", value=f"`{villagerdata['hobby']}`")
            e.add_field(name="Initial Phrase", value='`"{}"`'.format(villagerdata["catch-phrase"]))
            prob = len(list(self.species.keys())) * self.species[villagerdata["species"]]
            e.add_field(inline=False, name="NMT Probability", value="`1 in {:,}`".format(prob))
        except Exception as ex:
            e = funcs.errorEmbed(None, f"An error occurred - {ex}")
        await ctx.send(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="acspecies", description="Shows information about an Animal Crossing: New Horizons villager species.",
                      aliases=["species"])
    async def acspecies(self, ctx, *, species: str=""):
        try:
            species = species.replace(" ", "").title()
            value = self.species[species]
            e = Embed(title=species)
            e.set_thumbnail(url=AC_LOGO)
            villagers = []
            for i in list(self.villagers):
                data = self.villagers[i]
                if data["species"] == species:
                    villagers.append(data["name"]["name-USen"].title())
            e.add_field(name=f"Villagers ({value})", value=", ".join(f"`{i}`" for i in sorted(villagers)))
            prob = len(list(self.species.keys())) * value
            e.add_field(inline=False, name="Villager NMT Probability", value="`1 in {:,}`".format(prob))
        except KeyError:
            e = funcs.errorEmbed(
                    "Invalid option!",
                    "Valid options:\n\n{}".format(", ".join(f"`{opt}`" for opt in self.species.keys()))
            )
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="achouseware", aliases=["houseware", "acnhhouseware", "ach"], usage="<item name (case sensitive)>",
                      description="Shows information about an Animal Crossing: New Horizons houseware furniture item.")
    async def achouseware(self, ctx, *, item):
        await ctx.send(embed=await self.furnitureEmbed(ctx, "houseware", item))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acwallmounted", aliases=["wallmounted", "acnhwallmounted", "acw", "acwall"],
                      usage="<item name (case sensitive)>",
                      description="Shows information about an Animal Crossing: New Horizons wallmounted furniture item.")
    async def acwallmounted(self, ctx, *, item):
        await ctx.send(embed=await self.furnitureEmbed(ctx, "wallmounted", item))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="acmisc", aliases=["acnhmisc", "acm"], usage="<item name (case sensitive)>",
                      description="Shows information about an Animal Crossing: New Horizons miscellaneous furniture item.")
    async def acmisc(self, ctx, *, item):
        await ctx.send(embed=await self.furnitureEmbed(ctx, "misc", item))


def setup(client: commands.Bot):
    client.add_cog(AnimalCrossing(client))
