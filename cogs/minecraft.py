import math
from time import time
from scipy import stats
from random import randint
from base64 import b64decode
from asyncio import TimeoutError
from json import load, loads, dump

from discord import Embed, File, Colour
from discord.ext import commands

from assets import eye_data
from other_utils import funcs


class Minecraft(commands.Cog, name="Minecraft"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @staticmethod
    def randomEyes():
        eyes = 0
        for _ in range(12):
            luckyNumber = randint(1, 10)
            if luckyNumber == 1:
                eyes += 1
        return eyes

    @staticmethod
    def coordsDist(x, z):
        return math.sqrt(x * x + z * z)

    @staticmethod
    def f3cProcessing(clipboard):
        try:
            args = clipboard.split(" ")
            return float(args[6]), float(args[8]), float(args[9]) % 360
        except Exception:
            raise Exception("Invalid input. Please do not modify your F3+C clipboard.")

    @staticmethod
    def angleProcessing(angle):
        if angle >= 0:
            return (angle + 90) % 360
        return (angle - 270) % 360

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="findseed", description="Everyone's favourite command.",
                      aliases=["fs", "seed", "f", "s"])
    async def findseed(self, ctx):
        eyes = self.randomEyes()
        with open(f"{funcs.getPath()}/data.json", "r", encoding="utf-8") as f:
            data = load(f)
        f.close()
        odds = eye_data.EYE_DATA[str(eyes)]["percent"]
        onein = eye_data.EYE_DATA[str(eyes)]["onein"]
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
            odds = eye_data.EYE_DATA[str(i)]["percent"]
            msg += f"{i} eye - `{odds}% (1 in {eye_data.EYE_DATA[str(i)]['onein']})`\n"
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
    @commands.command(name="server", description="Gets the current status of a Minecraft server.", aliases=["mcserver"],
                      usage="[server address]")
    async def server(self, ctx, *, ipaddress: str=""):
        ipaddress = ipaddress.casefold().replace(" ", "") or "mc.pastelcraft.me"
        try:
            res = await funcs.getRequest(
                f"https://api.mcsrvstat.us/2/{ipaddress}",
                headers={"accept": "application/json"}
            )
            data = res.json()
            status = data["online"]
            e = Embed(title="Minecraft Server Status", colour=Colour.green() if status else Colour.red())
            e.add_field(name="Server Address", value=f"`{ipaddress}`")
            e.add_field(name="Online", value=f"`{status}`")
            if status:
                players = data["players"]["online"]
                e.add_field(name="Player Count", value=f"`{players}`")
                if players:
                    try:
                        playerLimit = 25
                        playerList = data["players"]["list"][:playerLimit]
                        listStr = ", ".join(f"`{player}`" for player in playerList)
                        if len(playerList) != players:
                            listStr += f" *and {players - playerLimit} more...*"
                        e.add_field(name="Players", value=listStr)
                    except:
                        pass
                e.add_field(name="Version", value=f'`{data["version"]}`')
                e.add_field(name="Port", value=f'`{data["port"]}`')
                e.set_thumbnail(url=f"https://eu.mc-api.net/v3/server/favicon/{ipaddress}")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid server address or server error?")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="pearlbarter", description="Finds the probability of getting 2 or more ender pearl trades" + \
                                                      " in a given number of trades in Minecraft 1.16.1.",
                      aliases=["piglin", "barter", "bartering", "pearl", "pearls", "trades", "trade"],
                      usage="<total trades>")
    async def pearlbarter(self, ctx, *, trades: str=""):
        try:
            n = int(trades)
            if not 2 <= n <= 999:
                return await ctx.send(embed=funcs.errorEmbed(None, "Value must be between 2 and 999."))
        except ValueError:
            return await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
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
                h, m, s, ms = funcs.timeDifferenceStr(igt, 0, noStr=True)
                e.add_field(name=categories[count], value=f"`{h if h!=0 else ''}{'h ' if h!=0 else ''}{m}m {s}s " + \
                                                          f"{ms if ms!=0 else ''}{'ms ' if ms!=0 else ''}(by {runner})`")
                count += 1
        except Exception:
            e = funcs.errorEmbed(None, "Possible server error.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="blindtravel", description="A Minecraft: Java Edition speedrunning tool that " + \
                                                      "should be used when you want to build another por" + \
                                                      "tal in the Nether before throwing any eyes of end" + \
                                                      "er. To use this command, in the game, press F3+C," + \
                                                      " pause, come over to Discord, paste your clipboar" + \
                                                      "d as an argument for the command, and then build " + \
                                                      "your portal at the suggested coordinates in the N" + \
                                                      "ether. This command is for versions 1.9+ and may " + \
                                                      "not be 100% accurate.",
                      aliases=["bt", "blind"], usage="<F3+C data>")
    async def blindtravel(self, ctx, *, f3c):
        try:
            x, z, _ = self.f3cProcessing(f3c)
            dist = self.coordsDist(x, z)
            o = 190 if dist < 190 else dist if dist < 290 else 290 if dist < 480 else 594 if dist < 594 else dist \
                if dist < 686 else 686 if dist < 832 else 970 if dist < 970 else dist if dist < 1060 else 1060
            t = math.atan(z / x)
            xp = round(funcs.sign(x) * abs(o * math.cos(t)))
            zp = round(funcs.sign(z) * abs(o * math.sin(t)))
            await ctx.send(f"{ctx.author.mention} Build your portal at: **{xp}, {zp}**")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="educatedtravel", description="A Minecraft: Java Edition speedrunning tool th" + \
                                                         "at should be used when you want to build anoth" + \
                                                         "er portal in the Nether after throwing an eye " + \
                                                         "of ender. To use this command, in the game, th" + \
                                                         "row an eye, stand still, put your mouse direct" + \
                                                         "ly over the eye, press F3+C, pause, come over " + \
                                                         "to Discord, paste your clipboard as an argumen" + \
                                                         "t for the command, and then build your portal " + \
                                                         "at the suggested coordinates in the Nether. Th" + \
                                                         "is command is for versions 1.9+ and may not be" + \
                                                         " 100% accurate.",
                      aliases=["et", "educated", "nethertravel"], usage="<F3+C data>")
    async def educatedtravel(self, ctx, *, f3c):
        try:
            x, z, f = self.f3cProcessing(f3c)
            f = (360 + f if f < 0 else f) - 180
            o = 640 if self.coordsDist(x, z) > 3584 else 216
            m1 = -math.tan((90 - f) * (math.pi / 180))
            a = 1 + (m1 ** 2)
            b1 = -m1 * (x / 8) + (z / 8)
            b = 2 * m1 * b1
            xp = ((-b) + (funcs.sign(f) * math.sqrt(b ** 2 - 4 * a * (b1 ** 2 - o ** 2)))) / (2 * a)
            zp = round(m1 * xp + b1)
            xp = round(xp)
            await ctx.send(f"{ctx.author.mention} Build your portal at: **{xp}, {zp}**")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="doubletravel", description="A Minecraft: Java Edition speedrunning tool that" + \
                                                       ", whilst you are in the Nether, gets a spot for " + \
                                                       "you to make your first portal inside the second " + \
                                                       "ring of strongholds. To use this command, in the" + \
                                                       " game, press F3+C, pause, come over to Discord, " + \
                                                       "paste your clipboard as an argument for the comm" + \
                                                       "and, and then build your portal at the suggested" + \
                                                       " coordinates in the Nether. `educatedtravel` shou" + \
                                                       "ld then be used after exiting the Nether which s" + \
                                                       "hould do a good job of getting you to the right " + \
                                                       "spot in the Nether to build your second portal. " + \
                                                       "This command is for versions 1.9+ and may not be" + \
                                                       " 100% accurate.",
                      aliases=["dt", "double"], usage="<F3+C data>")
    async def doubletravel(self, ctx, *, f3c):
        try:
            x, z, _ = self.f3cProcessing(f3c)
            o = 520
            t = math.atan(z / x)
            xp = round(funcs.sign(x) * abs(o * math.cos(t)))
            zp = round(funcs.sign(z) * abs(o * math.sin(t)))
            await ctx.send(
                f"{ctx.author.mention} Build your first portal at: **{xp}, {zp}**\n\n" + \
                f"Use `{self.client.command_prefix}educatedtravel` afterwards."
            )
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="safeblind", description="A Minecraft: Java Edition speedrunning tool that, s" + \
                                                    "imilar to `blindtravel`, should be used when you wan" + \
                                                    "t to build another portal in the Nether before thro" + \
                                                    "wing any eyes of ender. This on average will get yo" + \
                                                    "u closer to the stronghold compared to `blindtravel`" + \
                                                    ", but time may be lost. To use this command, in the" + \
                                                    " game, press F3+C, pause, come over to Discord, pas" + \
                                                    "te your clipboard as an argument for the command, a" + \
                                                    "nd then build your portal at the suggested coordina" + \
                                                    "tes in the Nether. This command is for versions 1.9" + \
                                                    "+ and may not be 100% accurate.",
                      aliases=["sb", "safetravel", "safe", "st"], usage="<F3+C data>")
    async def safeblind(self, ctx, *, f3c):
        try:
            x, z, _ = self.f3cProcessing(f3c)
            dist = self.coordsDist(x, z)
            o = 222 if dist < 222 else dist if dist < 250 else 250 if dist < 480 else 615 if dist < 615 \
                else dist if dist < 645 else 645 if dist < 832 else 1005 if dist < 1005 else dist if dist < 1032 \
                else 1032
            t = math.atan(z / x)
            xp = round(funcs.sign(x) * abs(o * math.cos(t)))
            zp = round(funcs.sign(z) * abs(o * math.sin(t)))
            await ctx.send(f"{ctx.author.mention} Build your portal at: **{xp}, {zp}**")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(usage="<F3+C data>", description="A Minecraft: Java Edition speedrunning tool that use" + \
                                                       's the "8, 8" rule to try and guess the location of t' + \
                                                       "he stronghold from an eye of ender throw. This comma" + \
                                                       "nd is experimental and should only be used when you " + \
                                                       "think you are close to the stronghold. To use this c" + \
                                                       "ommand, in the game, throw an eye, stand still, put " + \
                                                       "your mouse directly over the eye, press F3+C, pause," + \
                                                       " come over to Discord, paste your clipboard as an ar" + \
                                                       "gument for the command, and take the suggested coord" + \
                                                       "inates into account. It is recommended to use `trian" + \
                                                       "gulation` instead. This command is for versions 1.9+" + \
                                                       " and may not be 100% accurate.",
                      aliases=["eyethrow", "44", "onethrow", "throw", "eye", "eyes"], name="88")
    async def eighteight(self, ctx, *, f3c):
        try:
            x, z, f = self.f3cProcessing(f3c)
            f = (360 + f if f < 0 else f) - 180
            r = (90 - f) * (math.pi / 180)
            b = 8 - abs(abs(x) % 16) + 16
            l = []
            s = 0
            while s < 11904:
                d = b * funcs.sign(f)
                x += d
                z += d * -math.tan(r)
                v = abs(abs(abs(z) % 16) - 8) + 0.5
                s = self.coordsDist(x, z)
                if s > 1408:
                    l.append({"k": x, "v": v, "j": v * v * math.sqrt(1 + len(l)), "r": z})
                b = 16
            l.sort(key=lambda i: i["j"])
            xp, zp = round(l[0]["k"]), round(l[0]["r"])
            await ctx.send(f"{ctx.author.mention} The stronghold could be at: **{xp}, {zp}**")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="triangulation", description="A Minecraft: Java Edition speedrunning tool tha" + \
                                                        "t uses two sets of F3+C coordinates to try and " + \
                                                        "triangulate the stronghold. To use this command" + \
                                                        ", in the game, throw an eye, stand still, put y" + \
                                                        "our mouse directly over the eye, press F3+C, pa" + \
                                                        "use, come over to Discord, paste your clipboard" + \
                                                        " as an argument for the command, come back to t" + \
                                                        "he game, get closer to the stronghold whilst sl" + \
                                                        "ightly deviating from your angle, repeat the pr" + \
                                                        "ocess again, submit your second F3+C clipboard " + \
                                                        "as a regular message, and take the suggested co" + \
                                                        "ordinates into account. This command is for all" + \
                                                        " versions and may not be 100% accurate.",
                      aliases=["triangulate", "stronghold", "triangle"], usage="<F3+C data>")
    async def triangulation(self, ctx, *, f3c):
        try:
            x0, z0, f0 = self.f3cProcessing(f3c)
        except Exception as ex:
            return await ctx.send(embed=funcs.errorEmbed(None, str(ex)))
        x1, z1, f1 = None, None, None
        await ctx.send(
            f"Once you are ready, paste your second F3+C paste here. " + \
            "You have 20 minutes. Type `!cancel` to cancel."
        )
        try:
            while True:
                msg = await self.client.wait_for(
                    "message", timeout=1200, check=lambda m: ctx.author == m.author
                )
                try:
                    x1, z1, f1 = self.f3cProcessing(msg.content)
                except:
                    if msg.content.casefold() == "!cancel":
                        return await ctx.send("Cancelling.")
                    continue
                if x1 == x0 and z1 == z0 and f1 == f0:
                    continue
                break
            a0 = math.tan(self.angleProcessing(f0) * math.pi / 180)
            a1 = math.tan(self.angleProcessing(f1) * math.pi / 180)
            b = z0 - x0 * a0
            xp = ((z1 - x1 * a1) - b) / (a0 - a1)
            zp = xp * a0 + b
            await ctx.send(f"{ctx.author.mention} The stronghold could be at: **{round(xp)}, {round(zp)}**")
        except TimeoutError:
            await ctx.send("Cancelling.")


def setup(client: commands.Bot):
    client.add_cog(Minecraft(client))
