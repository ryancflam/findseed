from re import findall
from asyncio import sleep

from discord.ext import commands

from other_utils import funcs


class ScamPreventer(commands.Cog, name="Scam Preventer"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.scamurl = "discord.com/ra"

    async def deleteEmbedOrAttachment(self, message, qrlink):
        qr = await funcs.decodeQR(qrlink)
        if self.scamurl in qr:
            await message.delete()
            return True
        else:
            res = await funcs.getRequest(qr)
            qr = res.url
            if self.scamurl in qr:
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
                    tryimgur = "/imgur.com"
                    if tryimgur in link:
                        try:
                            link = link.replace(tryimgur, "/i.imgur.com")
                            link += ".jpg"
                        except:
                            pass
                    res = await funcs.getRequest(link)
                    tryscam = res.url
                except:
                    pass
                if self.scamurl in tryscam.casefold().replace(" ", ""):
                    await message.delete()
                    return
            except:
                pass
        msg = message.content.casefold().replace(" ", "")
        if self.scamurl in msg:
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
                if await self.deleteEmbedOrAttachment(message, qrlink):
                    return
            except:
                pass


def setup(client: commands.Bot):
    client.add_cog(ScamPreventer(client))
