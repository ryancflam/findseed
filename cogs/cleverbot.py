from random import choice
from re import sub

from discord.ext import commands

from other_utils import funcs

ALLOWED_BOTS = [
    479937255868465156,
    492970622587109380,
    597028739616079893,
    771696725173469204,
    771403225840222238
]


class Cleverbot(commands.Cog, name="Cleverbot", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        if funcs.userNotBlacklisted(self.client, message) and self.client.user in message.mentions \
                and not (await self.client.get_context(message)).valid \
                and (not message.author.bot or message.author.id in ALLOWED_BOTS):
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
            text = choice(["I do not understand.", "Please say that again.", "What was that?", "Ok."]) \
                if data["status"] == 4 else data["that"].replace("A.L.I.C.E", self.client.user.name).replace(
                "ALICE", self.client.user.name).replace("<br>", "").replace("&quot;", '"').replace("&lt;",
                "<").replace("&gt;", ">").replace("&amp;", "&")
            await message.channel.send(f"{message.author.mention} {text}")


def setup(client: commands.Bot):
    client.add_cog(Cleverbot(client))
