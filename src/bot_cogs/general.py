from datetime import datetime
from sys import version
from time import time

from discord import Embed, __version__
from discord.ext import commands
from psutil import cpu_percent, disk_usage, virtual_memory

import config
from src.utils import funcs
from src.utils.base_cog import BaseCog


class General(BaseCog, name="General", description="Standard commands relating to this bot, its features, or Discord."):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)

    @commands.command(name="ping", description="Tests the latency of the bot.", aliases=["p", "pong", "latency"])
    async def ping(self, ctx):
        ptime = int(round(time() * 1000))
        msg = await ctx.reply(":ping_pong: Pong! `Pinging...`")
        ping = int(round(time() * 1000)) - ptime
        newmsg = ":ping_pong: Pong! `{:,} ms`".format(ping)
        if ping == 420:
            newmsg += " <:weed:663638830309703680>"
        elif ping >= 1000:
            newmsg += "\n\nWell that was slow..."
        await msg.edit(content=newmsg)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="invite", description="Invite this or another bot to your server.", usage="[bot user ID]")
    async def invite(self, ctx, *, botid=""):
        botid = botid.replace(" ", "") or self.client.user.id
        e = Embed(
            description=f"[Invite Link](https://discord.com/oauth2/authorize?client_id={botid}" + \
                        "&permissions=473196598&scope=bot)"
        )
        try:
            user = self.client.get_user(int(botid))
            if not user or not user.bot:
                e.set_footer(text="Note: Invite link may be invalid.")
        except:
            e = funcs.errorEmbed(None, "Invalid input.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="botinfo", description="Shows information about the bot.",
                      aliases=["bi", "info", "cpu", "ram", "bot"])
    async def botinfo(self, ctx):
        appinfo = await self.client.application_info()
        e = Embed(description=appinfo.description)
        dt = self.client.user.created_at
        e.set_author(name=self.client.user.name, icon_url=self.client.user.avatar)
        e.set_thumbnail(url=self.client.user.avatar)
        e.add_field(name="Bot Owner", value=f"`{appinfo.owner}`")
        e.add_field(name="Python Version", value=f"`{version.split(' ')[0]}`")
        e.add_field(name="Library Version", value=f"`Pycord {__version__}`")
        e.add_field(name="Creation Date", value=funcs.dateBirthday(dt.day, dt.month, dt.year))
        e.add_field(name="Servers", value="`{:,}`".format(len(self.client.guilds)))
        e.add_field(name="Users (Excluding Bots)",
                    value="`{:,} ({:,})`".format(len(self.client.users), len([i for i in self.client.users if not i.bot])))
        e.add_field(name="CPU Usage", value=f"`{funcs.removeDotZero(cpu_percent())}%`")
        e.add_field(name="Memory Usage", value=f"`{funcs.removeDotZero(dict(virtual_memory()._asdict())['percent'])}%`")
        e.add_field(name="Memory Available",
                    value="`{} MB`".format(
                        funcs.removeDotZero(round(float(dict(virtual_memory()._asdict())['available']) / 1024 / 1024, 2))
                    ))
        e.add_field(name="Disk Usage", value=f"`{funcs.removeDotZero(dict(disk_usage('/')._asdict())['percent'])}%`")
        e.add_field(name="Disk Space Available",
                    value="`{} GB`".format(
                        funcs.removeDotZero(round(float(dict(disk_usage('/')._asdict())['free']) / 1024 / 1024 / 1024, 2))
                    ))
        try:
            res = await funcs.getRequest(f"https://api.statcord.com/v3/{self.client.user.id}",
                                         params={"Authorization": config.statcordKey})
            statcord = res.json()
            e.add_field(name="Bandwidth Usage",
                        value="`{} MB`".format(funcs.removeDotZero(round(int(statcord["data"][0]["bandwidth"]) / 1024 / 1024, 2))))
            popular = statcord["popular"][0]
            e.add_field(name="Most Popular Command",
                        value="`{}{} ({:,})`".format(self.client.command_prefix, popular['name'], int(popular['count'])))
        except:
            pass
        e.add_field(name="!findseed Calls", value="`{:,}`".format((await funcs.readJson("data/findseed.json"))['calls']))
        e.add_field(name="Local Time", value=f"`{str(datetime.fromtimestamp(int(time())))}`")
        e.set_footer(text=f"Bot uptime: {funcs.timeDifferenceStr(time(), self.client.startTime)}")
        e.set_image(url=funcs.githubRepoPic(config.githubRepo))
        await ctx.reply(embed=e,
                        view=funcs.newButtonView(2, label="GitHub Repository", url="https://github.com/" + config.githubRepo))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="serverinfo", description="Shows information about a Discord server that the bot is in.",
                      aliases=["guild", "server", "guildinfo"], usage="[server ID]")
    async def serverinfo(self, ctx, *, serverID: str=""):
        try:
            serverID = serverID.replace(" ", "") or str(ctx.guild.id)
            g = self.client.get_guild(int(serverID))
            e = Embed(description=g.description or "")
            if g.icon:
                e.set_author(name=g.name, icon_url=g.icon.url)
            else:
                e.set_author(name=g.name)
            dt = g.created_at
            members = g.members
            e.add_field(name="Owner", value=f"`{str(g.owner)}`")
            e.add_field(name="Server ID", value=f"`{g.id}`")
            e.add_field(name="Creation Date", value=funcs.dateBirthday(dt.day, dt.month, dt.year))
            e.add_field(name="Premium Boosters", value="`{:,}`".format(g.premium_subscription_count))
            if g.premium_subscriber_role:
                e.add_field(name="Premium Booster Role",
                            value=g.premium_subscriber_role.mention if ctx.guild == g else f"`{g.premium_subscriber_role}`")
            if g.discovery_splash:
                e.add_field(name="Discovery Splash", value=f"`{g.discovery_splash}`")
            e.add_field(name="Users (Excluding Bots)",
                        value="`{:,} ({:,})`".format(len(members), len([i for i in members if not i.bot])))
            e.add_field(name="Channel Categories", value="`{:,}`".format(len(g.categories)))
            e.add_field(name="Channels (Voice)", value="`{:,} ({:,})`".format(len(g.channels), len(g.voice_channels)))
            if ctx.guild == g:
                if g.public_updates_channel:
                    e.add_field(name="Public Updates Channel", value=g.public_updates_channel.mention)
                if g.afk_channel:
                    e.add_field(name="AFK Channel", value=g.afk_channel.mention)
            e.add_field(name="Roles ({:,})".format(len(g.roles)),
                        value=("".join(f"{i.mention}, " for i in g.roles)[:800].rsplit(", ", 1)[0]) if ctx.guild == g
                        else ("".join(
                            f"`{i}`, " for i in g.roles
                        )[:800].rsplit("`, ", 1)[0] + "`").replace("`@everyone`", "@everyone"))
            emojis = g.emojis
            if emojis:
                emojistxt1, _ = "".join(str(i) for i in emojis)[:800].rsplit(">", 1)
                e.add_field(name="Emojis ({:,})".format(len(emojis)), value=emojistxt1 + ">")
            if g.banner:
                e.set_image(url=g.banner.url)
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Unknown server.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="userinfo", description="Shows information about a Discord user.",
                      aliases=["member", "user", "memberinfo", "whois"], usage="[user ID OR @mention]")
    async def userinfo(self, ctx, *, userID=None):
        try:
            if not userID:
                userID = str(ctx.author.id)
            else:
                userID = funcs.removeMention(userID).replace(" ", "")
            u = self.client.get_user(int(userID))
            dt = u.created_at
            e = Embed(description=u.mention if u != self.client.user else "That's me!")
            e.set_author(name=str(u), icon_url=u.avatar)
            e.set_thumbnail(url=u.avatar)
            e.add_field(name="Is Bot", value=f"`{str(u.bot)}`")
            e.add_field(name="User ID", value=f"`{u.id}`")
            e.add_field(name="Creation Date", value=funcs.dateBirthday(dt.day, dt.month, dt.year))
            if ctx.guild:
                try:
                    member = await ctx.guild.fetch_member(userID)
                    dt2 = member.joined_at
                    e.add_field(name="Joined Server On", value=funcs.dateBirthday(dt2.day, dt2.month, dt2.year))
                    if member.nick:
                        e.add_field(name="Nickname", value=f"`{member.nick}`")
                    if member.activity:
                        e.add_field(name="Activity", value=f"`{member.activity}`")
                    e.add_field(name="Roles ({:,})".format(len(member.roles)),
                                value="".join(f"{i.mention}, " for i in member.roles)[:800].rsplit(", ", 1)[0])
                except:
                    pass
        except Exception as ex:
            funcs.printError(ctx, ex)
            e = funcs.errorEmbed(None, "Unknown user.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="category", description="Shows a list of commands in a given category.",
                      usage="[category]", aliases=["cog"])
    async def category(self, ctx, *, cogname: str="General"):
        prefix = self.client.command_prefix
        while True:
            try:
                cog = self.client.get_cog(cogname.replace("_", " ").title())
                userisowner = ctx.author == (await self.client.application_info()).owner
                commandsList = list(
                    filter(
                        lambda x: userisowner or not funcs.commandIsOwnerOnly(x) and not funcs.commandIsEE(x),
                        sorted(cog.get_commands(), key=lambda y: y.name)
                    )
                )
                if not commandsList:
                    raise Exception()
                break
            except:
                cogname = "General"
        e = Embed(title=cog.name, description=cog.description)
        e.add_field(name="Commands ({:,})".format(len(commandsList)),
                    value=", ".join(f"`{prefix}{str(command)}`" for command in commandsList))
        e.set_footer(text=f"Use {prefix}help <command> for help with a specific command.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="help", description="Shows a list of commands.", usage="[command]",
                      aliases=["cmds", "cmd", "h", "commands", "command"])
    async def help(self, ctx, *cmd):
        if not cmd:
            e = funcs.commandsListEmbed(self.client)
        else:
            try:
                prefix = self.client.command_prefix
                command = self.client.get_command(cmd[0].replace(prefix, "").casefold())
                if funcs.commandIsOwnerOnly(command) and ctx.author != (await self.client.application_info()).owner \
                        or funcs.commandIsEE(command) and not await funcs.easterEggsPredicate(ctx):
                    raise Exception()
                name = command.name
                usage = command.usage
                aliases = sorted(command.aliases)
                e = Embed(title=f"{prefix}{name}", description=command.description)
                if usage:
                    e.set_footer(text="Command usage: <> = Required; [] = Optional")
                    e.add_field(name="Usage", value=f"```{prefix}{name} {usage}```")
                if aliases:
                    e.add_field(
                        name="Aliases", value=", ".join(f"`{prefix}{alias}`" for alias in aliases)
                    )
                e.add_field(name="Category", value=f"`{command.cog.name}`")
            except Exception:
                e = funcs.errorEmbed(None, "Unknown command.")
        await ctx.reply(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="miscellaneous", aliases=["hidden"],
                      description="Shows a list of miscellaneous commands hidden from the main commands menu.")
    async def miscellaneous(self, ctx):
        await ctx.reply(embed=funcs.commandsListEmbed(self.client, menu=1))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="everygoddamncommand", hidden=True, description="Shows literally every goddamn command.")
    async def everygoddamncommand(self, ctx):
        await ctx.reply(embed=funcs.commandsListEmbed(self.client, menu=3))

    @commands.cooldown(1, 180, commands.BucketType.user)
    @commands.command(description="Feel free to use this to send a message to the bot owner, whether it be to report " +
                                  "bugs (please do) or to simply say hi. The bot owner won't bite (probably), but " +
                                  "spam will result in a blacklist.",
                      usage="<message>", name="msgbotowner")
    async def msgbotowner(self, ctx, *, output: str=""):
        try:
            output = output.replace("`", "")
            msgtoowner = f"**{str(ctx.author)} ({ctx.author.mention}) has left a message for you:**" + \
                         f"```{output}```\nMessage ID: `{ctx.message.id}`\nChannel ID: `{ctx.channel.id}`" + \
                         f"\nUser ID: `{ctx.author.id}`\n\n" + \
                         f"Reply using:```{self.client.command_prefix}reply {ctx.message.id} {ctx.channel.id} <message>```"
            if len(msgtoowner) > 2000:
                remain = len(msgtoowner) - 2000
                raise Exception(
                    "The message is too long. Please make it `{:,}` character{} shorter.".format(remain, "" if remain == 1 else "s")
                )
            await (await self.client.application_info()).owner.send(msgtoowner)
            await ctx.reply(f"{ctx.author.mention} **You have left a message for the bot owner:**\n```{output}```\n" +
                            "Please ensure that your DMs are enabled and expect a reply soon. Spam may result in a blacklist.")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="pins", description="Returns the total number of message pins in this channel.",
                      aliases=["pin"])
    async def pins(self, ctx):
        await ctx.reply(embed=Embed(title="Channel Pins", description=funcs.formatting("{:,}".format(len(await ctx.pins())))))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="poll", description="Makes a poll.", usage="<question>", aliases=["questionnaire", "question", "survey"])
    @commands.guild_only()
    async def poll(self, ctx, *, question):
        if len(question) > 200:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Question must be 200 characters or less."))
        messages, answers = [ctx.message], []
        count = 0
        while count < 20:
            messages.append(
                await ctx.send(
                    "Enter poll choice, `!undo` to delete previous choice, `!done` to publish poll, or `!cancel` to cancel."
                )
            )
            try:
                entry = await self.client.wait_for(
                    "message",
                    check=lambda m: m.author == ctx.author and m.channel == ctx.channel and len(m.content) <= 100,
                    timeout=60
                )
            except TimeoutError:
                break
            messages.append(entry)
            if entry.content.casefold() == "!done":
                break
            if entry.content.casefold() == "!undo":
                if answers:
                    answers.pop()
                    count -= 1
                else:
                    messages.append(
                        await ctx.send(embed=funcs.errorEmbed(None, "No choices."))
                    )
            elif entry.content.casefold() == "!cancel":
                return await ctx.reply("Cancelling poll.")
            else:
                answers.append((chr(0x1f1e6 + count), entry.content))
                count += 1
        try:
            await ctx.channel.delete_messages(messages)
        except:
            pass
        if len(answers) < 2:
            return await ctx.send(embed=funcs.errorEmbed(None, "Not enough choices."))
        answer = "\n".join(f"{keycap}: {content}" for keycap, content in answers)
        e = Embed(title=question, description=f"Poll by: {ctx.author.mention}")
        e.add_field(name="Choices", value=answer)
        e.set_footer(text=str(datetime.utcfromtimestamp(int(time()))) + " UTC")
        try:
            poll = await ctx.send(embed=e)
            for emoji, _ in answers:
                await poll.add_reaction(emoji)
        except Exception as ex:
            funcs.printError(ctx, ex)
            return await ctx.send(embed=funcs.errorEmbed(None, "Too many choices?"))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="avatar", description="Shows the avatar of a user.",
                      aliases=["pfp", "icon"], usage="[user ID OR @mention]")
    async def avatar(self, ctx, *, userID=None):
        if not userID:
            userID = str(ctx.author.id)
        else:
            userID = funcs.removeMention(userID).replace(" ", "")
        try:
            avatar = self.client.get_user(int(userID)).avatar
            await funcs.sendImage(ctx, avatar.url, name=f"avatar.{'gif' if avatar.is_animated() else 'png'}")
        except Exception as ex:
            funcs.printError(ctx, ex)
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid user."))

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="channelid", description="Shows the current channel's ID.", aliases=["channel", "cid"], hidden=True)
    async def channelid(self, ctx):
        await ctx.reply(f"`#{ctx.channel.id}`")


setup = General.setup
