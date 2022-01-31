# Credit - https://github.com/Sharpieman20/Sharpies-Speedrunning-Tools
# For blindtravel, doubletravel, educatedtravel, safeblind, triangulation
# Credit - https://github.com/FourGoesFast/PerfectTravelBot
# For divinetravel, perfecttravel

import math
from asyncio import TimeoutError
from base64 import b64decode
from json import loads
from random import choice, randint
from time import time

from discord import Colour, Embed, File
from discord.ext import commands

from other_utils import funcs

BARTER_LIMIT = 896


class Minecraft(commands.Cog, name="Minecraft", description="Commands relating to *Minecraft* and *Minecraft* speedrunning."):
    def __init__(self, botInstance):
        self.client = botInstance
        self.client.loop.create_task(self.__readFiles())

    async def __readFiles(self):
        self.divinetravel = await funcs.readJson("assets/minecraft/divine_travel.json")
        self.perfecttravel = await funcs.readJson("assets/minecraft/perfect_travel.json")
        self.eyedata = await funcs.readJson("assets/minecraft/eye_data.json")
        self.loottable = await self.piglinLootTable()
        await funcs.generateJson(
            "findseed",
            {
                "calls": 0,
                "highest": {
                    "found": 0,
                    "number": 0,
                    "time": int(time())
                }
            }
        )
        await funcs.generateJson("finddream", {"iteration": 0, "mostPearls": 0, "mostRods": 0})

    @staticmethod
    async def piglinLootTable():
        lt = await funcs.readJson("assets/minecraft/piglin_loot_table.json")
        ltnew = []
        for i in lt:
            if i["id"] < 5:
                item = i["item"]
                for j in range(1, 4):
                    i["item"] = f"{item} {j}"
                    for _ in range(i["weight"]):
                        ltnew.append(i.copy())
                    i["id"] += 1
            else:
                for _ in range(i["weight"] * 3):
                    ltnew.append(i)
        return ltnew

    @staticmethod
    def randomEyes():
        eyes = 0
        for _ in range(12):
            eyes += 1 if funcs.oneIn(10) else 0
        return eyes

    @staticmethod
    def getExcess(item):
        stacks = item / 64
        excess = int((stacks - int(stacks)) * 64)
        stacksandexcess = int(stacks) and excess
        return "" if not int(stacks) and excess == item \
               else f" ({'{:,} stack{}'.format(int(stacks), '' if int(stacks) == 1 else 's') if int(stacks) else ''}" + \
                    f"{' + ' if stacksandexcess else ''}{str(excess) if excess else ''})"

    @staticmethod
    def chargeableAnchors(glowdust: int, cryobby: int):
        return min([glowdust // 16, cryobby // 6])

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

    @staticmethod
    def coordsDist(x, z):
        return math.sqrt(x * x + z * z)

    def coordsDifference(self, coords1: tuple, coords2: tuple):
        return self.coordsDist(coords1[0] - coords2[0], coords1[1] - coords2[1])

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="findseed", description="Everyone's favourite command. Test your luck using this command!",
                      aliases=["fs", "seed", "findseeds", "f"])
    async def findseed(self, ctx):
        eyes = self.randomEyes()
        data = await funcs.readJson("data/findseed.json")
        odds = self.eyedata[str(eyes)]["percent"]
        onein = self.eyedata[str(eyes)]["onein"]
        update = False
        if eyes >= data["highest"]["number"]:
            data["highest"]["found"] -= data["highest"]["found"] - 1 if eyes > data["highest"]["number"] else -1
            data["highest"]["number"] = eyes
            data["highest"]["time"] = int(time())
            update = True
        highest = data["highest"]["number"]
        highestTime = data["highest"]["time"]
        highestTotal = data["highest"]["found"]
        data["calls"] += 1
        calls = data["calls"]
        await funcs.dumpJson("data/findseed.json", data)
        file = File(f"{funcs.getPath()}/assets/minecraft/portal_frame_images/{eyes}eye.png", filename="portal.png")
        foundTime = "just now"
        if not update:
            timestr = funcs.timeDifferenceStr(time(), highestTime)
            timestr_0 = int(timestr.split(" ")[0])
            if timestr_0 > 2:
                foundTime = f"{timestr_0} days"
            else:
                foundTime = timestr
        e = Embed(title=f"{self.client.command_prefix}findseed",
                  description=f"Requested by: {ctx.message.author.mention}")
        e.add_field(name="Your Eyes", value=f"`{eyes}`")
        e.add_field(name="Probability", value=f"`{odds}% (1 in {onein})`")
        e.add_field(name="Most Eyes Found", inline=False,
                    value=f"`{highest} (last found {foundTime}{' ago' if not update else ''}" + \
                          f", found {'{:,}'.format(highestTotal)} time{'' if highestTotal == 1 else 's'})`")
        e.set_footer(text=f"The command has been called {'{:,}'.format(calls)} time{'' if calls == 1 else 's'}. !eyeodds")
        e.set_image(url="attachment://portal.png")
        await ctx.reply(embed=e, file=file)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="eyeodds", description="Shows the odds of getting each type of end portal.",
                      aliases=["odds", "eyes", "eye"])
    async def eyeodds(self, ctx):
        msg = ""
        for i in range(13):
            odds = self.eyedata[str(i)]["percent"]
            msg += f"{i} eye - `{odds}% (1 in {self.eyedata[str(i)]['onein']})`\n"
        await ctx.reply(msg)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="finddream", description="Can you get Dream's" + ' *Minecraft* speedrunning "luck"? ' + \
                                                    "Test your luck using this command!",
                      aliases=["dream", "dreamsimulator", "dreamsim", "dreamluck", "fd"], hidden=True)
    async def finddream(self, ctx):
        pearls, rods = 0, 0
        dpearls, drods = 262, 305
        data = await funcs.readJson("data/finddream.json")
        mostPearls = data["mostPearls"]
        mostRods = data["mostRods"]
        for _ in range(dpearls):
            pearls += 1 if randint(0, 422) < 20 else 0
        for _ in range(drods):
            rods += 1 if funcs.oneIn(2) else 0
        data["mostPearls"] = pearls if pearls >= mostPearls else mostPearls
        data["mostRods"] = rods if rods >= mostRods else mostRods
        data["iteration"] += 1
        iters = data['iteration']
        await funcs.dumpJson("data/finddream.json", data)
        e = Embed(
            title=f"{self.client.command_prefix}finddream",
            description=f"Dream got 42 ender pearl trades in {dpearls} plus 211 blaze rod drops in {drods}. " + \
                        f"Can you achieve his 'luck'?\n\nRequested by: {ctx.author.mention}"
        )
        e.add_field(name="Your Pearl Trades", value=f"`{pearls} ({round(pearls / dpearls * 100, 3)}%)`")
        e.add_field(name="Your Rod Drops", value=f"`{rods} ({round(rods / drods * 100, 3)}%)`")
        e.set_footer(
            text=f"The command has been called {'{:,}'.format(iters)} time{'' if iters == 1 else 's'}. " + \
                 f"| Most pearl trades: {data['mostPearls']}; most rod drops: {data['mostRods']}"
        )
        e.set_thumbnail(url="https://static.wikia.nocookie.net/dream_team/images/7/7b/Dream.jpeg")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="findcleric", description="Will you get the ender pearl trade from the cleric, " + \
                                                     "or will you get one-thirded? Test your luck using this command!",
                      aliases=["cleric", "stupidvillager"], hidden=True)
    async def findcleric(self, ctx):
        e = Embed(title=f"{self.client.command_prefix}findcleric",
                  description=f"Requested by: {ctx.message.author.mention}")
        badluckonein = 3
        goodluck = not funcs.oneIn(badluckonein)
        e.add_field(name="Result", value=f"`{'Pearl' if goodluck else 'Bottle'} Trade{'!' if goodluck else '...'}`")
        e.set_thumbnail(url="https://media.discordapp.net/attachments/771404776410972161/856203578615529532/cleric.png")
        e.set_image(url="https://media.discordapp.net/attachments/771404776410972161/856203574337601536/pearl.png" if goodluck else
                        "https://media.discordapp.net/attachments/771404776410972161/856203573113520138/bottle.png")
        e.set_footer(text=f"Odds: {str(badluckonein - 1) if goodluck else '1'}/{str(badluckonein)}")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="findgravel", description="Will you get flint from gravel? Test your luck using this command!",
                      aliases=["gravel", "flint", "findflint"], hidden=True)
    async def findgravel(self, ctx):
        e = Embed(title=f"{self.client.command_prefix}findgravel",
                  description=f"Requested by: {ctx.message.author.mention}")
        goodluckonein = 10
        badluck = not funcs.oneIn(goodluckonein)
        e.add_field(name="Result", value=f"`{'Gravel' if badluck else 'Flint'}{'...' if badluck else '!'}`")
        e.set_thumbnail(url="https://media.discordapp.net/attachments/771698457391136798/856209821383917608/gravel.png")
        e.set_image(url="https://media.discordapp.net/attachments/771698457391136798/856209821383917608/gravel.png" if badluck else
                        "https://media.discordapp.net/attachments/771698457391136798/856209843174244362/flint.png")
        e.set_footer(text=f"Odds: {str(goodluckonein - 1) if badluck else '1'}/{str(goodluckonein)}")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="findperch", description="You are in insane pace and about to kill the dragon..." + \
                                                    "but does it perch instantly? Test your luck using this command!",
                      aliases=["dragon", "fp", "finddragon"], hidden=True)
    async def findperch(self, ctx):
        e = Embed(title=f"{self.client.command_prefix}findperch",
                  description=f"Requested by: {ctx.message.author.mention}")
        goodluckonein = 13
        badluck = not funcs.oneIn(goodluckonein)
        e.add_field(name="Result", value=f"`{'No Perch' if badluck else 'Perch'}{'...' if badluck else '!'}`")
        e.set_thumbnail(url="https://media.discordapp.net/attachments/771404776410972161/928297045486370857/dragon.png")
        e.set_image(url="https://media.discordapp.net/attachments/771404776410972161/928299016259776613/2022-01-05_22.48.45.png"
                        if badluck
                        else "https://media.discordapp.net/attachments/771404776410972161/928298549861572638/2022-01-05_22.46.50.png")
        e.set_footer(text=f"Odds: {str(goodluckonein - 1) if badluck else '1'}/{str(goodluckonein)}")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="findskull", description="You kill a wither skeleton...but does it drop a wither skull?" + \
                                                    " Test your luck using this command!",
                      aliases=["skull", "witherskull", "findwitherskull", "findwither"], hidden=True)
    async def findskull(self, ctx):
        e = Embed(title=f"{self.client.command_prefix}findskull",
                  description=f"Requested by: {ctx.message.author.mention}")
        goodluckonein = 40
        badluck = not funcs.oneIn(goodluckonein)
        e.add_field(name="Result", value=f"`{'No Skull' if badluck else 'Skull'}{'...' if badluck else '!'}`")
        e.set_thumbnail(url="https://cdn.discordapp.com/attachments/771404776410972161/935204890639233054/unknown.png")
        e.set_image(
            url="" if badluck else "https://cdn.discordapp.com/attachments/771404776410972161/935204919651205250/unknown.png"
        )
        e.set_footer(text=f"Odds: {str(goodluckonein - 1) if badluck else '1'}/{str(goodluckonein)}")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="findblaze", description="You kill a blaze...but does it drop a rod? Test your luck using this command!",
                      aliases=["blaze", "rod", "blazerod", "findrod", "findblazerod"], hidden=True)
    async def findblaze(self, ctx):
        e = Embed(title=f"{self.client.command_prefix}findblaze",
                  description=f"Requested by: {ctx.message.author.mention}")
        badluckonein = 2
        goodluck = not funcs.oneIn(badluckonein)
        e.add_field(name="Result", value=f"`{'Rod' if goodluck else 'No Rod'} Drop{'!' if goodluck else '...'}`")
        e.set_thumbnail(url="https://media.discordapp.net/attachments/771698457391136798/856213640809414666/blaze.png")
        e.set_image(url="https://media.discordapp.net/attachments/771698457391136798/856213641020178472/rod.png" if goodluck else
                        "https://cdn.discordapp.com/attachments/771698457391136798/856213642173612032/norod.png")
        e.set_footer(text=f"Odds: {str(badluckonein - 1) if goodluck else '1'}/{str(badluckonein)}")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="perchcmd", description="Shows the command to force the the ender dragon perch.", aliases=["perch"])
    async def perchcmd(self, ctx):
        await ctx.reply("```1.13+: /data merge entity @e[type=ender_dragon,limit=1] {DragonPhase:2}\n\n" +
                        "1.9-1.12: /entitydata @e[type=ender_dragon] {DragonPhase:2}```")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="logs", description="Calculates how many logs you will need to trade for a certain number of emeralds.",
                      aliases=["log", "wood"], usage="<amount of emeralds needed>")
    async def logs(self, ctx, emeralds):
        try:
            emeralds = int(emeralds)
            if emeralds < 1:
                raise Exception
            log = emeralds * 4
            await ctx.reply("You want **{:,}** emerald{}.\n\nYou will need **{:,}** logs{}.".format(
                emeralds, "" if emeralds == 1 else "s", int(log), self.getExcess(log)
            ))
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(
                embed=funcs.errorEmbed(None, "Invalid input. Please make sure you are entering positive, non-zero integers.")
            )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="haybales", aliases=["hay", "haybale"], usage="<amount of emeralds needed>",
                      description="Calculates how many hay bales you will need to trade for a certain number of emeralds.")
    async def haybales(self, ctx, emeralds):
        try:
            emeralds = int(emeralds)
            if emeralds < 1:
                raise Exception
            hay = 20 * emeralds / 9
            hay = funcs.strictRounding(hay)
            await ctx.reply("You want **{:,}** emerald{}.\n\nYou will need **{:,}** hay bales{}.".format(
                emeralds, "" if emeralds == 1 else "s", int(hay), self.getExcess(hay)
            ))
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(
                embed=funcs.errorEmbed(None, "Invalid input. Please make sure you are entering positive, non-zero integers.")
            )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="anchors", description="Calculates how many chargeable respawn anchors you can craft based on how " + \
                                                  "much glowstone dust and crying obsidian you have.",
                      aliases=["anchor"], usage="<amount of glowstone dust> <amount of crying obdisian>")
    async def anchors(self, ctx, glowdust, cryobby):
        try:
            glowdust = int(glowdust)
            cryobby = int(cryobby)
            if glowdust < 1 or cryobby < 1:
                raise Exception
            anchors = self.chargeableAnchors(glowdust, cryobby)
            charge = " and sufficiently charge {}".format("it" if anchors == 1 else "them") if anchors else ""
            await ctx.reply(
                "You have **{:,}** glowstone dust and **{:,}** crying obsidian.\n\nYou can make **".format(glowdust, cryobby) +
                "{:,}** respawn anchor{}{}.".format(anchors, "" if anchors == 1 else "s", charge)
            )
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(
                embed=funcs.errorEmbed(None, "Invalid input. Please make sure you are entering positive, non-zero integers.")
            )

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(description="Simulates *Minecraft: Java Edition* 1.16.1 piglin bartering. Test your luck using this command!",
                      aliases=["barter", "piglin", "poglin", "bartering", "barteringsim"], name="bartersim",
                      usage=f"[gold ingots up to 10,000]\n\nAlternative usage(s):\n\n- <gold blocks up to 1,111 (ending with b)>")
    async def bartersim(self, ctx, goldingots: str="1"):
        try:
            try:
                goldingots = int(goldingots)
            except:
                goldingots = int(goldingots[:-1]) * 9
            if not 0 < goldingots < 10001:
                return await ctx.reply(embed=funcs.errorEmbed(None, f"Value must be between 1 and 10,000."))
        except ValueError:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))
        trades = {}
        string, glowdust, cryobby = 0, 0, 0
        for _ in range(goldingots):
            trade = choice(self.loottable)
            if trade["id"] not in list(trades.keys()):
                trades[trade["id"]] = {}
                trades[trade["id"]]["item"] = trade["item"]
                n = choice(trade["quantity"])
                trades[trade["id"]]["quantity"] = n
                trades[trade["id"]]["trades"] = 1
            else:
                n = choice(trade["quantity"])
                trades[trade["id"]]["quantity"] += n
                trades[trade["id"]]["trades"] += 1
            if trade["id"] == 13:
                string += n
            elif trade["id"] == 10:
                glowdust += n
            elif trade["id"] == 19:
                cryobby += n
        res = "You bartered {:,} gold ingot{} for:\n\n".format(goldingots, "" if goldingots == 1 else "s")
        for i in sorted(trades):
            t = trades[i]
            res += "{}{:,} x {} ({:,} trade{})\n".format(
                "*** " if i in [7, 8, 10, 12, 13, 18, 19] else "    ",
                t["quantity"], t["item"], t["trades"], "" if t["trades"] == 1 else "s"
            )
        anchors = self.chargeableAnchors(glowdust, cryobby)
        beds = string // 12
        explosives = anchors + beds
        if explosives:
            res += "\nExplosives you can craft ({:,}):\n\n".format(explosives)
            if beds:
                res += "    {:,} x Bed\n".format(beds)
            if anchors:
                res += "    {:,} x Respawn Anchor (w/ enough glowstone to power)".format(anchors)
        await ctx.reply(funcs.formatting(res))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="pearlbarter", description="Finds the probability of getting 12 or more ender pearls" + \
                                                      " in a given number of piglin trades in *Minecraft* 1.16.1.",
                      aliases=["pearltrade", "pearlbartering", "barteringpearl", "barterpearl", "barterpearls"],
                      usage=f"[total gold ingots up to {BARTER_LIMIT}]")
    async def pearlbarter(self, ctx, trades: str="2"):
        try:
            n = int(trades)
            if not 2 <= n <= BARTER_LIMIT:
                return await ctx.reply(embed=funcs.errorEmbed(None, f"Value must be between 2 and {BARTER_LIMIT}."))
        except ValueError:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))
        x = 1 - (403 / 423) ** n - n * (20 / 423) * ((403 / 423) ** (n - 1)) - (2 / 5) * (n * (n - 1) / 2) \
            * ((403 / 423) ** (n - 2)) * ((20 / 423) ** 2)
        await ctx.reply(f"**[1.16.1]** The probability of getting 12 or more ender pearls" + \
                        f" with {n} gold ingots is:\n\n`{round(x * 100, 5)}%` (1 in {round(1 / x, 5)})")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="blindtravel", description="A *Minecraft: Java Edition* speedrunning tool that " + \
                                                      "should be used when you want to build another por" + \
                                                      "tal in the Nether before throwing any eyes of end" + \
                                                      "er. To use this command, in the game, press F3+C," + \
                                                      " pause, come over to Discord, paste your clipboar" + \
                                                      "d as an argument for the command, and then build " + \
                                                      "your portal at the suggested coordinates in the N" + \
                                                      "ether. This command is for versions 1.13+ and may " + \
                                                      "not be 100% accurate. This command MAY not be used" + \
                                                      " in a real speedrun.",
                      aliases=["bt", "blind", "blindtrav"], usage="<F3+C data>")
    async def blindtravel(self, ctx, *, f3c):
        await ctx.send("**Note:** This command, along with other speedrunning calculators, MAY not be used in a real speedrun.")
        try:
            x, z, _ = self.f3cProcessing(f3c)
            dist = self.coordsDist(x, z)
            o = 190 if dist < 190 else dist if dist < 290 else 290 if dist < 442 else 580 if dist < 580 else dist \
                if dist < 692 else 686 if dist < 825 else 970 if dist < 970 else dist if dist < 1060 else 1060
            t = math.atan(z / x)
            xp = funcs.sign(x) * abs(o * math.cos(t))
            zp = funcs.sign(z) * abs(o * math.sin(t))
            blocks = round(self.coordsDifference((x, z), (xp, zp)))
            await ctx.reply(
                f"Build your portal at: **{round(xp)}, {round(zp)}** " + \
                f"({'{:,}'.format(blocks)} block{'' if blocks == 1 else 's'} away)"
            )
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="educatedtravel", description="A *Minecraft: Java Edition* speedrunning tool th" + \
                                                         "at should be used when you want to build anoth" + \
                                                         "er portal in the Nether after throwing an eye " + \
                                                         "of ender. To use this command, in the game, th" + \
                                                         "row an eye, stand still, put your mouse direct" + \
                                                         "ly over the eye, press F3+C, pause, come over " + \
                                                         "to Discord, paste your clipboard as an argumen" + \
                                                         "t for the command, and then build your portal " + \
                                                         "at the suggested coordinates in the Nether. Th" + \
                                                         "is command is for versions 1.13+ and may not be" + \
                                                         " 100% accurate. This command MAY not be used in" + \
                                                         " a real speedrun.",
                      aliases=["et", "educated", "nethertravel"], usage="<F3+C data>")
    async def educatedtravel(self, ctx, *, f3c):
        await ctx.send("**Note:** This command, along with other speedrunning calculators, MAY not be used in a real speedrun.")
        try:
            x, z, f = self.f3cProcessing(f3c)
            f = (360 + f if f < 0 else f) - 180
            o = 640 if self.coordsDist(x, z) > 3584 else 216
            m1 = -math.tan((90 - f) * (math.pi / 180))
            a = 1 + (m1 ** 2)
            b1 = -m1 * (x / 8) + (z / 8)
            b = 2 * m1 * b1
            xp = ((-b) + (funcs.sign(f) * math.sqrt(b ** 2 - 4 * a * (b1 ** 2 - o ** 2)))) / (2 * a)
            zp = m1 * xp + b1
            await ctx.reply(f"Build your portal at: **{round(xp)}, {round(zp)}** ")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="doubletravel", description="A *Minecraft: Java Edition* speedrunning tool that" + \
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
                                                       "This command is for versions 1.13+ and may not be" + \
                                                       " 100% accurate. This command MAY not be used in a " + \
                                                       "real speedrun.",
                      aliases=["double"], usage="<F3+C data>")
    async def doubletravel(self, ctx, *, f3c):
        await ctx.send("**Note:** This command, along with other speedrunning calculators, MAY not be used in a real speedrun.")
        try:
            x, z, _ = self.f3cProcessing(f3c)
            o = 520
            t = math.atan(z / x)
            xp = funcs.sign(x) * abs(o * math.cos(t))
            zp = funcs.sign(z) * abs(o * math.sin(t))
            blocks = round(self.coordsDifference((x, z), (xp, zp)))
            await ctx.reply(
                f"Build your first portal at: **{round(xp)}, {round(zp)}** " + \
                f"({'{:,}'.format(blocks)} block{'' if blocks == 1 else 's'} away)\n\n" + \
                f"Use `{self.client.command_prefix}educatedtravel` afterwards."
            )
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="safeblind", description="A *Minecraft: Java Edition* speedrunning tool that, s" + \
                                                    "imilar to `blindtravel`, should be used when you wan" + \
                                                    "t to build another portal in the Nether before thro" + \
                                                    "wing any eyes of ender. This on average will get yo" + \
                                                    "u closer to the stronghold compared to `blindtravel`" + \
                                                    ", but time may be lost. To use this command, in the" + \
                                                    " game, press F3+C, pause, come over to Discord, pas" + \
                                                    "te your clipboard as an argument for the command, a" + \
                                                    "nd then build your portal at the suggested coordina" + \
                                                    "tes in the Nether. This command is for versions 1.13" + \
                                                    "+ and may not be 100% accurate. This command MAY not" + \
                                                    " be used in a real speedrun.",
                      aliases=["sb", "safetravel", "safe", "st"], usage="<F3+C data>", hidden=True)
    async def safeblind(self, ctx, *, f3c):
        await ctx.send("**Note:** This command, along with other speedrunning calculators, MAY not be used in a real speedrun.")
        try:
            x, z, _ = self.f3cProcessing(f3c)
            dist = self.coordsDist(x, z)
            o = 222 if dist < 222 else dist if dist < 250 else 250 if dist < 480 else 615 if dist < 615 \
                else dist if dist < 645 else 645 if dist < 832 else 1005 if dist < 1005 else dist if dist < 1032 \
                else 1032
            t = math.atan(z / x)
            xp = funcs.sign(x) * abs(o * math.cos(t))
            zp = funcs.sign(z) * abs(o * math.sin(t))
            blocks = round(self.coordsDifference((x, z), (xp, zp)))
            await ctx.reply(
                f"Build your portal at: **{round(xp)}, {round(zp)}** " + \
                f"({'{:,}'.format(blocks)} block{'' if blocks == 1 else 's'} away)"
            )
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="perfecttravel", description="A *Minecraft: Java Edition* speedrunning tool that att" + \
                                                        "empts to take you directly to the stronghold portal " + \
                                                        "room with the use of two Nether portals and F3 data." + \
                                                        " To use this command, in the game, leave your first " + \
                                                        "portal, find a chunk intersection and stand on the c" + \
                                                        'hunk coordinate "0, 0" right in the centre, press F3' + \
                                                        "+C, pause, come over to Discord, paste your clipboar" + \
                                                        "d as an argument for the command, go back to the Net" + \
                                                        "her, and then build your second portal at the sugges" + \
                                                        "ted coordinates in the Nether. This command is for v" + \
                                                        "ersions 1.13+ and may not be 100% accurate. This com" + \
                                                        "mand MAY not be used in a real speedrun.",
                      aliases=["perfectt", "perfect", "ptravel", "ptrav", "ptr", "pt"], usage='<F3+C data> ["calc"]\n\n' + \
                      'Note: Add "calc" at the end if you do not want to manually calculate the portal coordinates yourself.')
    async def perfecttravel(self, ctx, *, f3c):
        calc = True if f3c.casefold().split()[-1] == "calc" else False
        try:
            nx, nz, px, pz = None, None, None, None
            x, z, f = self.f3cProcessing(f3c)
            if f > 180:
                f -= 360
            if f < -180:
                f += 360
            targetchunk = self.perfecttravel[str(round(f, 2))][0]
            if calc:
                await ctx.send("**Note:** Second Nether portal coordinates are calculated for you. " + \
                               "Your run is now most likely invalid.")
            else:
                await ctx.send("**Note:** Although no calculations are done and only a lookup table is being used, " + \
                               f"note that you may still risk invalidating your run or at least have it kept under close scrutiny.")
            try:
                targetchunkx, targetchunkz = targetchunk.split(" ")
                px, pz = int(x / 16) + (0 if x > 0 else -1), int(z / 16) + (0 if z > 0 else -1)
                nx = ((px + int(targetchunkx)) * 2) if calc else targetchunkx
                nz = ((pz + int(targetchunkz)) * 2) if calc else targetchunkz
            except:
                targetchunk = ""
            if targetchunk:
                if calc:
                    await ctx.reply(
                        f"Build your second portal at: **" + \
                        f"{round(nx + (1 if nx < 0 else 0))}, {round(nz + (1 if nz < 0 else 0))}** " + \
                        "\n\nMore info: https://youtu.be/YpV7I9X-Jso"
                    )
                else:
                    await ctx.reply(
                        f"Offset: **{nx}, {nz}**\n\nYour current chunk for reference: **" + \
                        f"{px}, {pz}**" + \
                        "\n\nMore info: https://youtu.be/YpV7I9X-Jso"
                    )
            else:
                await ctx.reply(f"Cannot find ideal coordinates...")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="bedtiming", description="Shows the bed timing for end fights.",
                      aliases=["bedtimings", "onecycle", "timingbed", "bedtime", "bed", "beds"])
    async def bedtiming(self, ctx):
        await funcs.sendImage(ctx, "https://media.discordapp.net/attachments/771698457391136798/937078099789635614/unknown.png")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="eray", aliases=["eraying", "microlensing"],
                      description="Shows the microlensing tutorial for *Minecraft: Java Edition* speedrunning.")
    async def eray(self, ctx):
        await ctx.reply("https://www.youtube.com/watch?v=jvTfMLPnMSw")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="blindtravelcoords", aliases=["rings", "strongholdrings", "strongholdring"],
                      description="Shows the idea blind travel coordinates for the first to third stronghold rings.")
    async def blindtravelcoords(self, ctx):
        await ctx.reply("https://imgur.com/gallery/i3fIanf")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="mcspeedrunning", aliases=["mcspeedrun", "minecraftspeedrun", "minecraftspeedrunning", "mcsr"],
                      description="Shows the Minecraft Speedrunning website.", hidden=True)
    async def mcspeedrunning(self, ctx):
        await ctx.reply("https://www.minecraftspeedrunning.com/")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="speedrunigt", aliases=["igt"], description="Shows the SpeedRunIGT mod website.", hidden=True)
    async def speedrunigt(self, ctx):
        await ctx.reply("https://redlime.github.io/SpeedRunIGT/")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="zerocycle", description="Shows the Zero Cycle practice map.", hidden=True)
    async def zerocycle(self, ctx):
        await ctx.reply("https://zerocycle.repl.co/")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="fsg", description="Shows a list of FSG seed generators.", hidden=True, aliases=["fsgseed", "fsgseeds"])
    async def fsg(self, ctx):
        await ctx.reply("Use one of the allowed generators: " +
                        "<https://docs.google.com/spreadsheets/d/1ilu72GJ-vJZq2LFU68rycGMeTbWPjHJnO8PGfp4QjA8/edit#gid=0>\n\n" +
                        "If you would like to use the generator locally for shorter wait times, follow this: " +
                        "<https://youtu.be/Gl7zOn2lLo4>\n\nPlease play the seed within 30 seconds after it has been generated.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="triangulation", description="A *Minecraft: Java Edition* speedrunning tool tha" + \
                                                        "t attempts to locate the stronghold using both " + \
                                                        'the "8, 8" rule and triangulation. To use this ' + \
                                                        "command, in the game, throw and eye, stand stil" + \
                                                        "l, put your mouse directly over the eye, press " + \
                                                        "F3+C, pause, come over to Discord, paste your c" + \
                                                        "lipboard as an argument for the command, and th" + \
                                                        "e command should return a set of coordinates ca" + \
                                                        'lculated using the "8, 8" rule. You may continu' + \
                                                        "e using this command by parsing more F3+C clipb" + \
                                                        "oards as regular messages as you get closer to " + \
                                                        "the stronghold. Once the program knows you are " + \
                                                        "fairly close to the stronghold, it will automat" + \
                                                        "ically stop. This command is for versions 1.13+" + \
                                                        " and may not be 100% accurate. This command MAY" + \
                                                        " not be used in a real speedrun.",
                      aliases=["triangulate", "stronghold", "triangle", "trian", "tri", "88", "44"],
                      usage="<F3+C data>")
    async def triangulation(self, ctx, *, f3c):
        await ctx.send("**Note:** This command, along with other speedrunning calculators, MAY not be used in a real speedrun.")
        try:
            x, z, f = self.f3cProcessing(f3c)
            x0, z0, f0 = x, z, f
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
            xp, zp = l[0]["k"], l[0]["r"]
            blocks = round(self.coordsDifference((x0, z0), (xp, zp)))
            await ctx.reply(
                f"The stronghold could be at: **{round(xp)}, {round(zp)}** ({'{:,}'.format(blocks)} block" +
                f"{'' if blocks == 1 else 's'} away)\n\nMethod: 8, 8\n\nPaste your F3+C clipboard here once " +
                "you are ready. The program will stop after 20 minutes of inactivity. Type `!cancel` to cancel."
            )
        except Exception as ex:
            return await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))
        x1, z1, f1 = None, None, None
        blocks = 100
        try:
            while blocks > 40:
                while True:
                    msg = await self.client.wait_for(
                        "message", timeout=1200, check=lambda m: ctx.author == m.author and ctx.channel == m.channel
                    )
                    try:
                        x1, z1, f1 = self.f3cProcessing(msg.content)
                    except:
                        if msg.content.casefold() == "!cancel":
                            return await ctx.reply("Cancelling triangulation.")
                        continue
                    if x1 == x0 and z1 == z0 and f1 == f0:
                        continue
                    break
                try:
                    a0 = math.tan(self.angleProcessing(f0) * math.pi / 180)
                    a1 = math.tan(self.angleProcessing(f1) * math.pi / 180)
                    b = z0 - x0 * a0
                    xp = ((z1 - x1 * a1) - b) / (a0 - a1)
                    zp = xp * a0 + b
                    blocks = round(self.coordsDifference((x1, z1), (xp, zp)))
                except:
                    continue
                await msg.reply(
                    f"The stronghold could be at: **{round(xp)}, {round(zp)}** ({'{:,}'.format(blocks)} block" +
                    f"{'' if blocks == 1 else 's'} away)\n\nMethod: Triangulation\n\nPaste your F3+C clipboard here once " +
                    "you are ready. The program will stop after 20 minutes of inactivity. Type `!cancel` to cancel."
                )
                x0, z0, f0 = x1, z1, f1
            await ctx.send("You are close to the stronghold, stopping triangulation program.")
        except TimeoutError:
            await ctx.send("You have been inactive for over 20 minutes, stopping triangulation program.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="coordsdist", description="Calculates the distance between two sets of *Minecraft* coordinates.",
                      aliases=["coords", "distance", "dist", "coord", "coordinates", "coordinate"],
                      usage="<x #1> <z #1> <x #2> <z #2>\n\nAlternative usage(s):\n\n- <F3+C data> <x> <z>")
    async def coords(self, ctx, *, inp: str):
        inp = funcs.replaceCharacters(inp, [",", "(", ")", ";"])
        args = inp.split(" ")
        try:
            try:
                x1, z1, _ = self.f3cProcessing(inp)
            except:
                x1, z1 = float(args[0]), float(args[1])
            x2, z2 = float(args[-2]), float(args[-1])
        except ValueError:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Invalid arguments."))
        await ctx.reply(
            "The distance between (**{}**; **{}**) and (**{}**; **{}**) is: ".format(
                funcs.removeDotZero(round(x1, 5)),
                funcs.removeDotZero(round(z1, 5)),
                funcs.removeDotZero(round(x2, 5)),
                funcs.removeDotZero(round(z2, 5))
            ) + f"**{funcs.removeDotZero(round(self.coordsDifference((x1, z1), (x2, z2)), 5))}**"
        )

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="speedrunwr", description="Shows the current world records for the solo Any% Glitchless " + \
                                                     "*Minecraft: Java Edition* speedrun categories.",
                      aliases=["worldrecord", "wr", "mcwr", "ssg", "rsg"])
    async def speedrunwr(self, ctx):
        await ctx.send("Getting speedrun.com data. Please wait...")
        try:
            e = Embed(description="https://www.speedrun.com/mc")
            e.set_author(name="Minecraft Speedrun World Records - Solo Any% Glitchless",
                         icon_url="https://cdn.discordapp.com/attachments/771698457391136798/842103816761114624/mc.png")
            urls = [
                "klrzpjo1&var-wl33kewl=gq7zo9p1",
                "klrzpjo1&var-wl33kewl=21go6e6q",
                "klrzpjo1&var-wl33kewl=4qye4731",
                "21d4zvp1&var-wl33kewl=gq7zo9p1",
                "21d4zvp1&var-wl33kewl=21go6e6q",
                "21d4zvp1&var-wl33kewl=4qye4731"
            ]
            categories = [
                "Set Seed Glitchless (Pre-1.9)",
                "Set Seed Glitchless (1.9-1.15)",
                "Set Seed Glitchless (1.16+)",
                "Random Seed Glitchless (Pre-1.9)",
                "Random Seed Glitchless (1.9-1.15)",
                "Random Seed Glitchless (1.16+)"
            ]
            count = 0
            for category in urls:
                res = await funcs.getRequest(
                    "https://www.speedrun.com/api/v1/leaderboards/j1npme6p/category/mkeyl926?var-r8rg67rn=" + category
                )
                wrdata = res.json()["data"]["runs"][0]["run"]
                igt = wrdata["times"]["primary_t"]
                res = await funcs.getRequest(wrdata["players"][0]["uri"])
                runner = res.json()["data"]["names"]["international"]
                d, h, m, s, ms = funcs.timeDifferenceStr(igt, 0, noStr=True)
                e.add_field(name=categories[count], inline=False,
                            value=f"`{funcs.timeStr(d, h, m, s, ms)} ({runner})`")
                count += 1
            e.set_footer(text="Click the link above for more speedrun categories.",
                         icon_url="https://cdn.discordapp.com/attachments/771698457391136798/842103813585240124/src.png")
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Possible server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="skin", description="Gets the skin of a *Minecraft: Java Edition* user.", aliases=["mcskin"],
                      usage="[username]", hidden=True)
    async def skin(self, ctx, username: str=""):
        if username == "":
            username = ctx.message.author.name
        try:
            data = await funcs.getRequest(f"https://api.mojang.com/users/profiles/minecraft/{username}")
            username = data.json()["name"]
            res = await funcs.getRequest(
                f"https://sessionserver.mojang.com/session/minecraft/profile/{str(data.json()['id'])}"
            )
            data = loads(b64decode(res.json()["properties"][0]["value"]))
            skin = data["textures"]["SKIN"]["url"]
            e = Embed(
                title="Minecraft User",
                description=f"**{username}**"
            )
            e.set_image(url=skin)
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Invalid skin or server error.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="mcserver", description="Gets the current status of a *Minecraft: Java Edition* server.",
                      usage="[server address]")
    async def mcserver(self, ctx, *, ipaddress: str=""):
        ipaddress = ipaddress.casefold().replace(" ", "") or "mc.hypixel.net"
        try:
            res = await funcs.getRequest(f"https://api.mcsrvstat.us/2/{ipaddress}", headers={"accept": "application/json"})
            data = res.json()
            status = data["online"]
            e = Embed(title="Minecraft Server Status", colour=Colour.green() if status else Colour.red())
            e.add_field(name="Server Address", value=f"`{ipaddress}`")
            e.add_field(name="Online", value=f"`{status}`")
            if status:
                players = data["players"]["online"]
                e.add_field(name="Player Count", value="`{:,}/{:,}`".format(players, data['players']['max']))
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
                try:
                    e.add_field(name="Software", value=f'`{data["software"]}`')
                except:
                    pass
                motd = data["motd"]["clean"]
                try:
                    secondLine = f"\n{motd[1].strip().replace('&amp;', '&')}"
                except:
                    secondLine = ""
                e.set_footer(text=motd[0].strip().replace('&amp;', '&') + secondLine)
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Invalid server address or server error?")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="fossils", description="Brings up a *Minecraft* fossil identification chart for divine travel.",
                      aliases=["ft", "fossiltable", "fossilchart", "fossil"])
    async def fossils(self, ctx):
        url = "https://cdn.discordapp.com/attachments/771404776410972161/842022227347636264/fossiltable.jpg"
        await funcs.sendImage(
            ctx, url, message="PDF: https://cdn.discordapp.com/attachments/817309668924719144/"+ \
                              "818310310153814056/Fossil_origin_identification_1.pdf"
        )

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="divinetravel", description="Brings up a *Minecraft* divine travel chart.",
                      aliases=["dt", "divine", "div", "dv"], usage="[option]")
    async def divinetravel(self, ctx, *, option: str=""):
        if option:
            try:
                res = self.divinetravel[option.casefold().replace(" ", "")].split(" | ")
                e = Embed(title="Divine Travel: " + option.casefold().replace(" ", ""))
                for i in range(len(res)):
                    e.add_field(name=f"Stronghold {str(i + 1)}", value=f"`{res[i].split(': ')[1]}`")
            except KeyError:
                e = funcs.errorEmbed(
                    "Invalid option!",
                    "Valid options:\n\n{}".format(", ".join(f"`{opt}`" for opt in self.divinetravel.keys()))
                )
            await ctx.reply(embed=e)
        else:
            url = "https://media.discordapp.net/attachments/771698457391136798/934726825811275816/unknown.png"
            await funcs.sendImage(ctx, url)


def setup(botInstance):
    botInstance.add_cog(Minecraft(botInstance))
