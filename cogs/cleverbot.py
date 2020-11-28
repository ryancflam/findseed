from re import sub
from json import load
from random import choice

from discord.ext import commands

import info
from other_utils import funcs


class Cleverbot(commands.Cog, name="Cleverbot"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        with open(f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8") as f:
            data = load(f)
        f.close()
        serverList = list(data["servers"])
        userList = list(data["users"])
        allowed = True
        for serverID in serverList:
            server = self.client.get_guild(serverID)
            if server:
                member = server.get_member(message.author.id)
                if member:
                    allowed = False
                    break
        if not allowed or message.author.id in userList or \
                message.guild and message.guild.id in serverList:
            return
        if self.client.user in message.mentions and not message.content.startswith(info.prefix):
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
