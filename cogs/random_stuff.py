import hashlib
from random import choice, randint
from asyncio import sleep

from discord import Embed, Member, File
from discord.ext import commands

from other_utils import funcs


class RandomStuff(commands.Cog, name="Random Stuff"):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.activeSpinners = []

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="dadjoke", description="Sends a random dad joke.", aliases=["dj", "joke"])
    async def dadjoke(self, ctx):
        headers = {"Accept": "application/json"}
        res = await funcs.getRequest("https://icanhazdadjoke.com/", headers=headers)
        await ctx.send(res.json()["joke"])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="trumpthinks", description="What Donald Trump thinks about something or someone.",
                      aliases=["whatdoestrumpthink", "plstrump", "trump", "asktrump", "tt"], usage="<input>")
    async def trumpthinks(self, ctx, *, something:str=""):
        if something == "":
            e = funcs.errorEmbed(None,"Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None,"Please enter 100 characters or less.")
        else:
            res = await funcs.getRequest("https://api.whatdoestrumpthink.com/api/v1/quotes")
            quotes = choice(list(res.json()["messages"]["personalized"]))
            e = Embed(
                title=f"What does Trump think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name="Trump Thinks", value=f"```{something} {quotes}```")
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/659771291858894849/673599147160502282/trumpface.png")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="neothinks", description="What Neo thinks about something or someone.",
                      aliases=["nt", "plsneo", "neosays", "neo", "neot"], usage="<input>")
    async def neothinks(self, ctx, *, something:str=""):
        if something == "":
            e = funcs.errorEmbed(None,"Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None,"Please enter 100 characters or less.")
        else:
            if "neo" in something.casefold():
                quotes = choice([
                    "hold up... Stick it up yours you flawed brony",
                    "wait hang on..."
                ])
            else:
                quotes = choice([
                    " is the Flaw",
                    " is flawed",
                    " ruined the court session",
                    " is the abomination of Zion and the incarnation of the Flaw",
                    " came around and forced Clorox to ban me",
                    " doesn't know what the Flaw is",
                    " is doing the same thing I was banned for. Why are my punishers committing the same crimes?",
                    " must be deported from Zion",
                    " was brainwashed by MLP",
                    " is an absolute injustice and is deliberately opposing the truth and right side",
                    "? LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOL",
                    " delivers flawed messages to children and adults",
                    " is a threat to the goal of Zion, which is to make the uncommon common",
                    " first discovered the Flaw by looking at himself",
                    " is a liar hiding his potential"
                ])
            thumbnail = choice([
                "https://media.discordapp.net/attachments/769899860253736990/772818443585191936/unknown.png",
                "https://media.discordapp.net/attachments/769899860253736990/773133850108624916/2019-02-24.png"
            ])
            e = Embed(
                title=f"What does Neo think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name=f"Neo Thinks", value=f"```{something}{quotes}```")
            e.set_thumbnail(url=thumbnail)
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="audiblethinks", description="What Audible thinks about something or someone.",
                      aliases=["at", "plsaudible", "audiblesays", "audible", "audiblet"], usage="<input>")
    async def audiblethinks(self, ctx, *, something:str=""):
        if something == "":
            e = funcs.errorEmbed(None,"Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None,"Please enter 100 characters or less.")
        else:
            if "audible" in something.casefold():
                quotes = choice([
                    " wait... I'm not gonna roast myself you socialite.",
                    "... Alright, we need to talk."
                ])
            else:
                dq = '"'
                quotes = choice([
                    " is a disgusting vice",
                    " is a socialite",
                    " implies a complete misunderstanding and misinterpretation of my philosophy",
                    " is a true fad",
                    " is a pseudo-gestalt thinker with his head so far lost in the clouds he can't see reality.",
                    " are immersed in their holistic vagueries",
                    " is worse than thinking that cooperation and teamwork somehow magically outperform an individual's" + \
                    f" competence and intellect by {dq}creating{dq} genius with average people's synergy.",
                    " socializes so much that he has mental health concerns.",
                    " did absloutely **** all to resolve the pandemic and did close to nothing to prepare" + \
                    " themselves to it and let alone did they do anything to functionally resolve problems.",
                    "'s utter contradictory mindset is the biggest problem and cruelty that has ever endorsed the human race",
                    " is a cancerous remnant of a scar of weakness we call sociability, a scar that remained from " + \
                    "the days in which individuals needed others to survive, a scar inherited from the bygone days in " + \
                    "which we had smaller brains.",
                    " is the epitome of unadaptability: it is conservative, change resistant and irrational.",
                    " won't accept that smart working and learning is the future",
                    " is not ready to live with the freedom and responsibility of being an individual.",
                    " shouldn't just forget, rationalize, or justify his limitations.",
                    " misses the point that science is both an individual and cooperative effort at different times",
                    " ignores that natural selection favors the culture of empathy, team players, social and altruistic " + \
                    "people, ignoring the fact there are other fundamental traits and other strategies that are selected.",
                    " urges people to self-suppress their own skills in the place of the skills of others.",
                    " shouldn't fire MLP and Disney writers to write its articles",
                    " is like pressing a fork on a plate right next your ear except that you're also being physically " + \
                    "tortured in the process.",
                    " should be against human rights",
                    " teaches you to be a collaborative socialite born to loathe solitude and allow an a** mark to define you.",
                    " should just be transported to their idealized MLP social nirvana and be done with their idiocies.",
                    "? I have to vomit.",
                    "'s content is made for a mass society who obviously likes being told their pro-social and " + \
                    "interdependent properties of mass delusion and incompetence are what makes them strong",
                    " has basic knowledge about humanity, but understands nothing about the human.",
                    " should be sealed in the depths of the Atlantic ocean.",
                    " makes everyone's eyes melt and also causes you to become deaf.",
                    " and collaborative learning are a reactionary movement to the great individual empowerment created" + \
                    " by the availability of 21st century technology. We are using 21st century tech with 20th century markets.",
                    "'s fixation with collaboration, social skills and synergy is getting annoying and increasingly " + \
                    "hard to bear.",
                    " is simply highlighting the paradigm of the majority, as we got obsessed with statistics and averages" + \
                    ", we see them as undeniable evidence that the other way is wrong.",
                    " is a highly abused term in language by making such word apply to as much things as possible, " + \
                    "ending up with an unfalsifiable logical absolute that borders on ontology.",
                    " gives me a thrice damned headache"
                ])
            thumbnail = choice([
                "https://media.discordapp.net/attachments/769899860253736990/773118827293704192/PicsArt_11-03-10.37.49.jpg",
                "https://media.discordapp.net/attachments/766326653538271232/772817547074601000/unknown.png",
                "https://media.discordapp.net/attachments/769899860253736990/773121703009714176/Screenshot_20201103_104927.jpg"
            ])
            e = Embed(
                title=f"What does Audible think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name=f"Audible Thinks", value=f"```{something}{quotes}```")
            e.set_thumbnail(url=thumbnail)
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="roast", description="Roasts a user.", aliases=["insult", "toast"],
                      usage="[@mention]")
    async def roast(self, ctx, member:Member=""):
        if member == "":
            member = ctx.message.author
        res = await funcs.getRequest("https://insult.mattbas.org/api/insult.json")
        await ctx.send(res.json()["insult"].replace("You are", f"{member.display_name} is"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="fidgetspinner", description="Spins a fidget spinner.",
                      aliases=["spin", "spinner", "youspinmerightround"])
    async def fidgetspinner(self, ctx):
        if ctx.author.id in self.activeSpinners:
            await ctx.send(embed=funcs.errorEmbed(None,"Your fidget spinner is still spinning, please wait!"))
            return
        self.activeSpinners.append(ctx.message.author.id)
        try:
            url = choice([
                "https://media.giphy.com/media/cnY70GhrM5nJ6/giphy.gif",
                "https://media.giphy.com/media/cwT3y6UFFseGc/giphy.gif",
                "https://media.giphy.com/media/1Ubrzxvik2puE/giphy.gif",
                "https://files.gamebanana.com/img/ico/sprays/593404c44a588.gif",
                "https://gifimage.net/wp-content/uploads/2017/11/fidget-spinner-gif-transparent-6.gif"
            ])
            file = File(await funcs.getImage(url),"spinner.gif")
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
                      aliases=["love", "lovecalculator"], usage="<@mention> [@mention]")
    async def lovecalc(self, ctx, first:Member=None, second:Member=None):
        if first is None:
            await ctx.send(embed=funcs.errorEmbed(None, "Cannot process empty input."))
            return
        if second is None:
            second = ctx.author
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
                      aliases=["pfp"], usage="[@mention]")
    async def avatar(self, ctx, *, user:Member=None):
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
        await ctx.send(f":8ball: {mention}: `{'Empty input...' if msg=='' else choice(responses)}`")
        
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


def setup(client:commands.Bot):
    client.add_cog(RandomStuff(client))
