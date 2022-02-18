from asyncio import sleep
from re import findall

from discord.ext import commands

from src.utils import funcs
from src.utils.base_cog import BaseCog

IMGUR_URL = "imgur.com"


class ScamPreventer(BaseCog, name="Scam Preventer", command_attrs=dict(hidden=True),
                    description="A cog that tries to remove messages with Discord scam links."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)
        self.client.loop.create_task(self.__readFiles())

    async def __readFiles(self):
        self.scamlinks = await funcs.readTxt(funcs.getResource(self.name, "scam_links.txt"), lines=True)
        await funcs.generateJson("scam_preventer", {"disallowed_servers": []})

    @commands.command(name="spdisable", description="Disables the scam preventer for your server, which is enabled by default.",
                      aliases=["spd", "dsp", "disablesp"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def spdisable(self, ctx):
        data = await funcs.readJson("data/scam_preventer.json")
        serverList = list(data["disallowed_servers"])
        if ctx.guild.id not in serverList:
            serverList.append(ctx.guild.id)
            data["disallowed_servers"] = serverList
            await funcs.dumpJson("data/scam_preventer.json", data)
            return await ctx.reply("`Disabled the scam preventer for this server.`")
        await ctx.reply(embed=funcs.errorEmbed(None, "The scam preventer is not enabled for this server."))

    @commands.command(name="spenable", description="Enables the scam preventer for your server.",
                      aliases=["spe", "esp", "enablesp"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def spenable(self, ctx):
        data = await funcs.readJson("data/scam_preventer.json")
        serverList = list(data["disallowed_servers"])
        if ctx.guild.id in serverList:
            serverList.remove(ctx.guild.id)
            data["disallowed_servers"] = serverList
            await funcs.dumpJson("data/scam_preventer.json", data)
            return await ctx.reply("`Enabled the scam preventer for this server.`")
        await ctx.reply(embed=funcs.errorEmbed(None, "The scam preventer is already enabled for this server."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="scamurls", description="Shows the scam URLs that the bot tries to remove.",
                      aliases=["scam", "scamlinks", "scamlink", "scamurl"])
    async def scamurls(self, ctx):
        await ctx.reply("<https://github.com/ryancflam/findseed/blob/master/resources/scam_preventer/scam_links.txt>")

    async def deleteEmbedOrAttachment(self, message, qrlink):
        if not qrlink:
            return False
        qr = await funcs.decodeQR(qrlink)
        if not qr:
            return False
        for url in self.scamlinks:
            if url in qr.casefold():
                try:
                    await message.delete()
                    return True
                except:
                    break
        return False

    async def detectText(self, message, txt):
        if not txt:
            return False
        text = funcs.asciiIgnore(txt.casefold().replace(" ", "").replace("\n", ""))
        urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", text)
        for link in urls:
            try:
                if link.endswith(">"):
                    link = link[:-1]
                res = await funcs.getRequest(link)
                tryscam = res.url
                try:
                    tryimgur = f"/{IMGUR_URL}"
                    if tryimgur in link:
                        try:
                            link = link.replace(tryimgur, f"/i.{IMGUR_URL}")
                            link += ".jpg"
                        except:
                            pass
                    res = await funcs.getRequest(link)
                    tryscam = res.url
                except:
                    pass
                for url in self.scamlinks:
                    if url in tryscam.casefold().replace(" ", ""):
                        await message.delete()
                        return True
            except:
                pass
        for url in self.scamlinks:
            if url in text:
                try:
                    await message.delete()
                    return True
                except:
                    pass
        return False

    async def processMessage(self, message):
        if not message.guild and message.author == self.client.user \
                or message.guild \
                and message.guild.id not in (await funcs.readJson("data/scam_preventer.json"))["disallowed_servers"]:
            for a in message.attachments:
                try:
                    qrlink = a.url
                    if await self.deleteEmbedOrAttachment(message, qrlink):
                        return
                except:
                    pass
            if await self.detectText(message, message.content):
                return
            await sleep(3)
            for e in message.embeds:
                try:
                    if await self.detectText(message, e.title) or await self.detectText(message, e.description):
                        return
                except:
                    pass
                for field in e.fields:
                    try:
                        if await self.detectText(message, field.value) or await self.detectText(message, field.name):
                            return
                    except:
                        pass
                try:
                    if await self.deleteEmbedOrAttachment(message, e.thumbnail.url) \
                            or await self.deleteEmbedOrAttachment(message, e.image.url):
                        return
                except:
                    pass

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            await self.processMessage(message)
        except:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            try:
                await self.processMessage(after)
            except:
                pass


setup = ScamPreventer.setup
