from time import time
from scipy import stats
from base64 import b64decode
from json import load, loads, dump

from discord import Embed, File
from discord.ext import commands

from assets import eye_data
from other_utils import funcs


class Minecraft(commands.Cog, name="Minecraft"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="findseed", description="Everyone's favourite command.",
                      aliases=["fs", "eye", "eyes", "seed", "f", "s"])
    async def findseed(self, ctx):
        eyes = funcs.randomEyes()
        with open(f"{funcs.getPath()}/data.json", "r", encoding="utf-8") as f:
            data = load(f)
        f.close()
        odds = eye_data.eyeData[str(eyes)]["percent"]
        onein = eye_data.eyeData[str(eyes)]["onein"]
        if eyes >= data["highest"]["number"]:
            if eyes > data["highest"]["number"]:
                data["highest"]["found"] = 1
            else:
                data["highest"]["found"] += 1
            data["highest"]["number"] = eyes
            data["highest"]["time"] = int(time())
            update = True
        else:
            update = False
        highest = data["highest"]["number"]
        highestTime = data["highest"]["time"]
        highestTotal = data["highest"]["found"]
        data["calls"] += 1
        calls = data["calls"]
        with open(f"{funcs.getPath()}/data.json", "w") as f:
            dump(data, f, sort_keys=True, indent=4)
        f.close()
        file = File(f"{funcs.getPath()}/assets/{eyes}eye.png", filename="portal.png")
        if not update:
            foundTime = f"{funcs.timeDifferenceStr(time(), highestTime)}"
        else:
            foundTime = "just now"
        e = Embed(
            title="!findseed",
            description=f"{ctx.message.author.mention} --> Your seed is a **{eyes} eye**."
        )
        e.add_field(name="Probability", value=f"`{odds}% (1 in {onein})`")
        e.add_field(name="Most Eyes Found", value=f"`{highest} (last found {foundTime}{' ago' if not update else ''}" + \
                                                  f", found {highestTotal} time{'' if highestTotal==1 else 's'})`")
        e.set_footer(text=f"The command has been called {calls} time{'' if calls==1 else 's'}. !eyeodds")
        e.set_image(url="attachment://portal.png")
        await ctx.send(embed=e, file=file)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="eyeodds", description="Shows the odds of getting each type of end portal.",
                      aliases=["odds", "eo", "odd", "o"])
    async def eyeodds(self, ctx):
        msg = ""
        for i in range(13):
            odds = eye_data.eyeData[str(i)]["percent"]
            msg += f"{i} eye - `{odds}% (1 in {eye_data.eyeData[str(i)]['onein']})`\n"
        await ctx.send(msg)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="skin", description="Gets the skin of a Minecraft user.", aliases=["mcskin"],
                      usage="[username]")
    async def skin(self, ctx, username: str=""):
        if username == "":
            username = ctx.message.author.name
        try:
            data = await funcs.getRequest(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            username = data.json()["name"]
            res = await funcs.getRequest(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{str(data.json()['id'])}"
            )
            data = b64decode(res.json()["properties"][0]["value"])
            data = loads(data)
            skin = data["textures"]["SKIN"]["url"]
            e = Embed(
                title="Minecraft User",
                description=f"**{username}**"
            )
            e.set_image(url=skin)
        except Exception:
            e = funcs.errorEmbed(None, "Invalid skin or server error.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="pearlbarter", description="Finds the probability of getting 2 or more ender pearl trades" + \
                                                      " in a given number of trades in Minecraft 1.16.1.",
                      aliases=["piglin", "barter", "bartering", "pearl", "pearls", "trades", "trade"], usage="<total trades>")
    async def pearlbarter(self, ctx, *, trades: str=""):
        try:
            n = int(trades)
            if not 2 <= n <= 999:
                await ctx.send(embed=funcs.errorEmbed(None, "Value must be between 2 and 999."))
                return
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
            return
        x = sum(stats.binom.pmf([i for i in range(2, n + 1)], n, 20 / 423))
        await ctx.send(f"**[1.16.1]** The probability of getting 2 or more ender pearl trades (at least " + \
                       f"8-16 pearls) in {n} gold is `{x * 100}%`. *(1 in {1 / x})*")

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="wr", description="Shows the current world records for some of the most prominent " + \
                                             "Minecraft: Java Edition speedrun categories.", aliases=["worldrecord"])
    async def wr(self, ctx):
        await ctx.send("Getting speedrun.com data. Please wait...")
        try:
            e = Embed(
                title="Minecraft Speedrun World Records",
                description="https://www.speedrun.com/mc"
            )
            urls = [
                "mkeyl926?var-r8rg67rn=klrzpjo1&var-wl33kewl=gq7zo9p1",
                "mkeyl926?var-r8rg67rn=klrzpjo1&var-wl33kewl=21go6e6q",
                "mkeyl926?var-r8rg67rn=21d4zvp1&var-wl33kewl=gq7zo9p1",
                "mkeyl926?var-r8rg67rn=21d4zvp1&var-wl33kewl=21go6e6q",
                "mkeyl926?var-r8rg67rn=21d4zvp1&var-wl33kewl=4qye4731",
                "wkpn0vdr?var-2lgzk1o8=rqv4pz7q&var-wlexoyr8=jqzywv2l",
                "wkpn0vdr?var-2lgzk1o8=rqv4pz7q&var-wlexoyr8=klr6djol",
                "wkpn0vdr?var-2lgzk1o8=5lekrv5l&var-wlexoyr8=jqzywv2l",
                "wkpn0vdr?var-2lgzk1o8=5lekrv5l&var-wlexoyr8=klr6djol"
            ]
            categories = ["SSG Pre-1.9", "SSG 1.9+", "RSG Pre-1.9", "RSG 1.9-1.15", "RSG 1.16+",
                          "SS Pre-1.9", "SS 1.9+", "RS Pre-1.9", "RS 1.9+"]
            count = 0
            for category in urls:
                res = await funcs.getRequest(
                    "https://www.speedrun.com/api/v1/leaderboards/j1npme6p/category/" + category
                )
                wrdata = res.json()["data"]["runs"][0]["run"]
                igt = wrdata["times"]["ingame_t"]
                res = await funcs.getRequest(wrdata["players"][0]["uri"])
                runner = res.json()["data"]["names"]["international"]
                h, m, s, ms = funcs.timeDifferenceStr(igt, 0, True)
                e.add_field(name=categories[count], value=f"`{h if h!=0 else ''}{'h ' if h!=0 else ''}{m}m {s}s " + \
                                                          f"{ms if ms!=0 else ''}{'ms ' if ms!=0 else ''}(by {runner})`")
                count += 1
        except Exception:
            e = funcs.errorEmbed(None, "Possible server error.")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(Minecraft(client))
