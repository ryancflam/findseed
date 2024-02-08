from random import choice, randint
from re import sub

from discord.ext import commands

from src.utils import funcs
from src.utils.base_cog import BaseCog


class UnpromptedMessages(BaseCog, name="Unprompted Messages", command_attrs=dict(hidden=True),
                         description="Funny bot responses that are not command-invoked."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)
        self.client.loop.create_task(self.__generateFiles())
        self.lastthreemsgs = {}

    @staticmethod
    async def __generateFiles():
        await funcs.generateJson("unprompted_bots", {"ids": []})
        await funcs.generateJson("unprompted_messages", {"servers": []})

    @commands.command(name="umenable", description="Enables unprompted messages for your server.",
                      aliases=["ume", "eum", "enableum"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def umenable(self, ctx):
        data = await funcs.readJson("data/unprompted_messages.json")
        serverList = list(data["servers"])
        if ctx.guild.id not in serverList:
            serverList.append(ctx.guild.id)
            data["servers"] = serverList
            await funcs.dumpJson("data/unprompted_messages.json", data)
            return await ctx.reply("`Enabled unprompted messages for this server.`")
        await ctx.reply(embed=funcs.errorEmbed(None, "Unprompted messages are already enabled for this server."))

    @commands.command(name="umdisable", description="Disables unprompted messages for your server.",
                      aliases=["umd", "dum", "disableum"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def umdisable(self, ctx):
        data = await funcs.readJson("data/unprompted_messages.json")
        serverList = list(data["servers"])
        if ctx.guild.id in serverList:
            serverList.remove(ctx.guild.id)
            data["servers"] = serverList
            await funcs.dumpJson("data/unprompted_messages.json", data)
            return await ctx.reply("`Disabled unprompted messages for this server.`")
        await ctx.reply(embed=funcs.errorEmbed(None, "Unprompted messages are not enabled for this server."))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="unpromptedmessages", description="Shows the unprompted messages menu.", aliases=["um"])
    async def unpromptedmessages(self, ctx):
        msg = f'`"@{self.client.user.name} <input>"` - Has a cleverbot respond to user input\n' + \
              f'`"I\'m <input>"` - "Hi <input>, I\'m {self.client.user.name}!"\n' + \
              '`"netvigator" in input` - "notvogotor"\n' + \
              '`"gg"` - "pp"\n' + \
              '`"h"` - Responds with an image (1 in 10), or "h"\n' + \
              '`"f"` - Responds with an image (1 in 10), or "f"\n' + \
              '`"p"` - Responds with an image (1 in 10), or "p"\n' + \
              '`"staying alive" in input` - Responds with a gif\n' + \
              '`"hkeaa" in input` - Responds with an image\n' + \
              '`"hmmm (or with more m\'s)"` - Responds with a gif\n' + \
              '`"gordon ramsay" in input` - Responds with a gif'
        await ctx.reply(
            f"{msg}\n\nUser inputs are case-insensitive. Use `{self.client.command_prefix}umenable` to enable unprompted messages."
        )

    @commands.Cog.listener()
    async def on_message(self, message):
        if (not message.guild
            or message.guild and message.guild.id in (await funcs.readJson("data/unprompted_messages.json"))["servers"]) \
                and await funcs.userNotBlacklisted(self.client, message) \
                and (not message.author.bot or (message.author.id in (await funcs.readJson("data/unprompted_bots.json"))["ids"]
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
                        try:
                            del self.lastthreemsgs[message.channel.id]
                        except:
                            pass
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
                await message.reply(content=text)
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
                elif lowercase == "gg":
                    await message.channel.send("pp")
                elif lowercase == "h":
                    if funcs.oneIn(10):
                        rdm = randint(1, 3)
                        if rdm == 1:
                            await funcs.sendImage(
                                message.channel,
                                "https://media.discordapp.net/attachments/928912635011932201/1205087424514891826/DTiE9MtU8AAULcs.jpeg"
                            )
                        elif rdm == 2:
                            await funcs.sendImage(
                                message.channel,
                                "https://media.discordapp.net/attachments/928912635011932201/1205093293986291763/83a.png"
                            )
                        else:
                            await message.channel.send("https://tenor.com/view/letter-h-gif-9063752")
                    else:
                        await message.channel.send("h")
                elif lowercase == "f":
                    if funcs.oneIn(10):
                        await funcs.sendImage(
                            message.channel,
                            "https://cdn.discordapp.com/attachments/663264341126152223/842785581602701312/assets_f.jpg"
                        )
                    else:
                        await message.channel.send("f")
                elif lowercase == "p":
                    if funcs.oneIn(10):
                        rdm = randint(1, 3)
                        if rdm == 1:
                            await funcs.sendImage(
                                message.channel,
                                "https://cdn.discordapp.com/attachments/926862383660535898/1020988012768792606/IMG_1344.jpg"
                            )
                        elif rdm == 2:
                            await message.channel.send("https://tenor.com/view/letter-p-gif-9063760")
                        else:
                            await message.channel.send("https://tenor.com/view/phantombot-letter-p-gif-15089580")
                    else:
                        await message.channel.send("p")
                elif "gordon ramsay" in lowercase:
                    await message.channel.send("https://i.imgur.com/XezjUCZ.gifv")
                elif "staying alive" in lowercase:
                    await message.channel.send("https://tenor.com/view/stayin-alive-staying-alive-bee-gees-gif-14315934")
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


setup = UnpromptedMessages.setup
