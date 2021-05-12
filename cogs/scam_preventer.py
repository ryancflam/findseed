from asyncio import sleep
from re import findall

from discord.ext import commands

from other_utils import funcs

SCAM_URL = "discord.com/ra"
IMGUR_URL = "imgur.com"


class ScamPreventer(commands.Cog, name="Scam Preventer", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client

    @staticmethod
    async def deleteEmbedOrAttachment(message, qrlink):
        qr = await funcs.decodeQR(qrlink)
        if SCAM_URL in qr:
            await message.delete()
            return True
        else:
            res = await funcs.getRequest(qr)
            qr = res.url
            if SCAM_URL in qr:
                await message.delete()
                return True
        return False

    @commands.Cog.listener()
    async def on_message(self, message):
        urls = findall(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            message.content
        )
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
                if SCAM_URL in tryscam.casefold().replace(" ", ""):
                    await message.delete()
                    return
            except:
                pass
        msg = message.content.casefold().replace(" ", "")
        if SCAM_URL in msg:
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
                await self.deleteEmbedOrAttachment(message, qrlink)
            except:
                pass


def setup(client: commands.Bot):
    client.add_cog(ScamPreventer(client))
