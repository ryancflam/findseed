import hashlib
from json import load
from time import time
from datetime import datetime
from asyncpraw import Reddit
from asyncio import sleep, TimeoutError
from random import choice, randint, shuffle

from discord import Embed, Member, File, channel
from discord.ext import commands

import config
from other_utils import funcs


class RandomStuff(commands.Cog, name="Random Stuff"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.activeSpinners = []
        self.phoneWaitingChannels = []
        self.phoneCallChannels = []
        self.personalityTest = load(open(f"{funcs.getPath()}/assets/personality_test.json", "r", encoding="utf8"))
        self.reddit = Reddit(client_id=config.redditClientID,
                             client_secret=config.redditClientSecret,
                             user_agent="*")

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
                      aliases=["pt", "mbti", "personality"])
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
        res2 = File(await funcs.getImage(res.json()["message"]), "dog.jpg")
        await ctx.send(file=res2)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="cat", description="Sends a random cat image.")
    async def cat(self, ctx):
        res = await funcs.getRequest("https://api.thecatapi.com/v1/images/search")
        image = res.json()[0]["url"]
        res2 = File(await funcs.getImage(image), image.split("thecatapi.com/images/")[1])
        await ctx.send(file=res2)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="trumpthinks", description="What Donald Trump thinks about something or someone.",
                      aliases=["whatdoestrumpthink", "plstrump", "trump", "asktrump", "tt", "tq"], usage="<input>")
    async def trumpthinks(self, ctx, *, something: str=""):
        if something == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None, "Please enter 100 characters or less.")
        else:
            with open(f"{funcs.getPath()}/assets/trump_quotes.json", "r", encoding="utf-8") as f:
                data = load(f)
            f.close()
            quotes = choice(data["messages"]["list"])
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
            file = File(await funcs.getImage(url), "spinner.gif")
            await ctx.send(
                f"<:fidgetspinner:675314386784485376> **{ctx.message.author.name} has spun a fidget spinner. " + \
                "Let's see how long it lasts...** <:fidgetspinner:675314386784485376>", file=file
            )
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
        url = user.avatar_url_as(format=ext if ext != "gif" else None)
        file = File(await funcs.getImage(str(url)), f"avatar.{ext}")
        await ctx.send(file=file)

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

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="hash", description="Generates a hash from an input using an algorithm.",
                      aliases=["hashing", "hashbrown"], usage="<algorithm> [input]")
    async def hash(self, ctx, algo=None, *, msg=""):
        algorithms = [
            "md5", "blake2b", "blake2s", "sha1", "sha224", "sha256", "sha384", "sha512", "sha", "md"
        ]
        if not algo:
            e = funcs.errorEmbed(None, "Please select a hashing algorithm.")
        else:
            algo = algo.casefold().replace("-", "").replace("_", "").strip()
            if algo not in algorithms:
                e = funcs.errorEmbed(
                    "Invalid algorithm!",
                    "Valid options:\n\n`MD5`, `BLAKE2b`, `BLAKE2s`, " + \
                    "`SHA1`, `SHA224`, `SHA256`, `SHA384`, `SHA512`"
                )
            else:
                if algo.startswith("md"):
                    algo = "MD5"
                    output = str(hashlib.md5(msg.encode("utf-8")).hexdigest())
                elif algo == "blake2b":
                    algo = "BLAKE2b"
                    output = str(hashlib.blake2b(msg.encode("utf-8")).hexdigest())
                elif algo == "blake2s":
                    algo = "BLAKE2s"
                    output = str(hashlib.blake2s(msg.encode("utf-8")).hexdigest())
                elif algo == "sha1" or algo == "sha":
                    algo = "SHA1"
                    output = str(hashlib.sha1(msg.encode("utf-8")).hexdigest())
                elif algo == "sha224":
                    algo = "SHA224"
                    output = str(hashlib.sha224(msg.encode("utf-8")).hexdigest())
                elif algo == "sha256":
                    algo = "SHA256"
                    output = str(hashlib.sha256(msg.encode("utf-8")).hexdigest())
                elif algo == "sha384":
                    algo = "SHA384"
                    output = str(hashlib.sha384(msg.encode("utf-8")).hexdigest())
                else:
                    algo = "SHA512"
                    output = str(hashlib.sha512(msg.encode("utf-8")).hexdigest())
                e = Embed(title=algo, description=funcs.formatting(output))
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="urban", description="Looks up a term on Urban Dictionary.",
                      aliases=["ud", "urbandictionary"], usage="<term>")
    async def urban(self, ctx, *, term=""):
        if term == "":
            e = funcs.errorEmbed(None, "Empty input.")
        else:
            res = await funcs.getRequest(f"http://api.urbandictionary.com/v0/define", params={"term": term})
            data = res.json()
            terms = data["list"]
            if len(terms) == 0:
                e = funcs.errorEmbed(None, "Unknown term.")
            else:
                thumbnail = "https://cdn.discordapp.com/attachments/659771291858894849/" + \
                            "669142387330777115/urban-dictionary-android.png"
                example = terms[0]["example"].replace("[", "").replace("]", "")
                definition = terms[0]["definition"].replace("[", "").replace("]", "")
                permalink = terms[0]["permalink"]
                word = terms[0]["word"].replace("*", "\*").replace("_", "\_")
                e = Embed(title=word, description=permalink)
                e.add_field(name="Definition", value=funcs.formatting(definition, limit=1000))
                e.set_thumbnail(url=thumbnail)
                if example:
                    e.add_field(name="Example(s)", value=funcs.formatting(example, limit=1000))
                e.set_footer(
                    text=f"Submitted by {terms[0]['author']} | Approval rate: " + \
                         f"{round(terms[0]['thumbs_up'] / (terms[0]['thumbs_up'] + terms[0]['thumbs_down']) * 100, 2)}" + \
                         f"% ({terms[0]['thumbs_up']} 👍 - {terms[0]['thumbs_down']} 👎)"
                )
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="reddit", description="Looks up a community or user on Reddit.",
                      aliases=["subreddit", "r", "redditor"], usage="<r/subreddit OR u/redditor>")
    async def reddit(self, ctx, *, inp=""):
        inp = inp.replace(" ", "/")
        while inp.startswith("/"):
            inp = inp[1:]
        while inp.endswith("/"):
            inp = inp[:-1]
        try:
            if inp.casefold().startswith("r") and "/" in inp:
                subreddit = await self.reddit.subreddit(inp.split("/")[-1], fetch=True)
                if subreddit.over18 and not isinstance(ctx.channel, channel.DMChannel) \
                        and not ctx.channel.is_nsfw():
                    e = funcs.errorEmbed("NSFW/Over 18!", "Please view this community in an NSFW channel.")
                else:
                    tags = [
                        i for i in [
                            "Link Flairs" if subreddit.can_assign_link_flair else 0,
                            "User Flairs" if subreddit.can_assign_user_flair else 0,
                            "Spoilers Enabled" if subreddit.spoilers_enabled else 0,
                            "NSFW" if subreddit.over18 else 0
                        ] if i
                    ]
                    e = Embed(title="r/" + subreddit.display_name,
                              description=f"https://www.reddit.com/r/{subreddit.display_name}" + " ([Old Reddit](" + \
                                          f"https://old.reddit.com/r/{subreddit.display_name}))")
                    if tags:
                        e.add_field(name="Tags", value=", ".join(f"`{i}`" for i in tags))
                    e.set_footer(text=subreddit.public_description)
                    e.add_field(name="Created (UTC)", value=f"`{datetime.fromtimestamp(subreddit.created_utc)}`")
                    e.add_field(name="Subscribers", value="`{:,}`".format(subreddit.subscribers))
                    async for submission in subreddit.new(limit=1):
                        sauthor = submission.author or "[deleted]"
                        if sauthor != "[deleted]":
                            sauthor = sauthor.name
                        e.add_field(
                            name="Latest Post ({:,} point{}; from u/{})".format(
                                submission.score, "" if submission.score == 1 else "s", sauthor
                            ),
                            value=f"https://www.reddit.com{submission.permalink}" + " ([Old Reddit](" + \
                                  f"https://old.reddit.com{submission.permalink}))",
                            inline=False
                        )
            elif inp.casefold().startswith("u") and "/" in inp:
                redditor = await self.reddit.redditor(inp.split("/")[-1], fetch=True)
                try:
                    suspended = redditor.is_suspended
                    tags = ["Suspended"]
                    nickname = ""
                except:
                    suspended = False
                    tags = [
                        i for i in [
                            "Verified" if redditor.has_verified_email else 0,
                            "Reddit Employee" if redditor.is_employee else 0,
                            "Moderator" if redditor.is_mod else 0,
                            "Gold" if redditor.is_gold else 0,
                            "NSFW" if redditor.subreddit["over_18"] else 0
                        ] if i
                    ]
                    nickname = redditor.subreddit["title"]
                if "NSFW" in tags and not isinstance(ctx.channel, channel.DMChannel) \
                        and not ctx.channel.is_nsfw():
                    e = funcs.errorEmbed("NSFW/Over 18!", "Please view this profile in an NSFW channel.")
                else:
                    e = Embed(title="u/" + redditor.name + (f" ({nickname})" if nickname else ""),
                              description=f"https://www.reddit.com/user/{redditor.name}" + " ([Old Reddit](" + \
                                          f"https://old.reddit.com/user/{redditor.name}))")
                    if tags:
                        e.add_field(name="Tags", value=", ".join(f"`{i}`" for i in tags))
                    if not suspended:
                        lkarma = redditor.link_karma
                        ckarma = redditor.comment_karma
                        trophies = await redditor.trophies()
                        e.set_thumbnail(url=redditor.icon_img)
                        e.add_field(name="Join Date (UTC)", value=f"`{datetime.fromtimestamp(redditor.created_utc)}`")
                        e.add_field(name="Total Karma", value="`{:,}`".format(lkarma + ckarma))
                        e.add_field(name="Post Karma", value="`{:,}`".format(lkarma))
                        e.add_field(name="Comment Karma", value="`{:,}`".format(ckarma))
                        if trophies:
                            e.add_field(
                                name="Trophies ({:,})".format(len(trophies)),
                                value=", ".join(f"`{trophy.name}`" for trophy in trophies[:50])
                                      + ("..." if len(trophies) > 50 else ""),
                                inline=False
                            )
                        async for submission in redditor.submissions.new(limit=1):
                            e.add_field(
                                name=f"Latest Post (on r/{submission.subreddit.display_name}; " + \
                                     f"{'{:,}'.format(submission.score)} point{'' if submission.score == 1 else 's'})",
                                value=f"https://www.reddit.com{submission.permalink}" + " ([Old Reddit](" + \
                                      f"https://old.reddit.com{submission.permalink}))",
                                inline=False
                            )
                        async for comment in redditor.comments.new(limit=1):
                            e.add_field(
                                name=f"Latest Comment (on r/{comment.subreddit.display_name}; " + \
                                     f"{'{:,}'.format(comment.score)} point{'' if comment.score == 1 else 's'})",
                                value=funcs.formatting(comment.body, limit=1000),
                                inline=False
                            )
                        e.set_footer(text=redditor.subreddit["public_description"])
                        e.set_image(url=redditor.subreddit["banner_img"])
            else:
                e = funcs.errorEmbed("Invalid input!", 'Please use `r/"subreddit name"` or `u/"username"`.')
        except Exception:
            e = funcs.errorEmbed(None, "Invalid search.")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(RandomStuff(client))
