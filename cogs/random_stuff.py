from asyncio import sleep, TimeoutError
from random import choice, randint, shuffle
from time import time

from discord import Embed, Member
from discord.ext import commands

from other_utils import funcs
from other_utils.playing_cards import PlayingCards

COIN_EDGE_ODDS = 6001
RN_RANGE = 999999999999


class RandomStuff(commands.Cog, name="Random Stuff"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.activeSpinners = []
        self.phoneWaitingChannels = []
        self.phoneCallChannels = []
        self.personalityTest = funcs.readJson("assets/personality_test.json")
        self.trumpquotes = funcs.readJson("assets/trump_quotes.json")

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="telephone", description="Talk to other users from other chatrooms! " + \
                                                    "This is an experimental feature and might not work 100% of the time.",
                      aliases=["phone", "userphone", "call"])
    async def telephone(self, ctx):
        if ctx.channel in self.phoneWaitingChannels:
            return await ctx.send(":telephone: Cancelling phone call.")
        if ctx.channel in self.phoneCallChannels:
            return await ctx.send(
                embed=funcs.errorEmbed(None, "A phone call is already in progress in this channel.")
            )
        self.phoneWaitingChannels.append(ctx.channel)
        await ctx.send(":telephone_receiver: Waiting for another party to pick up the phone...")
        if len(self.phoneWaitingChannels) == 1:
            sleepTime = 0
            while len(self.phoneWaitingChannels) == 1 and sleepTime < 120:
                if len(self.phoneWaitingChannels) == 1 and sleepTime >= 120:
                    self.phoneWaitingChannels.remove(ctx.channel)
                    return await ctx.send(":telephone: Seems like no one is answering; cancelling phone call.")
                await sleep(0.25)
                sleepTime += 1
        if len(self.phoneWaitingChannels) == 2:
            otherParty = self.phoneWaitingChannels[1 if self.phoneWaitingChannels.index(ctx.channel) == 0 else 0]
            await sleep(1)
            self.phoneWaitingChannels.remove(ctx.channel)
            self.phoneCallChannels.append(ctx.channel)
            resetTime = 0
            startCall = time()
            hangup = False
            await ctx.send(
                ":telephone_receiver: Someone has picked up the phone, say hello! " + \
                "Note that not all messages will be sent. Type `!hangup` to hang up."
            )
            while resetTime < 30 and not hangup and otherParty in self.phoneCallChannels:
                try:
                    msg = await self.client.wait_for(
                        "message", timeout=1, check=lambda m: m.channel == ctx.channel and m.author != self.client.user
                    )
                    if msg.content.casefold() == "!hangup":
                        relay = ":telephone: The other party has hung up the phone."
                        await ctx.send(":telephone: You have hung up the phone.")
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
            _, m, s, _ = funcs.timeDifferenceStr(time(), startCall, noStr=True)
            self.phoneCallChannels.remove(ctx.channel)
            return await ctx.send(f"`Elapsed time: {m}m {s}s`")
        self.phoneWaitingChannels.remove(ctx.channel)
        await ctx.send(":telephone: Seems like no one is answering; cancelling phone call.")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="personalitytest", description="Take a personality test consisting of 88 questions for fun.",
                      aliases=["pt", "mbti", "personality", "personalities", "16p", "16personalities"])
    async def personalitytest(self, ctx):
        await ctx.send("```Note: You are about to take a non-professional personality test with 88 questions. " + \
                       "The test should take around 15 to 30 minutes to complete. To select an answer, input " + \
                       "either 'a', 'b', or 'c'. Try to leave out as many neutral answers as possible. There " + \
                       "are no right or wrong answers.\n\nPlease note that this test does not consider the " + \
                       "cognitive functions and is only designed purely for fun. For more accurate results, " + \
                       "it is recommended that you study the eight cognitive functions and type yourself " + \
                       "based on those functions with the help of a test that makes good use of them.\n\nIf " + \
                       "you want to quit, input 'quit'. Otherwise, input 'test' to start the test.\n\n" + \
                       "Questions provided by EDCampus.```")
        try:
            choice = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=300
            )
        except TimeoutError:
            return await ctx.send(f"`{ctx.author.name} has left the personality test for idling too long.`")
        if choice.content.casefold() != "test":
            return await ctx.send(f"`{ctx.author.name} has left the personality test.`")
        res = list(self.personalityTest["questions"])
        e, i, s, n, t, f, j, p = 0, 0, 0, 0, 0, 0, 0, 0
        ei = ["1.", "5.", "9.", "13", "17", "21", "25", "29", "33", "37", "41",
              "45", "49", "53", "57", "61", "65", "69", "73", "77", "81", "85"]
        sn = ["2.", "6.", "10", "14", "18", "22", "26", "30", "34", "38", "42",
              "46", "50", "54", "58", "62", "66", "70", "74", "78", "82", "86"]
        tf = ["3.", "7.", "11", "15", "19", "23", "27", "31", "35", "39", "43",
              "47", "51", "55", "59", "63", "67", "71", "75", "79", "83", "87"]
        choices = [0, 1]
        questionNumbers = [i for i in range(88)]
        questionCount, choiceCount = 1, 1
        choice = None
        shuffle(questionNumbers)
        for x in questionNumbers:
            userInput = ""
            title = res[x]["title"]
            question = f"{title.split('. ')[1]}\n\n"
            shuffle(choices)
            for choice in choices:
                sub = "a) " if choiceCount == 1 else "b) "
                choiceCount = 2 if choiceCount == 1 else 1
                question += sub + res[x]["selections"][choice] + "\n"
            await ctx.send(f"```Question {questionCount} of 88 for {ctx.author.name}:\n\n{question[:-1]}\n" + \
                           "c) none of the above/neutral.```")
            while userInput.casefold() != "a" and userInput.casefold() != "b" \
                    and userInput.casefold() != "c" and userInput.casefold() != "quit" \
                    and userInput.casefold() != "exit" and userInput.casefold() != "leave":
                try:
                    answer = await self.client.wait_for(
                        "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=900
                    )
                except TimeoutError:
                    return await ctx.send(f"`{ctx.author.name} has left the personality test for idling too long.`")
                userInput = answer.content
                if userInput.casefold() != "a" and userInput.casefold() != "b" \
                        and userInput.casefold() != "c" and userInput.casefold() != "quit" \
                        and userInput.casefold() != "exit" and userInput.casefold() != "leave":
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))
            if userInput.casefold() == "quit" or userInput.casefold() == "exit" \
                    or userInput.casefold() == "leave":
                return await ctx.send(f"`{ctx.author.name} has left the personality test.`")
            if userInput.casefold() == "a" and choice == 1 \
                    or userInput.casefold() == "b" and choice == 0:
                if any(res[x]["title"].startswith(y) for y in ei):
                    e += 1
                elif any(res[x]["title"].startswith(y) for y in sn):
                    s += 1
                elif any(res[x]["title"].startswith(y) for y in tf):
                    t += 1
                else:
                    j += 1
            elif userInput.casefold() == "b" and choice == 1 \
                    or userInput.casefold() == "a" and choice == 0:
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
        snr = "Sensing - " if s > n else "Sensing/Intuitive? - " if s == n else "Intuitive - "
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
        await ctx.send(f"```== {ctx.author.name}'s Personality Test Result " + \
                       f"==\n\n{eir}{eis}\n{snr}{sns}\n{tfr}{tfs}\n{jpr}{jps}\n\nYour four-letter " + \
                       f"personality code is '{eic}{snc}{tfc}{jpc}'.\n\nOnce again, this test is " + \
                       "only for fun and should not be treated like a professional assessment. " + \
                       "Thank you for trying out this out!```")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="dadjoke", description="Sends a random dad joke.", aliases=["dj", "joke"])
    async def dadjoke(self, ctx):
        headers = {"Accept": "application/json"}
        res = await funcs.getRequest("https://icanhazdadjoke.com/", headers=headers)
        await ctx.send(res.json()["joke"])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="dog", description="Sends a random dog image.")
    async def dog(self, ctx):
        res = await funcs.getRequest("https://dog.ceo/api/breeds/image/random")
        await funcs.sendImage(ctx, res.json()["message"])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cat", description="Sends a random cat image.")
    async def cat(self, ctx):
        res = await funcs.getRequest("https://api.thecatapi.com/v1/images/search")
        image = res.json()[0]["url"]
        await funcs.sendImage(ctx, image, name=image.split("thecatapi.com/images/")[1])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="trumpthinks", description="What Donald Trump thinks about something or someone.",
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
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="roast", description="Roasts a user.", aliases=["insult", "toast"],
                      usage="[@mention]")
    async def roast(self, ctx, member: Member=None):
        member = member or ctx.message.author
        res = await funcs.getRequest("https://insult.mattbas.org/api/insult.json")
        await ctx.send(res.json()["insult"].replace("You are", f"{member.display_name} is"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="fidgetspinner", description="Spins a fidget spinner.",
                      aliases=["spin", "spinner", "youspinmerightround"])
    async def fidgetspinner(self, ctx):
        if ctx.author.id in self.activeSpinners:
            return await ctx.send(embed=funcs.errorEmbed(None, "Your fidget spinner is still spinning, please wait!"))
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
                                  message=f"<:fidgetspinner:675314386784485376> **{ctx.author.name} has spun a fidget"+ \
                                          " spinner. Let's see how long it lasts...** <:fidgetspinner:675314386784485376>")
            randomSeconds = randint(5, 180)
            await sleep(randomSeconds)
            await ctx.send(
                f"<:fidgetspinner:675314386784485376> **{ctx.message.author.name}'s fidget spinner has just stopped " + \
                f"spinning; it lasted {randomSeconds} seconds!** <:fidgetspinner:675314386784485376>"
            )
            self.activeSpinners.remove(ctx.message.author.id)
        except:
            await ctx.send(embed=funcs.errorEmbed(None, "An error occurred. Please try again later."))
            try:
                self.activeSpinners.remove(ctx.message.author.id)
            except ValueError:
                return

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="lovecalc", description="Calculates the love percentage between two users.",
                      aliases=["love", "lovecalculator", "lc"], usage="<@mention> [@mention]")
    async def lovecalc(self, ctx, first: Member=None, second: Member=None):
        if first is None:
            return await ctx.send(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        second = second or ctx.author
        try:
            newlist = [first.id, second.id]
            sentence = ""
            for i in sorted(newlist):
                sentence += str(i) + " loves "
            sentence = sentence[:-7]
            sentence = sentence.replace(" ", "").lower()
            intermediate = ""
            while len(sentence):
                intermediate += str(sentence.count(sentence[0]))
                sentence = sentence.replace(sentence[0], "")
            while int(intermediate) > 100:
                tmp = ""
                for i in range(0, int(len(intermediate) / 2)):
                    tmp += str(int(intermediate[i]) + int(intermediate[(i+1) * -1]))
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
            await ctx.send("The love percentage between " + \
                           f"**{first.name}** and **{second.name}** is **{intermediate}%{emoji}")
        except Exception:
            await ctx.send(embed=funcs.errorEmbed(None, "An error occurred. Invalid user?"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="avatar", description="Shows the avatar of a user.",
                      aliases=["pfp", "icon"], usage="[@mention]")
    async def avatar(self, ctx, *, user: Member=None):
        user = user or ctx.author
        ext = "gif" if user.is_avatar_animated() else "png"
        await funcs.sendImage(ctx, str(user.avatar_url_as(format=ext if ext != "gif" else None)), name=f"avatar.{ext}")

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="8ball", description="Ask 8ball a question.",
                      aliases=["8b", "8"], usage="<input>")
    async def eightball(self, ctx, *, msg=""):
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
        await ctx.send(f":8ball: {mention}: `{'Empty input...' if msg == '' else choice(responses)}`")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="coin", description="Flips coins.", usage="[amount up to 100]",
                      aliases=["coins", "flip", "fc", "flipcoin", "coinflip",
                               "flipcoins", "tosscoins", "cointoss", "tosscoin", "toss"])
    async def coin(self, ctx, amount="1"):
        try:
            amount = int(amount)
        except ValueError:
            amount = 1
        if not 0 < amount < 101:
            return await ctx.send(embed=funcs.errorEmbed(None, "Amount must be between 1 and 100."))
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
            await ctx.send(embed=e)
        else:
            result = ""
            for i in range(1, 4):
                cointype = 'Heads' if i == 1 else 'Tails' if i == 2 else 'Edge'
                result += "\n{}{}: {} time{}".format(
                    cointype, (" (1 in {:,} chance)".format(COIN_EDGE_ODDS) if i == 3 else ""),
                    total[cointype], "s" if total[cointype] > 1 else ""
                ) if total[cointype] else ""
            await ctx.send(f"```{', '.join(coin for coin in coins)}\n{result}\n\nRequested by: {ctx.author}```")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="die", description="Rolls dice.", usage="[amount up to 100]",
                      aliases=["dice", "roll", "rd", "rolldice", "rolldie", "diceroll", "dieroll"])
    async def die(self, ctx, amount="1"):
        try:
            amount = int(amount)
        except ValueError:
            amount = 1
        if not 0 < amount < 101:
            return await ctx.send(embed=funcs.errorEmbed(None, "Amount must be between 1 and 100."))
        dice = []
        total = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0}
        for _ in range(amount):
            randomdice = randint(1, 6)
            dice.append(randomdice)
            total[randomdice] += 1
        if amount == 1:
            e = Embed(title=dice[0], description=f"Requested by: {ctx.author.mention}")
            e.set_image(url=f"https://rolladie.net/images/dice/dice{dice[0]}.jpg")
            await ctx.send(embed=e)
        else:
            result = ""
            for i in range(1, 7):
                result += f"\n{i}: {total[i]} time{'s' if total[i] > 1 else ''}" if total[i] else ""
            dicesum = sum(dice)
            possiblepts = amount * 6
            await ctx.send(
                f"```{', '.join(str(die) for die in dice)}\n{result}\n\nTotal value: " + \
                f"{dicesum} out of {possiblepts} ({round(dicesum / possiblepts * 100, 3)}%)\n\nRequested by: {ctx.author}```"
            )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="card", description="Deals cards.", usage="[amount up to 52]",
                      aliases=["rc", "cards", "deal", "randomcard", "randomcards", "dc", "dealcard", "dealcards"])
    async def card(self, ctx, amount="1"):
        try:
            amount = int(amount)
        except ValueError:
            amount = 1
        if not 0 < amount < 53:
            return await ctx.send(embed=funcs.errorEmbed(None, "Amount must be between 1 and 52."))
        pc = PlayingCards()
        cards = pc.randomCard(amount)
        if amount == 1:
            e = Embed(title=pc.returnCardName(cards[0]), description=f"Requested by: {ctx.author.mention}")
            e.set_image(url=pc.returnCardImage(cards[0]))
            await ctx.send(embed=e)
        else:
            await ctx.send(
                "```{}\n\nRequested by: {}```".format(
                    "\n".join(f"{card} | {pc.returnCardName(card)}" for card in cards), ctx.author
                )
            )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="number", usage="[range up to {:,}] [starting point (0 OR 1)]".format(RN_RANGE),
                      aliases=["rn", "numbers", "randomnumber", "rng"], description="Generates a random number.")
    async def number(self, ctx, rnrange: str=str(RN_RANGE), start: str= "1"):
        try:
            rnrange = int(rnrange)
            if not 0 < rnrange < (RN_RANGE + 1):
                rnrange = RN_RANGE
        except ValueError:
            rnrange = RN_RANGE
        try:
            start = 1 if int(start) > 0 else 0
        except ValueError:
            start = 1
        await ctx.send("```{:,} (Range: {:,} to {:,})\n\nRequested by: {}```".format(
            randint(start, rnrange), start, rnrange, ctx.author
        ))


def setup(client: commands.Bot):
    client.add_cog(RandomStuff(client))
