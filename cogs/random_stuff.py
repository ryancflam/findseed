from random import choice, randint
from asyncio import sleep

import discord
from discord.ext import commands

import funcs


class RandomStuff(commands.Cog, name="Random Stuff"):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.activeSpinners = []

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="diu", description="Diu.", aliases=["dllm"])
    async def diu(self, ctx):
        await ctx.channel.send(
            "我唔撚柒鳩屌你個冚家剷含撚笨柒個老母個生滋甩毛嘅爛臭化花柳白濁梅毒" + \
            "性冷感閪都唔撚柒得陰陽面邊大邊細豬閪燉糯米雙番閪遮面長短腳谷精上腦" + \
            "陽萎笨柒周頭發炎陰蝨周圍跳白竇臭滴蟲入鳩祖宗十八代食屎撈屄周揈揈白痴戇鳩閪"
        )

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="mlp", description="The worst thing ever in existence.")
    async def mlp(self, ctx):
        if randint(0, 1) == 0:
            await ctx.channel.send(
                "That indefinably fallacious, thrice damned, abhorrent primitive, " + \
                "superbly and imperfectly obnoxious and ironically audience " + \
                "biased, stupid idiotic medieval mental torture machine"
            )
        else:
            url = "https://media.discordapp.net/attachments/769899860253736990/772731790791278602/unknown.png"
            file = discord.File(await funcs.getImage(url), "mlp.png")
            await ctx.channel.send(file=file)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="dadjoke", description="Sends a random dad joke.", aliases=["dj", "joke"])
    async def dadjoke(self, ctx):
        headers = {"Accept": "application/json"}
        res = await funcs.getRequest("https://icanhazdadjoke.com/", headers=headers)
        await ctx.channel.send(res.json()["joke"])

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="trumpthinks", description="What Donald Trump thinks about something or someone.",
                      aliases=["whatdoestrumpthink", "plstrump", "trump", "asktrump", "tt"], usage="<input>")
    async def trumpthinks(self, ctx, *, something:str=""):
        if something == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None, "Please enter 100 characters or less.")
        else:
            res = await funcs.getRequest("https://api.whatdoestrumpthink.com/api/v1/quotes")
            quotes = choice(list(res.json()["messages"]["personalized"]))
            e = discord.Embed(
                title=f"What does Trump think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name="Trump Thinks", value=f"```{something} {quotes}```")
            e.set_thumbnail(url="https://cdn.discordapp.com/attachments/659771291858894849/673599147160502282/trumpface.png")
        await ctx.channel.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="neothinks", description="What Neo thinks about something or someone.",
                      aliases=["nt", "plsneo", "neosays", "neo", "neot"], usage="<input>")
    async def neothinks(self, ctx, *, something:str=""):
        if something == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None, "Please enter 100 characters or less.")
        else:
            if "neo" in something.casefold():
                quotes = choice([
                    "hold up... Stick it up yours you flawed brony"
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
            e = discord.Embed(
                title=f"What does Neo think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name=f"Neo Thinks", value=f"```{something}{quotes}```")
            e.set_thumbnail(url=thumbnail)
        await ctx.channel.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="audiblethinks", description="What Audible thinks about something or someone.",
                      aliases=["at", "plsaudible", "audiblesays", "audible", "audiblet"], usage="<input>")
    async def audiblethinks(self, ctx, *, something:str=""):
        if something == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None, "Please enter 100 characters or less.")
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
                    " socializes too much that he has mental health concerns.",
                    " did absloutely **** all to resolve the pandemic and did close to nothing to prepare" + \
                    " themselves to it and let alone did they do anything to functionally resolve problems.",
                    "'s utter contradictory mindset is the biggest problem and cruelty that has ever endorsed the human race",
                    " is a cancerous remnant of a scar of weakness we call sociability, a scar that remained from " + \
                    "the days in which individuals needed others to survive, a scar inherited from the bygone days in " + \
                    "which we had smaller brains.",
                    " is the epitome of unadaptability: it is conservative, change resistant and irrational.",
                    " won't accept that smart working and learning is the future",
                    " is not ready to live with the freedom and responsibility of being an individual.",
                    " shouldn't just forget, rationalize or justify his limitations.",
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
            e = discord.Embed(
                title=f"What does Audible think of {something}?",
                description=f"Requested by: {ctx.message.author.mention}"
            )
            e.add_field(name=f"Audible Thinks", value=f"```{something}{quotes}```")
            e.set_thumbnail(url=thumbnail)
        await ctx.channel.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="roast", description="Roasts a user.", aliases=["insult", "toast"],
                      usage="[@mention]")
    async def roast(self, ctx, member:discord.Member=""):
        if member == "":
            member = ctx.message.author
        res = await funcs.getRequest("https://insult.mattbas.org/api/insult.json")
        await ctx.channel.send(res.json()["insult"].replace("You are", f"{member.display_name} is"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="neomeme", description="Neo.")
    async def neo(self, ctx):
        url = choice([
            "https://media.discordapp.net/attachments/362589047018749955/759806426230161466/unknown.png",
            "https://media.discordapp.net/attachments/362589047018749955/764478615164420106/unknown.png",
            "https://media.discordapp.net/attachments/362589047018749955/761920398102364170/unknown.png",
            "https://media.discordapp.net/attachments/769899860253736990/772088052407074836/neo_logic_meme.jpg"
        ])
        file = discord.File(await funcs.getImage(url), "neo.png")
        await ctx.channel.send(file=file)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="audiblememe", description="Audible Individualism intensifies.")
    async def audible(self, ctx):
        url = choice([
            "https://media.discordapp.net/attachments/769899860253736990/772099297189560340/unknown.png",
            "https://media.discordapp.net/attachments/769899860253736990/772100077111738408/PicsArt_10-21-03.07.47.jpg",
            "https://media.discordapp.net/attachments/769899860253736990/772101368412373012/PicsArt_10-31-03.14.46.png",
        ])
        file = discord.File(await funcs.getImage(url), "audible.png")
        await ctx.channel.send(file=file)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="fidgetspinner", description="Spins a fidget spinner.",
                      aliases=["spin", "spinner", "youspinmerightround"])
    async def fidgetspinner(self, ctx):
        if ctx.author.id in self.activeSpinners:
            await ctx.channel.send(embed=funcs.errorEmbed(None, "Your fidget spinner is still spinning, please wait!"))
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
            file = discord.File(await funcs.getImage(url), "spinner.gif")
            await ctx.channel.send(
                f"<:fidgetspinner:675314386784485376> **{ctx.message.author.name} has spun a fidget spinner. " + \
                "Let's see how long it lasts...** <:fidgetspinner:675314386784485376>", file=file
            )
            randomSeconds = randint(5, 180)
            await sleep(randomSeconds)
            await ctx.channel.send(
                f"<:fidgetspinner:675314386784485376> **{ctx.message.author.name}'s fidget spinner has just stopped " + \
                f"spinning; it lasted {randomSeconds} seconds!** <:fidgetspinner:675314386784485376>"
            )
            self.activeSpinners.remove(ctx.message.author.id)
        except:
            await ctx.channel.send(embed=funcs.errorEmbed(None, "An error occurred. Please try again later."))
            try:
                self.activeSpinners.remove(ctx.message.author.id)
            except ValueError:
                return


def setup(client):
    client.add_cog(RandomStuff(client))
