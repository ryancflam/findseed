# Hidden category

from asyncio import sleep
from re import findall

from discord.ext import commands

from other_utils import funcs

SCAM_URLS = ["discord.com/ra", "discordc.gift/", "discord.gifts/"]
IMGUR_URL = "imgur.com"


class ScamPreventer(commands.Cog, name="Scam Preventer", description="Prevents Discord scams.",
                    command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="scamurls", description="Shows the scam URLs that the bot tries to remove.",
                      aliases=["scam", "scamlinks", "scamlink", "scamurl"])
    async def scamurls(self, ctx):
        await ctx.reply(funcs.formatting("- " + "\n- ".join(SCAM_URLS), limit=2000))

    @staticmethod
    async def deleteEmbedOrAttachment(message, qrlink):
        qr = await funcs.decodeQR(qrlink)
        for url in SCAM_URLS:
            if url in qr.casefold():
                await message.delete()
                return True
            try:
                res = await funcs.getRequest(qr)
                qr = res.url
                if url in qr.casefold():
                    await message.delete()
                    return True
            except:
                continue
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author != self.client.user and message.author.id not in funcs.readJson("data/unprompted_bots.json")["ids"]:
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
                    for url in SCAM_URLS:
                        if url in tryscam.casefold().replace(" ", ""):
                            await message.delete()
                            return
                except:
                    pass
            msg = message.content.casefold().replace(" ", "")
            for url in SCAM_URLS:
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


def setup(client: commands.Bot):
    client.add_cog(ScamPreventer(client))
