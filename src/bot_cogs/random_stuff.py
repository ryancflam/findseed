# Credit - https://github.com/Littlemansmg/Discord-Meme-Generator
# For genmeme

from asyncio import TimeoutError, sleep
from datetime import datetime
from random import choice, choices, randint, shuffle
from time import time

from aiogtts import aiogTTS, lang
from deep_translator import GoogleTranslator
from discord import Colour, Embed, File, User
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

import config
from src.utils import funcs
from src.utils.base_cog import BaseCog
from src.utils.playing_cards import PlayingCards

COIN_EDGE_ODDS = 6001
RN_RANGE = 999999999999


class RandomStuff(BaseCog, name="Random Stuff", description="Some fun, random commands for you to kill time."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)
        self.client.loop.create_task(self.__readFiles())
        self.activeSpinners = []
        self.phoneWaitingChannels = []
        self.phoneCallChannels = []
        self.riggedChoice = ""

    async def __readFiles(self):
        self.personalityTest = await funcs.readJson(funcs.getResource(self.name, "personality_test.json"))
        self.trumpquotes = await funcs.readJson(funcs.getResource(self.name, "trump_quotes.json"))
        self.truths = await funcs.readTxt(funcs.getResource(self.name, "truths.txt"), lines=True)
        self.dares = await funcs.readTxt(funcs.getResource(self.name, "dares.txt"), lines=True)
        self.nhie = await funcs.readTxt(funcs.getResource(self.name, "nhie.txt"), lines=True)

    def makeMeme(self, filename: str, topString: str, bottomString: str=""):
        impact = funcs.PATH + funcs.getResource(self.name, "impact.ttf")
        img = Image.open(filename)
        imageSize = img.size
        fontSize = int(imageSize[1] / 5)
        fontSize2 = int(imageSize[1] / 5)
        font = ImageFont.truetype(impact, fontSize)
        font2 = ImageFont.truetype(impact, fontSize)
        topTextSize = font.getsize(topString)
        bottomTextSize = font2.getsize(bottomString)
        while topTextSize[0] > imageSize[0] - 20:
            fontSize = fontSize - 1
            font = ImageFont.truetype(impact, fontSize)
            topTextSize = font.getsize(topString)
        while bottomTextSize[0] > imageSize[0] - 20:
            fontSize2 = fontSize2 - 1
            font2 = ImageFont.truetype(impact, fontSize2)
            bottomTextSize = font2.getsize(bottomString)
        topTextPosition = ((imageSize[0] / 2) - (topTextSize[0] / 2), 0)
        bottomTextPosition = ((imageSize[0] / 2) - (bottomTextSize[0] / 2), imageSize[1] - bottomTextSize[1])
        draw = ImageDraw.Draw(img)
        outlineRange = int(fontSize / 15)
        outlineRange2 = int(fontSize2 / 15)
        for i in range(-outlineRange, outlineRange + 1):
            for j in range(-outlineRange, outlineRange + 1):
                draw.text((topTextPosition[0] + i, topTextPosition[1] + j), topString, (0, 0, 0), font=font)
        for i in range(-outlineRange2, outlineRange2 + 1):
            for j in range(-outlineRange2, outlineRange2 + 1):
                draw.text((bottomTextPosition[0] + j, bottomTextPosition[1] + j), bottomString, (0, 0, 0), font=font2)
        draw.text(topTextPosition, topString, (255, 255, 255), font=font)
        draw.text(bottomTextPosition, bottomString, (255, 255, 255), font=font2)
        imgName = f"{time()}.png"
        img.save(f"{funcs.PATH}/temp/{imgName}")
        return imgName

    @staticmethod
    async def inputOrAttachment(ctx, inp):
        if ctx.message.attachments:
            try:
                inp = await funcs.readTxtAttachment(ctx.message)
            except Exception as ex:
                funcs.printError(ctx, ex)
                inp = inp
        return inp

    @staticmethod
    def rgb(value):
        if value is not None:
            try:
                value = int(str(value).replace(",", ""))
                return value if 0 <= value <= 255 else randint(0, 255)
            except ValueError:
                return randint(0, 255)
        else:
            return randint(0, 255)

    def todEmbed(self, dare: int=0):
        if dare:
            q = choice(self.dares)
            etype = "Dare"
        else:
            q = choice(self.truths)
            etype = "Truth"
        return Embed(title="Truth or Dare", description=q).set_footer(text=etype)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="oohasecretcommand", hidden=True,
                      description="Ỳ̩̹̏͆ͅo̩͍̙͊́̂ù̧̦͘ ̙̩̓̀a̭̅r̜̀e̖̫̯̘͛̈́̌͋ ̛͙n̨̛͎̾͢͠ó̧̏͜t̻̥̙̏̔̔ ͒͢s̭̲̣̫̎̋͒̿u͖̝̖̬͂̆̈̉p̲̹̯̍̑̿p̨͔̒͊ò" 
                                  "̢s̱̭̮̘͒̀͝͝ë͉͖̞͍͉́͂̄̈́̉d̈͢ t̜̫͖̓͐͠ö̠̰̮͖́̐̕͘͜͞ ̥̤̲̤͗̑̆̕ḅ͎̼̫͗̾͐͛͗͜e̟̮͈͗̑͝ ̮̒h̐͟e̛̜͙̒r̼̜͍̟̿̓̓̿ë͙͙́.̪̥͌̾ " +
                                  "F̸͈̦͈͓͉̤̖̳͉̞̦̅͐̔͊̓͊̈̐̃̃ļ̵̘̻̺̱̣̦̙̣͉͔̼̘̓̉̈́̉̈͒̆͘̕͝͠ͅḙ̷̗̥̪̬̳̱̰̏͆̓̒̈́̽̈̒̽͗̅̂̐͘e̵̘̱͇͇̤̻̎̍ ̴̲̫̲͈̖̻̲̳̹̹̒͋̈́å̷̡͔͊̌̄͐̃̿̏͜ŗ̶̧̧̜̤̙̩̼̲̻̟̤̄̓̃̇̍͌͗̾͛̅̌̽̐́e̸" +
                                  "̼̭̯̈́̏͌̃̌̀̓́͂ǎ̸̰̥̠͙̃͂̕͘ ̷̡̢͍͚͈̜͈̻͚̯͖̯̙̖̖̽i̴̡͉͈̦̙̯̻̜̙͉̊͐͒̍̓ͅm̷̖̖͖̣̮͔͕͙̏̀́̅̀̈́̄͜͜͜m̵̯̫̋̆̍̒̽͗͋͌̔̑̓̈̍̕̕e̵̘̺̟̫̿̈̆͊͂͆͒̊̕͜d" +
                                  "̸͍͒́̂͗̏̔̇̓̊͂͘͠i̵̡̩͈̙̺͚̜̿̾͆̉̋̀̆̈́͛̕͠͝ă̵̛̬͓̤̠͈̝̮͑̀̔̌͊́̕̚͝͠͝t̵̟͛͛̆̀̑̓̇͆ḛ̵̢̺͖̺̒͝ḽ̵̡̢̡͈̮̤̲̖͍̺̦͖͘ͅỳ̵̖̰̟̦̑̈́̚.̸̛͔̠̬̱̭̭̞̟̦͂̆̿͋̌")
    async def oohasecretcommand(self, ctx):
        if await funcs.easterEggsPredicate(ctx):
            commandsList = list(filter(lambda x: not funcs.commandIsOwnerOnly(x),
                                       sorted(self.client.get_cog("Easter Eggs").get_commands(), key=lambda y: y.name)))
            m = await ctx.reply(", ".join(f"`{self.client.command_prefix}{str(command)}`" for command in commandsList)
                                + "\n\nDeletes: \"sigmax\", \"ankhazone\"")
        else:
            m = await ctx.reply(f"`{self.client.command_prefix}eeenable`")
        await sleep(1)
        await m.edit(content="Y̷o̸u̸ ̷d̴i̵d̶n̸'̷t̸ ̷s̶e̶e̶ ̸a̴n̵y̴t̷h̸i̸n̸g̵.̷")
        await sleep(0.5)
        await m.edit(content="Y̵̙͓̜̻̲̗̜̘͒̓̂̀̉̈́͛̂͌̀ǫ̵̨̛̳̼̪̂̈́̅̚ų̶̟̭̙̜̺̘̱̌̍̐̎̅̕ ̷͉̈́d̵͚̣̱͈̥͖͈͉̠̘̦̝͇͛̐͛͋̿͒̉͊̃̔̃͜͜ỉ̷̡̛͈̥̯̠͒̑͂̃̊̊̈́̚͝d̶̝̠͖̝̟͆̊͜ͅn̶̢̘̯͔̖͎̬͙̦̗̖͚͔̻̒̕'̵̨͙͇̳̋̑̏̔͊̌̐̆͘ţ̷̢̬̤̰͕̘̺̻͎͕̜͙͚͒̏̈́́̒̈́̊" +
                             " ̶̧̱͔̤̺̯̘̠͇̻͛͗͑̄ş̸̡̛͙̺͕̣͕̬̞̹͆̈́̈́͛̊̈̑̊̈́̌̓̄̚e̶̫̲̩̭̟̋̎́͂̇̂̊͜ͅḙ̷̤͕̓̆́̍͒͛͑̔ ̶͔̥̫͖̥̻̰̅͜a̴̧̮͐̾̃́̀͒͊̓̇̈́̃̐̍̚n̴̨̢̖̹̪̦̈́̊̍̈͒̾̅̋͂̽̽y̶̡͇̖̑t̴̛̮̘͉̘͐̋̔́͛͂̉̏͝" +
                             "h̶̙̳̖̲̙̳̲͎͕̝̝͈͙̝̏́̃̍̑́͛̈̄̿̚͘͜ỉ̶̜̦̓͗͊̓͒̏̕͝n̶̨͔̙͎̠̲̼̩͖̖͕͐̑̽̃͊͜͝ͅͅg̶̞͎̊̂̃͆́͑̿̚͝͝.̷̨̢̡͇̜͙̼̬̗͕͙̣̤͕̈́͆͜")
        await sleep(0.5)
        await m.delete()

    """ Disabled """
    # @commands.cooldown(1, 5, commands.BucketType.user)
    # @commands.command(name="wyr", description="Sends a random Would You Rather question.", aliases=["rather", "wouldyourather"])
    # async def wyr(self, ctx):
    #     try:
    #         res = await funcs.getRequest("http://either.io/questions/next/1")
    #         data = res.json()["questions"][0]
    #         total1 = int(data['option1_total'])
    #         total2 = int(data['option2_total'])
    #         total = total1 + total2
    #         opt1 = data['option_1']
    #         opt2 = data['option_2']
    #         info = data['moreinfo']
    #         e = Embed(title="Would You Rather",
    #                   description=f"🔵 {opt1 + ('' if opt1.endswith('.') else '.')}\n🔴 {opt2 + ('' if opt1.endswith('.') else '.')}")
    #         e.add_field(
    #             name="Option #1 Votes", value="`{:,} ({}%)`".format(total1, funcs.removeDotZero(round(total1 / total * 100, 2)))
    #         )
    #         e.add_field(
    #             name="Option #2 Votes", value="`{:,} ({}%)`".format(total2, funcs.removeDotZero(round(total2 / total * 100, 2)))
    #         )
    #         if info:
    #             e.set_footer(text=info)
    #         yes = True
    #     except Exception as ex:
    #         funcs.printError(ctx, ex)
    #         e = funcs.errorEmbed(None, "Server error.")
    #         yes = False
    #     msg = await ctx.send(embed=e)
    #     if yes:
    #         await msg.add_reaction("🔵")
    #         await msg.add_reaction("🔴")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="nhie", description="Sends a random Never Have I Ever question.",
                      aliases=["never", "ever", "neverhavei", "neverhaveiever"])
    async def nhie(self, ctx):
        await ctx.send(embed=Embed(title="Never Have I Ever...", description="..." + choice(self.nhie)))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="tod", description="Sends a random Truth or Dare question.",
                      aliases=["truthordare"])
    async def tod(self, ctx):
        await ctx.send(embed=self.todEmbed(dare=randint(0, 1)))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="truth", description="Sends a random Truth or Dare truth question.", aliases=["truths"])
    async def truth(self, ctx):
        await ctx.send(embed=self.todEmbed())

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="dare", description="Sends a random Truth or Dare dare.", aliases=["dares"])
    async def dare(self, ctx):
        await ctx.send(embed=self.todEmbed(dare=1))

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="literalchinese", usage="<Chinese/Japanese/Korean text (50 characters or less)>",
                      description="Literally translates Chinese, Japanese, and Korean characters to English one by one. " +
                                  "Translation may sometimes fail due to rate limit.",
                      aliases=["lc", "literaljapanese", "literalkorean"], hidden=True)
    async def literalchinese(self, ctx, *, inp):
        g = GoogleTranslator(source="auto", target="en")
        try:
            output = await funcs.funcToCoro(g.translate_batch, list(inp.replace(" ", "").replace("\n", ""))[:50])
            e = Embed(title="Literal Chinese", description=funcs.formatting(" ".join(output)))
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Rate limit reached, try again later.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 30, commands.BucketType.user)
    @commands.command(name="literalenglish", aliases=["le"], usage="<English text (50 words or less)>",
                      description="Literally translates English words to Chinese one by one. " +
                                  "Translation may sometimes fail due to rate limit.", hidden=True)
    async def literalenglish(self, ctx, *, inp):
        g = GoogleTranslator(source="auto", target="zh-TW")
        try:
            output = await funcs.funcToCoro(g.translate_batch, inp.split()[:50])
            e = Embed(title="Literal English", description=funcs.formatting("".join(output)))
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Rate limit reached, try again later.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="telephone", aliases=["phone", "userphone", "call"],
                      description="Talk to other users from other servers! This is an experimental feature and may not work.")
    async def telephone(self, ctx):
        if ctx.channel in self.phoneWaitingChannels:
            return await ctx.reply(":telephone: Cancelling phone call.")
        if ctx.channel in self.phoneCallChannels:
            return await ctx.reply(
                embed=funcs.errorEmbed(None, "A phone call is already in progress in this channel.")
            )
        self.phoneWaitingChannels.append(ctx.channel)
        await ctx.reply(":telephone_receiver: Waiting for another party to pick up the phone...")
        if len(self.phoneWaitingChannels) == 1:
            sleepTime = 0
            while len(self.phoneWaitingChannels) == 1 and sleepTime < 120:
                if len(self.phoneWaitingChannels) == 1 and sleepTime >= 120:
                    self.phoneWaitingChannels.remove(ctx.channel)
                    return await ctx.send(":telephone: Seems like no one is answering; cancelling phone call.")
                await sleep(0.25)
                sleepTime += 1
        if len(self.phoneWaitingChannels) == 2:
            otherParty = self.phoneWaitingChannels[1 if not self.phoneWaitingChannels.index(ctx.channel) else 0]
            await sleep(1)
            self.phoneWaitingChannels.remove(ctx.channel)
            self.phoneCallChannels.append(ctx.channel)
            resetTime = 0
            startCall = time()
            hangup = False
            await ctx.send(
                ":telephone_receiver: Someone has picked up the phone, say hello! " +
                "Note that not all messages will be sent. Type `!hangup` to hang up."
            )
            while resetTime < 30 and not hangup and otherParty in self.phoneCallChannels:
                try:
                    msg = await self.client.wait_for(
                        "message", timeout=1, check=lambda mm: mm.channel == ctx.channel and mm.author != self.client.user
                    )
                    if msg.content.casefold() == "!hangup":
                        relay = ":telephone: The other party has hung up the phone."
                        await msg.reply(":telephone: You have hung up the phone.")
                        hangup = True
                    else:
                        relay = f"**{msg.author}** » {msg.content}" + \
                                f"{msg.attachments[0].url if msg.attachments else ''}"
                    await otherParty.send(relay[:2000])
                    resetTime = 0
                except TimeoutError:
                    resetTime += 1
                    if resetTime == 30:
                        await ctx.send(":telephone: You have been idling for too long. Hanging up the phone...")
                        await otherParty.send(":telephone: The other party has hung up the phone.")
            m, s = funcs.minSecs(time(), startCall)
            self.phoneCallChannels.remove(ctx.channel)
            return await funcs.sendTime(ctx, m, s)
        self.phoneWaitingChannels.remove(ctx.channel)
        await ctx.send(":telephone: Seems like no one is answering; cancelling phone call.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="personalitytest", description="Take a personality test consisting of 88 questions for fun.",
                      aliases=["mbti", "personality", "personalities", "16p", "16personalities"])
    async def personalitytest(self, ctx):
        await ctx.reply("```== Please Read ==\n\nYou are about to take a low-level personality test consisting of 88 q" +
                       "uestions. The test should take around 20 to 30 minutes to complete. To select an answer, inpu" +
                       "t either 'a', 'b', or 'c'. Try to leave out as many neutral answers as possible. There " +
                       "are no right or wrong answers.\n\nPlease note that this test does not consider the eight " +
                       "cognitive functions and was created purely for fun. For more accurate and meaningful" +
                       " results, it is recommended that you study each of the cognitive functions and type yourself " +
                       "based on those functions with the help of a test that makes good use of them.\n\nIf " +
                       "you want to quit, input 'quit'. Otherwise, input 'test' to start the test.\n\n" +
                       "Questions provided by EDCampus. Each question has a 15-minute time limit.```")
        try:
            userchoice = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=300
            )
        except TimeoutError:
            return await ctx.send(f"`{ctx.author.name} has left the personality test for idling for too long.`")
        if userchoice.content.casefold() != "test":
            return await ctx.send(f"`{ctx.author.name} has left the personality test.`")
        res = list(self.personalityTest["questions"])
        e, i, s, n, t, f, j, p = 0, 0, 0, 0, 0, 0, 0, 0
        ei = ["1.", "5.", "9.", "13", "17", "21", "25", "29", "33", "37", "41",
              "45", "49", "53", "57", "61", "65", "69", "73", "77", "81", "85"]
        sn = ["2.", "6.", "10", "14", "18", "22", "26", "30", "34", "38", "42",
              "46", "50", "54", "58", "62", "66", "70", "74", "78", "82", "86"]
        tf = ["3.", "7.", "11", "15", "19", "23", "27", "31", "35", "39", "43",
              "47", "51", "55", "59", "63", "67", "71", "75", "79", "83", "87"]
        userchoices = [0, 1]
        questionNumbers = [i for i in range(88)]
        questionCount, choiceCount = 1, 1
        userchoice = None
        shuffle(questionNumbers)
        for x in questionNumbers:
            userInput = ""
            title = res[x]["title"]
            question = f"{title.split('. ')[1]}\n\n"
            shuffle(userchoices)
            for userchoice in userchoices:
                sub = "a) " if choiceCount == 1 else "b) "
                choiceCount = 2 if choiceCount == 1 else 1
                question += sub + res[x]["selections"][userchoice] + "\n"
            await ctx.send(f"```Question {questionCount} of 88 for {ctx.author.name}:\n\n{question[:-1]}\n" +
                           "c) none of the above/neutral.```")
            while userInput.casefold() != "a" and userInput.casefold() != "b" \
                    and userInput.casefold() != "c" and userInput.casefold() != "quit" \
                    and userInput.casefold() != "exit" and userInput.casefold() != "leave":
                try:
                    answer = await self.client.wait_for(
                        "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=900
                    )
                except TimeoutError:
                    return await ctx.send(f"`{ctx.author.name} has left the personality test for idling for too long.`")
                userInput = answer.content
                if userInput.casefold() != "a" and userInput.casefold() != "b" \
                        and userInput.casefold() != "c" and userInput.casefold() != "quit" \
                        and userInput.casefold() != "exit" and userInput.casefold() != "leave":
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
            if userInput.casefold() == "quit" or userInput.casefold() == "exit" \
                    or userInput.casefold() == "leave":
                return await ctx.send(f"`{ctx.author.name} has left the personality test.`")
            if userInput.casefold() == "a" and userchoice == 1 \
                    or userInput.casefold() == "b" and not userchoice:
                if any(res[x]["title"].startswith(y) for y in ei):
                    e += 1
                elif any(res[x]["title"].startswith(y) for y in sn):
                    s += 1
                elif any(res[x]["title"].startswith(y) for y in tf):
                    t += 1
                else:
                    j += 1
            elif userInput.casefold() == "b" and userchoice == 1 \
                    or userInput.casefold() == "a" and not userchoice:
                if any(res[x]["title"].startswith(y) for y in ei):
                    i += 1
                elif any(res[x]["title"].startswith(y) for y in sn):
                    n += 1
                elif any(res[x]["title"].startswith(y) for y in tf):
                    f += 1
                else:
                    p += 1
            else:
                if any(res[x]["title"].startswith(y) for y in ei):
                    e += 0.5
                    i += 0.5
                elif any(res[x]["title"].startswith(y) for y in sn):
                    s += 0.5
                    n += 0.5
                elif any(res[x]["title"].startswith(y) for y in tf):
                    t += 0.5
                    f += 0.5
                else:
                    j += 0.5
                    p += 0.5
            questionCount += 1
        eifavour = e if e > i else i
        snfavour = s if s > n else n
        tffavour = t if t > f else f
        jpfavour = j if j > p else p
        eir = "Extraverted - " if e > i else "Extraverted/Introverted? - " if e == i else "Introverted - "
        snr = "Sensing - " if s > n else "Sensing/iNtuitive? - " if s == n else "iNtuitive - "
        tfr = "Thinking - " if t > f else "Thinking/Feeling? - " if t == f else "Feeling - "
        jpr = "Judging - " if j > p else "Judging/Perceiving? - " if j == p else "Perceiving - "
        eic = "E" if e > i else "X" if e == i else "I"
        snc = "S" if s > n else "X" if s == n else "N"
        tfc = "T" if t > f else "X" if t == f else "F"
        jpc = "J" if j > p else "X" if j == p else "P"
        eipercent = eifavour / 22
        snpercent = snfavour / 22
        tfpercent = tffavour / 22
        jppercent = jpfavour / 22
        eis = "{:.0%}".format(eipercent)
        sns = "{:.0%}".format(snpercent)
        tfs = "{:.0%}".format(tfpercent)
        jps = "{:.0%}".format(jppercent)
        await ctx.send(f"```== {ctx.author.name}'s Personality Test Result " +
                       f"==\n\n{eir}{eis}\n{snr}{sns}\n{tfr}{tfs}\n{jpr}{jps}\n\nYour four-letter " +
                       f"personality code is '{eic}{snc}{tfc}{jpc}'.\n\nOnce again, this test is " +
                       "only for fun and should not be treated as a professional assessment. " +
                       "Thank you for trying out this test!```")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="dadjoke", description="Sends a random dad joke.", aliases=["dj", "joke"], hidden=True)
    async def dadjoke(self, ctx):
        try:
            res = await funcs.getRequest("https://icanhazdadjoke.com/", headers={"Accept": "application/json"})
            await ctx.reply(res.json()["joke"])
        except Exception as ex:
            funcs.printError(ctx, ex)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="yomama", description="Sends a random yo mama joke.",
                      aliases=["yomoma", "yomomma", "yomamma", "yomom"], hidden=True)
    async def yomama(self, ctx):
        try:
            res = await funcs.getRequest("https://api.yomomma.info/")
            await ctx.reply(res.json()["joke"])
        except Exception as ex:
            funcs.printError(ctx, ex)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="food", description="Sends a random food image.", hidden=True, aliases=["foodpic", "foodporn"])
    async def food(self, ctx):
        try:
            res = await funcs.getRequest("https://foodish-api.herokuapp.com/api/")
            await funcs.sendImage(ctx, res.json()["image"])
        except Exception as ex:
            funcs.printError(ctx, ex)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="coffee", description="Sends a random coffee image.", hidden=True)
    async def coffee(self, ctx):
        try:
            await funcs.sendImage(ctx, "https://coffee.alexflipnote.dev/random")
        except Exception as ex:
            funcs.printError(ctx, ex)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="dog", description="Sends a random dog image.", hidden=True)
    async def dog(self, ctx):
        try:
            res = await funcs.getRequest("https://dog.ceo/api/breeds/image/random")
            await funcs.sendImage(ctx, res.json()["message"])
        except Exception as ex:
            funcs.printError(ctx, ex)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cat", description="Sends a random cat image.", hidden=True)
    async def cat(self, ctx):
        try:
            res = await funcs.getRequest("https://api.thecatapi.com/v1/images/search")
            image = res.json()[0]["url"]
            await funcs.sendImage(ctx, image, name=image.split("thecatapi.com/images/")[1])
        except Exception as ex:
            funcs.printError(ctx, ex)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="trumpthinks", description="What does Donald Trump think about something or someone?",
                      aliases=["whatdoestrumpthink", "plstrump", "trump", "asktrump", "tt", "tq"], usage="<input>")
    async def trumpthinks(self, ctx, *, something: str=""):
        if something == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None, "Please enter 100 characters or less.")
        else:
            quotes = choice(self.trumpquotes["messages"]["list"])
            e = Embed(
                title=f"What does Trump think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name="Trump Thinks", value=f"```{something} {quotes}```")
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/659771291858894849/673599147160502282/trumpface.png")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="roast", description="Roasts a user.", aliases=["insult", "toast"],
                      usage="[@mention]", hidden=True)
    async def roast(self, ctx, member: User=None):
        member = member or ctx.message.author
        res = await funcs.getRequest("https://insult.mattbas.org/api/insult.json")
        await ctx.reply(res.json()["insult"].replace("You are", f"{member.display_name} is"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="fidgetspinner", description="Spins a fidget spinner.",
                      aliases=["spin", "spinner", "youspinmerightround"], hidden=True)
    async def fidgetspinner(self, ctx):
        if ctx.author.id in self.activeSpinners:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Your fidget spinner is still spinning, please wait!"))
        self.activeSpinners.append(ctx.message.author.id)
        try:
            url = choice([
                "https://media.giphy.com/media/cnY70GhrM5nJ6/giphy.gif",
                "https://media.giphy.com/media/cwT3y6UFFseGc/giphy.gif",
                "https://media.giphy.com/media/1Ubrzxvik2puE/giphy.gif",
                "https://files.gamebanana.com/img/ico/sprays/593404c44a588.gif",
                "https://gifimage.net/wp-content/uploads/2017/11/fidget-spinner-gif-transparent-6.gif"
            ])
            await funcs.sendImage(ctx, url, name="spinner.gif",
                                  message=f"<:fidgetspinner:675314386784485376> **{ctx.author.name} has spun a fidget"+
                                          " spinner. Let's see how long it lasts...** <:fidgetspinner:675314386784485376>")
            randomSeconds = randint(5, 180)
            await sleep(randomSeconds)
            await ctx.send(
                f"<:fidgetspinner:675314386784485376> **{ctx.message.author.name}'s fidget spinner has just stopped " +
                f"spinning; it lasted {randomSeconds} seconds!** <:fidgetspinner:675314386784485376>"
            )
            self.activeSpinners.remove(ctx.message.author.id)
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.send(embed=funcs.errorEmbed(None, "An error occurred. Please try again later."))
            try:
                self.activeSpinners.remove(ctx.message.author.id)
            except ValueError:
                return

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="iq", description="Calculates your IQ. This is a joke command.", usage="[@mention]", hidden=True)
    async def iq(self, ctx, mention: User=None):
        if not mention:
            mention = ctx.author
        iqres = randint(1, 200)
        if iqres < 80:
            msg = [
                "wow ur dum lololol",
                "STOOOPIDDDDDD",
                "U ARE AN IDIOT HAHAHAHAHAHAHAHAHA",
                "lmao dumbass",
                "what's 9+10?"
            ]
        elif iqres > 120:
            msg = [
                "k cool ur smart",
                "wow you got the smarts!!",
                "Intellectual.",
                "Harvard wants to know your location",
                "you like the NAWLEJ?",
                "Audible approves"
            ]
        else:
            msg = [
                "Nothing special whatsoever...",
                "ehhhh okay",
                "ur average",
                "yeah you are average-brained, absolutely nothing out of the ordinary",
                "lame"
            ]
        await ctx.reply(f"{mention.mention}'s IQ score is **{iqres}**.\n\n{choice(msg)}")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="lovecalc", description="Calculates the love percentage between two things or users with an algorithm.",
                      aliases=["love", "lovecalculator", "calclove"], usage="<input> [input]", hidden=True)
    async def lovecalc(self, ctx, first: str="", second: str=""):
        if not first:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        second = second or f"<@!{ctx.author.id}>"
        try:
            newlist = sorted([first, second])
            sentence = ""
            for i in newlist:
                sentence += str(i) + " loves "
            sentence = sentence[:-7]
            sentence = sentence.replace(" ", "").casefold()
            intermediate = ""
            while len(sentence):
                intermediate += str(sentence.count(sentence[0]))
                sentence = sentence.replace(sentence[0], "")
            while int(intermediate) > 100:
                tmp = ""
                for i in range(0, int(len(intermediate) / 2)):
                    tmp += str(int(intermediate[i]) + int(intermediate[(i + 1) * -1]))
                if len(intermediate) % 2 > 0:
                    tmp += intermediate[int(len(intermediate) % 2)]
                intermediate = tmp
            emoji = "!** :sparkling_heart:"
            if 49 < int(intermediate) < 80:
                emoji = "!** :heart:"
            if int(intermediate) < 50:
                emoji = "...** :brown_heart:"
            if int(intermediate) < 20:
                emoji = "...** :broken_heart:"
            await ctx.reply("The love percentage between " +
                            f"**{newlist[0]}** and **{newlist[1]}** is **{intermediate}%{emoji}")
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(embed=funcs.errorEmbed(None, "An error occurred. Invalid user?"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="8ball", description="Ask 8ball a question.",
                      aliases=["8b", "8"], usage="[input]")
    async def eightball(self, ctx, *, msg: str=""):
        mention = ctx.author.mention
        responses = [
            "It is certain.",
            "Reply hazy, try again.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and try again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful."
        ]
        await ctx.reply(
            f":8ball: {mention}: `{choice(['Empty input...', 'I cannot hear you.']) if not msg else choice(responses)}`"
        )

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="tts", description="Converts text to speech.", aliases=["texttospeech", "speech"],
                      usage='<language code> <input OR text attachment>')
    async def tts(self, ctx, langcode, *, inp=""):
        langs = lang.tts_langs()
        if langcode not in langs:
            langcode = langcode.casefold()
            if langcode not in langs:
                return await ctx.reply(embed=funcs.errorEmbed(
                    "Invalid language code!", "Valid options:\n\n" + ", ".join(f'`{i}`' for i in sorted(langs.keys()))
                ))
        inp = await self.inputOrAttachment(ctx, inp)
        if not inp:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        location = f"{time()}.mp3"
        await aiogTTS().save(inp, f"{funcs.PATH}/temp/{location}", slow=False, lang=langcode)
        file = File(f"{funcs.PATH}/temp/" + location)
        try:
            await ctx.reply(file=file)
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(embed=funcs.errorEmbed(None, "The generated file is too large!"))
        await funcs.deleteTempFile(location)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="brian", description="Converts text to speech with the Brian voice.",
                      usage='<input OR text attachment (3,000 characters or less)>')
    async def brian(self, ctx, *, inp=""):
        url = "https://api.streamelements.com/kappa/v2/speech?voice=Brian&text="
        inp = await self.inputOrAttachment(ctx, inp)
        if not inp:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        res = await funcs.getImageFile((url + inp.replace("\n", " "))[:3000], name=f"{time()}.mp3")
        try:
            await ctx.reply(file=res)
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(embed=funcs.errorEmbed(None, "The generated file is too large!"))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="flipcoin", description="Flips coins.", usage="[amount up to 100]",
                      aliases=["coins", "flip", "fc", "coin", "coinflip",
                               "flipcoins", "tosscoins", "cointoss", "tosscoin", "toss"])
    async def flipcoin(self, ctx, amount: str="1"):
        try:
            amount = int(amount)
        except ValueError:
            amount = 1
        if not 0 < amount < 101:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Amount must be between 1 and 100."))
        coins = []
        total = {"Heads": 0, "Tails": 0, "Edge": 0}
        for _ in range(amount):
            randomcoin = randint(1, COIN_EDGE_ODDS)
            coins.append(
                "Heads" if randomcoin <= ((COIN_EDGE_ODDS - 1) / 2) else "Tails" if randomcoin < COIN_EDGE_ODDS else "Edge"
            )
            total[coins[-1]] += 1
        if amount == 1:
            isEdge = coins[0] == "Edge"
            thumbnail = "https://upload.wikimedia.org/wikipedia/commons/6/67/1_oz_Vienna_Philharmonic_2017_edge.png" \
                        if isEdge else f"https://flipacoin.fun/images/coin/coin{'1' if coins[0] == 'Heads' else '2'}.png"
            e = Embed(title="OMG NO WAY!" if isEdge else coins[0], description=f"Requested by: {ctx.author.mention}")
            e.set_image(url=thumbnail)
            if isEdge:
                e.set_footer(text="1 in {:,} chance".format(COIN_EDGE_ODDS))
            await ctx.reply(embed=e)
        else:
            result = ""
            for i in range(1, 4):
                cointype = 'Heads' if i == 1 else 'Tails' if i == 2 else 'Edge'
                result += "\n{}{}: {} time{}".format(
                    cointype, (" (1 in {:,} chance)".format(COIN_EDGE_ODDS) if i == 3 else ""),
                    total[cointype], "s" if total[cointype] > 1 else ""
                ) if total[cointype] else ""
            await ctx.reply(f"```{', '.join(coin for coin in coins)}\n{result}\n\nRequested by: {ctx.author}```")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="rolldice", description="Rolls dice.", usage="[amount up to 100]",
                      aliases=["die", "roll", "rd", "dice", "rolldie", "diceroll", "dieroll"])
    async def rolldice(self, ctx, amount: str="1"):
        try:
            amount = int(amount)
        except ValueError:
            amount = 1
        if not 0 < amount < 101:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Amount must be between 1 and 100."))
        dice = []
        total = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for _ in range(amount):
            randomdice = randint(1, 6)
            dice.append(randomdice)
            total[randomdice] += 1
        if amount == 1:
            e = Embed(title=dice[0], description=f"Requested by: {ctx.author.mention}")
            e.set_image(url=f"https://rolladie.net/images/dice/dice{dice[0]}.jpg")
            await ctx.reply(embed=e)
        else:
            result = ""
            for i in range(1, 7):
                result += f"\n{i}: {total[i]} time{'s' if total[i] > 1 else ''}" if total[i] else ""
            dicesum = sum(dice)
            possiblepts = amount * 6
            await ctx.reply(
                f"```{', '.join(str(die) for die in dice)}\n{result}\n\nTotal value: " +
                f"{dicesum} out of {possiblepts} ({round(dicesum / possiblepts * 100, 3)}%)\n\nRequested by: {ctx.author}```"
            )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="randomcard", description="Deals cards.", usage="[amount up to 52]",
                      aliases=["rc", "cards", "deal", "card", "randomcards", "dc", "dealcard", "dealcards"])
    async def randomcard(self, ctx, amount: str="1"):
        try:
            amount = int(amount)
        except ValueError:
            amount = 1
        pc = PlayingCards()
        try:
            cards = pc.randomCard(amount)
        except Exception as ex:
            return await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))
        if amount == 1:
            e = Embed(title=pc.returnCardName(cards[0]), description=f"Requested by: {ctx.author.mention}")
            e.set_image(url=pc.returnCardImage(cards[0]))
            await ctx.reply(embed=e)
        else:
            await ctx.reply(
                "```{}\n\nRequested by: {}```".format(
                    "\n".join(f"{card} | {pc.returnCardName(card)}" for card in cards), ctx.author
                )
            )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="randomnumber", usage="[starting number] [range up to {:,}]".format(RN_RANGE),
                      aliases=["rn", "numbers", "number", "rng"], description="Generates a random number.")
    async def randomnumber(self, ctx, start: str= "1", rnrange: str=str(RN_RANGE)):
        try:
            rnrange = int(rnrange)
            if not 0 < rnrange < (RN_RANGE + 1):
                rnrange = RN_RANGE
        except ValueError:
            rnrange = RN_RANGE
        try:
            start = 1 if int(start) >= rnrange else int(start)
        except ValueError:
            start = 1
        await ctx.reply("```{:,} (Range: {:,} to {:,})\n\nRequested by: {}```".format(
            randint(start, rnrange), start, rnrange, ctx.author
        ))

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="randomcolour", usage="[colour hex OR R value] [G value] [B value]",
                      description="Generates a random colour.",
                      aliases=["color", "randomcolor", "colour", "colors", "colours", "rgb"])
    async def randomcolour(self, ctx, r=None, g=None, b=None):
        if r:
            colour = r[(1 if len(r) == 7 else 2 if r.casefold().startswith("0x") else 0):]
            if len(colour) == 6:
                try:
                    r, g, b = (int(colour[i:i + 2], 16) for i in (0, 2, 4))
                except ValueError:
                    r = self.rgb(r)
            else:
                r = self.rgb(r)
        else:
            r = self.rgb(r)
        g = self.rgb(g)
        b = self.rgb(b)
        colour = "%02x%02x%02x" % (r, g, b)
        e = Embed(colour=Colour(int(colour, 16)), title="#" + colour.casefold(),
                  description=f"Requested by: {ctx.author.mention}")
        e.add_field(name="RGB", value=f"`{r}, {g}, {b}`")
        e.set_image(url=f"https://www.colorhexa.com/{colour}.png")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="randomhex", usage="<digits>", aliases=["rhex", "hex", "hexadecimal", "randomhexadecimal"],
                      description="Generates a random hexadecimal number with a certain number of digits.")
    async def randomhex(self, ctx, digits):
        try:
            digits = int(digits.replace(",", ""))
        except:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))
        e = Embed(title="{:,}-Digit Hexadecimal".format(digits), description=f"```{funcs.randomHex(digits)}```")
        try:
            await ctx.reply(embed=e)
        except:
            await ctx.reply(embed=funcs.errorEmbed(None, "The result is too long!"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="randomchoice", usage="<items separated with ;>",
                      aliases=["shuffle", "list", "choose", "choice"], description="Picks a random item from a given list.")
    async def randomchoice(self, ctx, *, items):
        try:
            itemslist = funcs.itemSeparator(items)
            if ctx.author == (await self.client.application_info()).owner and self.riggedChoice in itemslist:
                item = self.riggedChoice
            else:
                item = choice(itemslist)
            e = Embed(title=f"{self.client.user.name} Chooses...",
                      description=f"Requested by: {ctx.author.mention}\n{funcs.formatting(item)}")
            e.add_field(name="Items ({:,})".format(len(itemslist)), value=", ".join(f"`{i}`" for i in itemslist))
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, str(ex))
        await ctx.reply(embed=e)

    @commands.command(name="rigchoice", description="Rigs !randomchoice because it's funny.",
                      usage="[desired choice]", hidden=True, aliases=["rigged", "riggy"])
    @commands.is_owner()
    async def rigchoice(self, ctx, *, text: str=""):
        if not text:
            self.riggedChoice = ""
            await ctx.reply(f"No longer rigging {self.client.command_prefix}randomchoice")
        else:
            self.riggedChoice = text
            await ctx.reply(f"Rigged {self.client.command_prefix}randomchoice to display the following item: `{text}`")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="shrek", description="Shrek.", hidden=True)
    async def shrek(self, ctx):
        await ctx.reply("https://imgur.com/gallery/IsWDJWa")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="titlecase", usage="<input>", aliases=["title", "capitalise", "capitalize"],
                      description="Titlecase.", hidden=True)
    async def titlecase(self, ctx, *, text: str=""):
        if not text:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        await ctx.reply(text.title())

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="lowercase", usage="<input>", aliases=["lower", "casefold", "whisper"],
                      description="lowercase.", hidden=True)
    async def lowercase(self, ctx, *, text: str=""):
        if not text:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        await ctx.reply(text.casefold())

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="uppercase", usage="<input>", aliases=["capslock", "shout", "scream", "upper", "caps"],
                      description="UPPERCASE.", hidden=True)
    async def uppercase(self, ctx, *, text: str=""):
        if not text:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        await ctx.reply(text.upper())

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="reverse", usage="<input>", aliases=["reversed", "rev"],
                      description=".txet ruoy sesreveR", hidden=True)
    async def reverse(self, ctx, *, text: str=""):
        if not text:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        await ctx.reply(text[::-1])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="weirdcase", usage="<input>", aliases=["mixedcase", "weird"],
                      description="MakEs yOuR TExT lOok sOmEthInG LikE tHiS.", hidden=True)
    async def weirdcase(self, ctx, *, text: str=""):
        if not text:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        await ctx.reply(funcs.weirdCase(text))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="glitchtext", usage="<input>", aliases=["glitch", "textglitch"],
                      description="Glitches text.", hidden=True)
    async def glitchtext(self, ctx, *, text: str=""):
        if text == "":
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        top = ["\u030d", "\u030e", "\u0304", "\u0305", "\u033f", "\u0311", "\u0306", "\u0310", "\u0352", "\u0357",
               "\u0351", "\u0307", "\u0308", "\u030a", "\u0342", "\u0343", "\u0344", "\u034a", "\u034b", "\u034c",
               "\u0303", "\u0302", "\u030c", "\u0350", "\u0300", "\u0301", "\u030b", "\u030f", "\u0312", "\u0313",
               "\u0314", "\u033d", "\u0309", "\u0363", "\u0364", "\u0365", "\u0366", "\u0367", "\u0368", "\u0369",
               "\u036a", "\u036b", "\u036c", "\u036d", "\u036e", "\u036f", "\u033e", "\u035b", "\u0346", "\u031a"]
        mid = ["\u0315", "\u031b", "\u0340", "\u0341", "\u0358", "\u0321", "\u0322", "\u0327", "\u0328", "\u0334",
               "\u0335", "\u0336", "\u034f", "\u035c", "\u035d", "\u035e", "\u035f", "\u0360", "\u0362", "\u0338",
               "\u0337", "\u0361", "\u0489", "\u20DE", "\u20DF", "\u20E0", "\u20E2", "\u20E4"]
        bottom = ["\u0316", "\u0317", "\u0318", "\u0319", "\u031c", "\u031d", "\u031e", "\u031f", "\u0320", "\u0324",
                  "\u0325", "\u0326", "\u0329", "\u032a", "\u032b", "\u032c", "\u032d", "\u032e", "\u032f", "\u0330",
                  "\u0331", "\u0332", "\u0333", "\u0339", "\u033a", "\u033b", "\u033c", "\u0345", "\u0347", "\u0348",
                  "\u0349", "\u034d", "\u034e", "\u0353", "\u0354", "\u0355", "\u0356", "\u0359", "\u035a", "\u0323"]
        res = ""
        for char in text:
            ranlevel = randint(20, 80)
            glitch = choices(bottom, k=ranlevel)
            glitch += choices(top, k=ranlevel)
            glitch += choice(mid)
            res += char + "".join(glitch)
        await ctx.reply(res[:2000])

    # @commands.cooldown(1, 20, commands.BucketType.user)
    # @commands.command(name="gentext", description="Generates text based on your input.",
    #                   aliases=["tg", "textgen", "gt", "chatgpt", "gpt", "chadgpt"], usage="<input>")
    # async def gentext(self, ctx, *, text=""):
    #     empty, resjson = False, None
    #     try:
    #         if text:
    #             await ctx.send("Processing text. Please wait...")
    #         else:
    #             empty = True
    #             raise Exception("Empty input.")
    #         res = await funcs.postRequest(
    #             "https://api.deepai.org/api/text-generator",
    #             data={"text": text}, headers={"api-key": config.deepAIKey}
    #         )
    #         resjson = res.json()
    #         e = Embed(title="Text Generation", description=funcs.formatting(resjson["output"].replace("```", "")))
    #         delbutton = True
    #     except Exception as ex:
    #         if not empty:
    #             funcs.printError(ctx, ex)
    #         e = funcs.errorEmbed(None, str(ex) if not resjson else resjson["err"])
    #         delbutton = False
    #     m = await ctx.reply(embed=e)
    #     if delbutton:
    #         await m.edit(view=DeleteButton(ctx, self.client, m))

    # @commands.cooldown(1, 30, commands.BucketType.user)
    # @commands.command(name="genimg", usage="<input> [\"-hq\" or \"-hd\" for high quality]",
    #                   description="Generates images based on your input. Warning: May generate inappropriate images.",
    #                   aliases=["ti", "imggen", "genimage", "imagegen", "imgen", "image", "img", "gi", "ig"])
    # async def genimg(self, ctx, *, text=""):
    #     empty, resjson, img = False, None, None
    #     try:
    #         if text:
    #             if text.casefold().endswith("-hq") or text.casefold().endswith("-hd"):
    #                 text = text[:-3]
    #                 data = {"text": text, "image_generator_version": "hd"}
    #                 hq = True
    #             else:
    #                 data = {"text": text}
    #                 hq = False
    #             await ctx.send(f"Generating {'HQ ' if hq else ''}image. Please wait...")
    #         else:
    #             empty = True
    #             raise Exception("Empty input.")
    #         res = await funcs.postRequest(
    #             "https://api.deepai.org/api/text2img",
    #             data=data, headers={"api-key": config.deepAIKey}
    #         )
    #         resjson = res.json()
    #         imgname = str(time()) + ".png"
    #         img = await funcs.getImageFile(resjson["output_url"], name=imgname)
    #         e = Embed(title="Image Generation").set_image(url="attachment://" + imgname)
    #         delbutton = True
    #     except Exception as ex:
    #         if not empty:
    #             funcs.printError(ctx, ex)
    #         e = funcs.errorEmbed(None, str(ex) if not resjson else resjson["err"])
    #         delbutton = False
    #     m = await ctx.reply(embed=e, file=img)
    #     if delbutton:
    #         await m.edit(view=DeleteButton(ctx, self.client, m))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="colouriser", description="Colourises a black-and-white image.", usage="<image URL OR image attachment>",
                      aliases=["colourise", "coloriser", "colorise", "colourizer", "colourize", "colorizer", "colorize"])
    async def colouriser(self, ctx, url=None):
        resjson, img = None, None
        if not ctx.message.attachments:
            await sleep(3)
        try:
            if ctx.message.attachments:
                imglink = ctx.message.attachments[0].url
            elif url:
                imglink = url
            else:
                raise Exception("No attachment or URL detected, please try again.")
            await ctx.send("Reading image. Please wait... " +
                           "(URL embeds take longer to process than image attachments)")
            res = await funcs.postRequest(
                "https://api.deepai.org/api/colorizer",
                data={"image": imglink}, headers={"api-key": config.deepAIKey}
            )
            resjson = res.json()
            imgname = str(time()) + ".png"
            img = await funcs.getImageFile(resjson["output_url"], name=imgname)
            e = Embed(title="Colouriser").set_image(url="attachment://" + imgname)
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, str(ex) if not resjson else resjson["err"])
        await ctx.reply(embed=e, file=img)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="genmeme", description="Generates a meme with top text and bottom text.",
                      aliases=["meme", "memegen", "memer", "makememe"], hidden=True,
                      usage="<image attachment> <top text and bottom text separated with ;>")
    async def genmeme(self, ctx, *, text=""):
        if not ctx.message.attachments:
            return await ctx.reply(embed=funcs.errorEmbed(None, "No attachment detected."))
        if not text:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        if len(text) > 50:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Please make your overall text 50 characters or less."))
        await ctx.send("Generating meme. Please wait...")
        if ";" not in text:
            bottom = ""
            top = text
        else:
            while "; " in text:
                text = text.replace("; ", ";")
            top, bottom = text.split(";", 1)
        await funcs.useImageFunc(ctx, self.makeMeme, top.upper(), bottom.upper())

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="zodiac", description="Converts a date to its zodiac sign.", hidden=True,
                      aliases=["starsign", "horoscope", "zs"], usage="[month] [day]\n\nAlternative usage(s):\n\n- <zodiac sign>")
    async def zodiac(self, ctx, month: str="", day: str=""):
        try:
            if month and not day:
                try:
                    z = funcs.getZodiacInfo(month)
                    e = Embed(title=z[2] + f" :{z[2].casefold().replace('scorpio', 'scorpius')}:")
                    e.add_field(name="Dates", value=f"`{z[1]}`")
                    e.set_image(url=z[0])
                except Exception as ex:
                    e = funcs.errorEmbed("Invalid zodiac!", str(ex))
            else:
                if not month:
                    month = month or datetime.now().month
                if not day:
                    day = day or datetime.now().day
                try:
                    month = funcs.monthNumberToName(int(month))
                except:
                    month = funcs.monthNumberToName(funcs.monthNameToNumber(month))
                monthint = int(funcs.monthNameToNumber(month))
                try:
                    day = int(day)
                except:
                    day = int(day[:-2])
                date = f"{month} {funcs.valueToOrdinal(day)}"
                if day < 1 or day > 31 and monthint in [1, 3, 5, 7, 8, 10, 12] \
                        or day > 30 and monthint in [4, 6, 9, 11] \
                        or day > 29 and monthint == 2:
                    raise Exception
                z = funcs.dateToZodiac(date)
                e = Embed(title=f"{date} Zodiac Sign :{z.casefold().replace('scorpio', 'scorpius')}:")
                e.set_image(url=funcs.getZodiacInfo(z)[0])
                e.set_footer(text=z)
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="chinesezodiac", description="Converts a year to its Chinese zodiac sign.", usage="[year]",
                      aliases=["cz", "zodiacchinese", "year", "yearofthe", "ly", "leap", "leapyear"], hidden=True)
    async def chinesezodiac(self, ctx, year: str=""):
        year = year or datetime.now().year
        try:
            year = int(year)
            e = Embed(
                title=f"{str(year) if year > 1 else str(year * -1 + 1) + ' B.C.'} Chinese Zodiac Sign",
                description=funcs.formatting(funcs.yearToChineseZodiac(year))
            )
            ly = str(funcs.leapYear(year))
            e.add_field(name="Leap Year", value=f"`{ly if ly != 'None' else 'Unknown'}`")
        except Exception:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)


setup = RandomStuff.setup
