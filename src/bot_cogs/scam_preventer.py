# Hidden category

from asyncio import sleep
from re import findall

from discord.ext import commands

from src.utils import funcs

IMGUR_URL = "imgur.com"


class ScamPreventer(commands.Cog, name="Scam Preventer", command_attrs=dict(hidden=True),
                    description="A cog that tries to remove messages with Discord scam links."):
    def __init__(self, botInstance):
        self.client = botInstance
        self.client.loop.create_task(self.__readFiles())

    async def __readFiles(self):
        self.scamlinks = await funcs.readTxt("resources/scam_preventer/scam_links.txt", lines=True)
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
        await ctx.reply(embed=funcs.errorEmbed(None, "The scam preventer is not enabled."))

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
        await ctx.reply(embed=funcs.errorEmbed(None, "The scam preventer is already enabled."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="scamurls", description="Shows the scam URLs that the bot tries to remove.",
                      aliases=["scam", "scamlinks", "scamlink", "scamurl"])
    async def scamurls(self, ctx):
        await ctx.reply("<https://github.com/ryancflam/findseed/blob/master/resources/scam_preventer/scam_links.txt>")

    async def deleteEmbedOrAttachment(self, message, qrlink):
        qr = await funcs.decodeQR(qrlink)
        for url in self.scamlinks:
            if url in qr.casefold():
                try:
                    await message.delete()
                    return True
                except:
                    break
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user \
                and message.author.id not in (await funcs.readJson("data/unprompted_bots.json"))["ids"] \
                and message.guild \
                and message.guild.id not in (await funcs.readJson("data/scam_preventer.json"))["disallowed_servers"]:
            urls = findall("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", message.content)
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
                            return
                except:
                    pass
            msg = message.content.casefold().replace(" ", "")
            for url in self.scamlinks:
                if url in msg:
                    try:
                        await message.delete()
                        return
                    except:
                        pass
            if message.attachments:
                try:
                    qrlink = message.attachments[0].url
                    if await self.deleteEmbedOrAttachment(message, qrlink):
                        return
                except:
                    pass
            await sleep(3)
            if message.embeds:
                try:
                    qrlink = message.embeds[0].thumbnail.url
                    _ = await self.deleteEmbedOrAttachment(message, qrlink)
                except:
                    pass


def setup(botInstance):
    botInstance.add_cog(ScamPreventer(botInstance))
