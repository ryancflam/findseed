# Hidden category

from random import choice, randint
from re import sub

from discord.ext import commands

from other_utils import funcs


class UnpromptedMessages(commands.Cog, name="Unprompted Messages", description="Funny bot responses that are not command-invoked.",
                         command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.lastthreemsgs = {}

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild and message.guild.id in funcs.readJson("data/unprompted_messages.json")["servers"] \
                and funcs.userNotBlacklisted(self.client, message) \
                and (not message.author.bot or (message.author.id in funcs.readJson("data/unprompted_bots.json")["ids"]
                                                and message.author.id != self.client.user.id)):
            originalmsg = message.content
            lowercase = originalmsg.casefold()
            if message.channel.id not in self.lastthreemsgs:
                self.lastthreemsgs[message.channel.id] = [message]
            else:
                if len(self.lastthreemsgs[message.channel.id]) < 3:
                    self.lastthreemsgs[message.channel.id].append(message)
                if len(self.lastthreemsgs[message.channel.id]) == 3:
                    authors = sorted([self.lastthreemsgs[message.channel.id][0].author.id,
                                      self.lastthreemsgs[message.channel.id][1].author.id,
                                      self.lastthreemsgs[message.channel.id][2].author.id])
                    msgs = [self.lastthreemsgs[message.channel.id][0].content,
                            self.lastthreemsgs[message.channel.id][1].content,
                            self.lastthreemsgs[message.channel.id][2].content]
                    if len(set(authors)) == 3 and len(set(msgs)) == 1:
                        await message.channel.send(originalmsg)
                        del self.lastthreemsgs[message.channel.id]
                        return
                    else:
                        self.lastthreemsgs[message.channel.id].pop(0)
            if self.client.user in message.mentions and not (await self.client.get_context(message)).valid:
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
                    if data["status"] == 4 else data["that"].replace("A.L.I.C.E", self.client.user.name) \
                    .replace("ALICE", self.client.user.name).replace("<br>", "").replace("&quot;", '"') \
                    .replace("&lt;","<").replace("&gt;", ">").replace("&amp;", "&")
                await message.channel.send(f"{message.author.mention} {text}")
            elif not message.author.bot:
                if lowercase.startswith(("im ", "i'm ", "i‘m ", "i’m ", "i am ")):
                    if lowercase.startswith("im "):
                        im = originalmsg[3:]
                    elif lowercase.startswith(("i'm ", "i’m ", "i‘m ")):
                        im = originalmsg[4:]
                    else:
                        im = originalmsg[5:]
                    if im.casefold() == self.client.user.name:
                        await message.channel.send(f"No you're not, you're {message.author.name}.")
                    else:
                        await message.channel.send(f"Hi {im}, I'm {self.client.user.name}!")
                elif "netvigator" in lowercase:
                    await message.channel.send("notvogotor")
                elif lowercase == "h":
                    if not randint(0, 9):
                        await funcs.sendImage(
                            message.channel,
                            "https://cdn.discordapp.com/attachments/665656727332585482/667138135091838977/4a1862c.gif",
                            name="h.gif"
                        )
                    else:
                        await message.channel.send("h")
                elif lowercase == "f":
                    if not randint(0, 9):
                        await funcs.sendImage(
                            message.channel,
                            "https://cdn.discordapp.com/attachments/663264341126152223/842785581602701312/assets_f.jpg"
                        )
                    else:
                        await message.channel.send("f")
                elif "gordon ramsay" in lowercase:
                    await message.channel.send("https://i.imgur.com/XezjUCZ.gifv")
                elif "hkeaa" in lowercase:
                    await funcs.sendImage(
                        message.channel,
                        "https://cdn.discordapp.com/attachments/659771291858894849/663420485438275594/HKEAA_DENIED.png"
                    )
                elif lowercase.startswith("hmmm"):
                    if all(m in "m" for m in lowercase.split("hmm", 1)[1].replace(" ", "")):
                        await funcs.sendImage(
                            message.channel, choice(
                                [
                                    "https://media.giphy.com/media/8lQyyys3SGBoUUxrUp/giphy.gif",
                                    "https://i.redd.it/qz6eknd73qvy.gif",
                                    "https://i.imgur.com/zXAA3CV.gif",
                                    "https://i.imgur.com/ZU014ft.gif",
                                    "https://i.imgur.com/o7EsvoS.gif",
                                    "https://i.imgur.com/8DxmZY6.gif"
                                ]
                            ), name="hmmm.gif"
                        )


def setup(client: commands.Bot):
    client.add_cog(UnpromptedMessages(client))
