from re import sub
from random import choice

from discord.ext import commands

import info
from other_utils import funcs


class Cleverbot(commands.Cog, name="Cleverbot", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if funcs.userNotBlacklisted(self.client, message) and self.client.user in message.mentions \
                and not message.content.startswith(info.prefix):
            allowedbots = [
                479937255868465156,
                492970622587109380,
                597028739616079893,
                771696725173469204,
                771403225840222238
            ]
            if message.author.bot and message.author.id not in allowedbots:
                return
            await message.channel.trigger_typing()
            msg = sub("<@!?" + str(self.client.user.id) + ">", "", message.content).strip()
            params = {
                "botid": "b8d616e35e36e881",
                "custid": message.author.id,
                "input": msg or "Hi",
                "format": "json"
            }
            res = await funcs.getRequest("https://www.pandorabots.com/pandora/talk-xml", params=params)
            data = res.json()
            if data["status"] == 4:
                text = choice(["I do not understand.", "Please say that again.", "What was that?", "Ok."])
            else:
                text = data["that"].replace("<br>", "")
                text = text.replace("&quot;", '"').replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
                text = text.replace("A.L.I.C.E", self.client.user.name).replace("ALICE", self.client.user.name)
            await message.channel.send(f"{message.author.mention} {text}")


def setup(client: commands.Bot):
    client.add_cog(Cleverbot(client))
