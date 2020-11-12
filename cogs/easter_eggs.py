from random import randint, choice

from discord.ext import commands
from discord import Embed, File, Colour

from other_utils import funcs


class EasterEggs(commands.Cog, name="Easter Eggs"):
    def __init__(self, client:commands.Bot):
        self.client = client

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
    @commands.command(name=">(", description="Just >(.")
    async def idontknowwhatthisis(self, ctx):
        url = "https://media.discordapp.net/attachments/771404776410972161/776320128953745428/angry.png"
        file = File(await funcs.getImage(url), ">(.png")
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


def setup(client:commands.Bot):
    client.add_cog(EasterEggs(client))
