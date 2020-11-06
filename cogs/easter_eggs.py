from random import randint

from discord import Embed, File
from discord.ext import commands

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
            file = File(await funcs.getImage(url),"mlp.png")
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


def setup(client:commands.Bot):
    client.add_cog(EasterEggs(client))
