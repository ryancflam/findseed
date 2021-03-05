from random import randint, choice

from discord.ext import commands
from discord import Embed, File, Colour

from other_utils import funcs


class EasterEggs(commands.Cog, name="Easter Eggs", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="neothinks", description="What Neo thinks about something or someone.",
                      aliases=["nt", "plsneo", "neosays", "neo", "neot"], usage="<input>")
    async def neothinks(self, ctx, *, something: str=""):
        if something == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        elif len(something) > 100:
            e = funcs.errorEmbed(None, "Please enter 100 characters or less.")
        else:
            if "neo" in something.casefold():
                quotes = choice([
                    " hold up... Stick it up yours you flawed brony",
                    " wait hang on..."
                ])
            else:
                quotes = choice([
                    " is the Flaw",
                    " is still making UMS songs about me, with of course a MLP reference",
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
    async def audiblethinks(self, ctx, *, something: str=""):
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
                    " shouldn't hire MLP and Disney writers to write its articles",
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

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="diu", description="Diu.", aliases=["dllm"])
    async def diu(self, ctx):
        await ctx.send(
            "我唔撚柒鳩屌你個冚家剷含撚笨柒個老母個生滋甩毛嘅爛臭化花柳白濁梅毒" + \
            "性冷感閪都唔撚柒得陰陽面邊大邊細豬閪燉糯米雙番閪遮面長短腳谷精上腦" + \
            "陽萎笨柒周頭發炎陰蝨周圍跳白竇臭滴蟲入鳩祖宗十八代食屎撈屄周揈揈白痴戇鳩閪"
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="mlp", description="The worst thing ever in existence.")
    async def mlp(self, ctx):
        if randint(0, 1) == 0:
            await ctx.send(
                "That indefinably fallacious, thrice damned, abhorrent primitive, " + \
                "superbly and imperfectly obnoxious and ironically audience " + \
                "biased, stupid idiotic medieval mental torture machine"
            )
        else:
            url = "https://media.discordapp.net/attachments/769899860253736990/772731790791278602/unknown.png"
            file = File(await funcs.getImage(url), "mlp.png")
            await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="zion1", description="May the Star be with you all.")
    async def zionone(self, ctx):
        await ctx.send(
            embed=Embed(
                description="[May the Star be with you all.](https://www.youtube.com/watch?v=en5QMOro6jA)"
            )
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="zion2", description="May the Star be with you all.")
    async def ziontwo(self, ctx):
        await ctx.send(
            embed=Embed(
                description="[May the Star be with you all.](https://www.youtube.com/watch?v=g2BLwhCtxjA)"
            )
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="zion3", description="May the Star be with you all.")
    async def zionthree(self, ctx):
        await ctx.send(
            embed=Embed(
                description="[May the Star be with you all.](https://www.youtube.com/watch?v=Z0AjAkCK8eI)"
            )
        )

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="lolwall", description="LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOL.")
    async def lolwall(self, ctx):
        await ctx.send("LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO" + \
                               "OOOOOOOOOOOOOOOOOOOL")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="lolwave", description="LOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooL.")
    async def lolwave(self, ctx):
        await ctx.send("LOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOo" + \
                               "oooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooO" + \
                               "OOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooo" + \
                               "oooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOO" + \
                               "OooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooo" + \
                               "oOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOo" + \
                               "oooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooO" + \
                               "OOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooo" + \
                               "oooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOO" + \
                               "OooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooo" + \
                               "oOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOo" + \
                               "oooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooO" + \
                               "OOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooo" + \
                               "oooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOO" + \
                               "OooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooo" + \
                               "oOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOooooooOOOOL")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="neomeme", description="Neo.")
    async def neo(self, ctx):
        url = choice([
            "https://media.discordapp.net/attachments/362589047018749955/759806426230161466/unknown.png",
            "https://media.discordapp.net/attachments/362589047018749955/764478615164420106/unknown.png",
            "https://media.discordapp.net/attachments/362589047018749955/761920398102364170/unknown.png",
            "https://media.discordapp.net/attachments/769899860253736990/772088052407074836/neo_logic_meme.jpg"
        ])
        file = File(await funcs.getImage(url), "neo.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="audiblememe", description="Audible Individualism intensifies.")
    async def audible(self, ctx):
        url = choice([
            "https://media.discordapp.net/attachments/769899860253736990/772099297189560340/unknown.png",
            "https://media.discordapp.net/attachments/769899860253736990/772100077111738408/PicsArt_10-21-03.07.47.jpg",
            "https://media.discordapp.net/attachments/769899860253736990/772101368412373012/PicsArt_10-31-03.14.46.png",
        ])
        file = File(await funcs.getImage(url), "audible.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="akiangry", description="Akinator is angry.")
    async def akiangry(self, ctx):
        url = "https://media.discordapp.net/attachments/769899860253736990/775032980787691550/2017-12-12_12.png"
        file = File(await funcs.getImage(url), "akiangry.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="handkerchief", description="Need a handkerchief?")
    async def handkerchief(self, ctx):
        url = "https://media.discordapp.net/attachments/771404776410972161/776318693969756160/al_doctor.jpg"
        file = File(await funcs.getImage(url), "handkerchief.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="you", description="You.")
    async def you(self, ctx):
        await ctx.send("https://tenor.com/view/dog-eating-food-cheese-dog-eating-gif-12285621")

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name=">(", description="Just >(.", aliases=[">c"])
    async def angry(self, ctx):
        url = "https://media.discordapp.net/attachments/771404776410972161/776320128953745428/angry.png"
        file = File(await funcs.getImage(url), ">(.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="marioannoyed", description="Server owner be like.")
    async def marioannoyed(self, ctx):
        url = "https://media.discordapp.net/attachments/780837667632971786/783004827322941480/image0.png"
        file = File(await funcs.getImage(url), "marioannoyed.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="xmurry", description="...")
    async def xmurry(self, ctx):
        url = "https://media.discordapp.net/attachments/780837667632971786/783005790742249472/2018-04-19_5.png"
        file = File(await funcs.getImage(url), "xmurry.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="oo", description="OO.")
    async def oo(self, ctx):
        url = "https://media.discordapp.net/attachments/780837667632971786/783006065028759552/2018-04-24.png"
        file = File(await funcs.getImage(url), "oo.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="marionietzsche", description="Moustache.")
    async def marionietzsche(self, ctx):
        url = "https://media.discordapp.net/attachments/780837667632971786/783006357509898260/2018-01-03_13.png"
        file = File(await funcs.getImage(url), "marionietzsche.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="mariowatchingmlp", description="He does not seem to like it...")
    async def mariowatchingmlp(self, ctx):
        url = "https://media.discordapp.net/attachments/780837667632971786/783006422844702720/2018-01-03_14.png"
        file = File(await funcs.getImage(url), "mariowatchingmlp.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="owchild", description="Man, that must hurt...")
    async def owchild(self, ctx):
        url = "https://media.discordapp.net/attachments/780837667632971786/783006687623643226/2019-06-22.png"
        file = File(await funcs.getImage(url), "owchild.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="dogecoinbuyers", description="Dogecoin buyers.")
    async def dogecoinbuyers(self, ctx):
        url = "https://media.discordapp.net/attachments/777818814829690884/813483257860849664/PicsArt_02-14-07.56.48.jpg"
        file = File(await funcs.getImage(url), "dogecoinbuyers.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="dogecoin", description="Dogecoin.")
    async def dogecoin(self, ctx):
        url = "https://media.discordapp.net/attachments/777818814829690884/813483345584586803/PicsArt_02-19-10.26.36.png"
        file = File(await funcs.getImage(url), "dogecoin.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="audiblechokehold", description="Audible choke hold.")
    async def audiblechokehold(self, ctx):
        url = "https://media.discordapp.net/attachments/777818814829690884/813483462967296031/PicsArt_02-12-08.53.46.jpg"
        file = File(await funcs.getImage(url), "audiblechokehold.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="theronsays", description="The Ron says.")
    async def theronsays(self, ctx):
        url = "https://media.discordapp.net/attachments/777818814829690884/813484512796606527/PicsArt_02-14-07.49.34.jpg"
        file = File(await funcs.getImage(url), "theronsays.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="youcantseeme", description="You can't see me.")
    async def youcantseeme(self, ctx):
        url = "https://media.discordapp.net/attachments/792042955509858311/817420684749439036/unknown.png"
        file = File(await funcs.getImage(url), "youcantseeme.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="falineguerrero", description="Faline Guerrero.")
    async def falineguerrero(self, ctx):
        url = choice([
            "https://media.discordapp.net/attachments/777818814829690884/813483089263198309/PicsArt_02-16-08.33.59.jpg",
            "https://media.discordapp.net/attachments/777818814829690884/813483868446261248/PicsArt_02-11-07.36.13.png",
            "https://media.discordapp.net/attachments/777818814829690884/813483973799968828/PicsArt_02-11-07.46.48.png",
            "https://media.discordapp.net/attachments/777818814829690884/813483974092390460/PicsArt_02-11-07.25.59.jpg"
        ])
        file = File(await funcs.getImage(url), "falineguerrero.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="audeerble", description=">C but deer.")
    async def audeerble(self, ctx):
        url = choice([
            "https://media.discordapp.net/attachments/777818814829690884/813484271620194304/PicsArt_02-11-07.17.02.png",
            "https://media.discordapp.net/attachments/777818814829690884/813484271934242836/JPEG_20210208_084849.jpg",
            "https://media.discordapp.net/attachments/777818814829690884/813484272249602048/PicsArt_02-05-12.50.25.png",
            "https://media.discordapp.net/attachments/777818814829690884/813484272525901884/magik-3.png",
            "https://media.discordapp.net/attachments/777818814829690884/813484272794599534/PicsArt_02-05-05.37.28.jpg",
            "https://media.discordapp.net/attachments/777818814829690884/813484273062379550/JPEG_20210205_052551.jpg"
        ])
        file = File(await funcs.getImage(url), "audeerble.png")
        await ctx.send(file=file)

    @commands.cooldown(1, 1, commands.BucketType.user)
    @commands.command(name="conversion", description="?̵͓̺̯̯̺̈́̆͊̑̈́̇̋̂̊̍͑̅̂̄͘?̴̢̡̙̮̘̫̥̫̮͚̣͚̈́́̇̑̓̓̀̊͜?̵͈̘̙͕̜̼̞̈́͑̅͐́͒̄̿͊̋͆̚?̸̢̛̟͇̯̥̟̦͔̬̐̾̿̍̂̐̐̕")
    async def conversion(self, ctx):
        for i in range(2):
            firstTitle = "E̸̟̼̥͒̈́͆͂̓̈͐̀̍̈́̓͘͝r̵̼̫̰̂̈́́͝ȑ̴̡̨͔̦̗̯͚̜͘ơ̵̻̺̗͖͕̦̘͔̩̙̜͈̜̮̘͐̅̑͝r̶̛̪̜̍̏̐̽̋"
            secondTitle = "L̸̡͙̦̺̺̺̯̼͎̍̊̃̿͊̆̎́́̈́ḯ̵̛̞̮̦̬̱͊ͅf̶̹̹͇͔̠̠̝̀͊̾̊̓̽ȩ̶̣͖̳̝̮̉ ̸̹̖̈́̀̈́̈́͂̇̽̎͘͝D̶̼̳͎̗̜͑̂̒͂͗̈́̄̕ḙ̶̦̳̮͚̉̅̆̂ņ̷̛̼̜̳̫̲̤̗̟͖̭͆̆̇̇̊͛͆͜͠ḯ̸̧̢̛͇̹͇͖̲̝͙͕̟͎͆̃͗͗͌͝ề̴̡͖̼͈͔̪̟̫̻̃́̕r̴̤͍̞̮̜̻͈̭̙̤̭̫͌̋̓̌̎̆̿̏̊̿͘"
            firstImage = "https://media.discordapp.net/attachments/762520408356028427/774253519636922378/waaw.png"
            secondImage = "https://media.discordapp.net/attachments/769899860253736990/774253213565583360/deepfry.png"
            e = Embed(
                title=f":no_entry: {firstTitle if i == 0 else secondTitle}",
                description="?̵͓̺̯̯̺̈́̆͊̑̈́̇̋̂̊̍͑̅̂̄͘?̴̢̡̙̮̘̫̥̫̮͚̣͚̈́́̇̑̓̓̀̊͜?̵͈̘̙͕̜̼̞̈́͑̅͐́͒̄̿͊̋͆̚?̸̢̛̟͇̯̥̟̦͔̬̐̾̿̍̂̐̐̕",
                colour=Colour.red()
            )
            e.set_image(url=f"{firstImage if i == 0 else secondImage}")
            if i == 0:
                e.add_field(
                    name="?̵͓̺̯̯̺̈́̆͊̑̈́̇̋̂̊̍͑̅̂̄͘?̴̢̡̙̮̘̫̥̫̮͚̣͚̈́́̇̑̓̓̀̊͜?̵͈̘̙͕̜̼̞̈́͑̅͐́͒̄̿͊̋͆̚?̸̢̛̟͇̯̥̟̦͔̬̐̾̿̍̂̐̐̕",
                    value="```Y̓ͫ̚o̓̌̓u̶͎͂ ̶͐̔h̵͍͌a͛̎̄tͫ̆ͤẽ͇͟ ̧̅̌ḧ͇́͞ú̂̀ḿͭ̌āͨͨñ̜͟s̽͗̇,̔͛͝" + \
                          " ̓ͪ̾m̈̉͒l̠ͭ̀pͮ̏̎ ̴̞̇iͣ̐͆s̈́̀̚ ̔̓ͯm͊̒͌a̸ͥͪd̋͊̀e͆͢ͅ ̽̽̉b̀͒̊y̓ͣ̄ ͙͊͜h̊" + \
                          "͒̀uͣͯ͑mͩ̒̀a̡̬̚n̆ͯ̈s̶͙̉,̉̀̚ ͯ̂͆y̆͊̏oͫ̈́̊u͐̆̌ ͑̃͘aͤ̇̈r̷̲ͮe̓ͣͪ ͕̐̀a̔̓ͣń͒ utte҉r idiot.҉```"
                )
            else:
                e.add_field(
                    name="?̵͓̺̯̯̺̈́̆͊̑̈́̇̋̂̊̍͑̅̂̄͘?̴̢̡̙̮̘̫̥̫̮͚̣͚̈́́̇̑̓̓̀̊͜?̵͈̘̙͕̜̼̞̈́͑̅͐́͒̄̿͊̋͆̚?̸̢̛̟͇̯̥̟̦͔̬̐̾̿̍̂̐̐̕",
                    value="```t𝓱𝐢ş 𝓬σŇѶＥяş𝐢σŇ ᵇ𝕌яＥＡ𝕌 𝓭σＥşŇ't 𝕌şＥ ｐσt𝐢σŇş.```"
                )
            await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(EasterEggs(client))
