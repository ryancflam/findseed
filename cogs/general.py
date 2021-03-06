from time import time

import psutil
from discord import __version__, Embed
from discord.ext import commands

from other_utils import funcs


class General(commands.Cog, name="General"):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.starttime = time()

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="ping", description="Shows the latency of the bot.", aliases=["p", "pong", "latency"])
    async def ping(self, ctx):
        ptime = int(round(time() * 1000))
        msg = await ctx.send(":ping_pong: Pong! `Pinging...`")
        ping = int(round(time() * 1000)) - ptime
        newmsg = ":ping_pong: Pong! `{:,} ms`".format(ping)
        if ping >= 1000:
            newmsg += "\n\nWell that was slow..."
        await msg.edit(content=newmsg)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="invite", description="Invite any bot to your server.", usage="[bot user ID]")
    async def invite(self, ctx, *, botid=""):
        botid = botid.replace(" ", "") or self.client.user.id
        e = Embed(
            description=f"[Invite Link](https://discord.com/oauth2/authorize?client_id={botid}" + \
                        "&permissions=473196598&scope=bot)"
        )
        if botid != self.client.user.id:
            e.set_footer(text="Note: Invite link may be invalid.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="botinfo", description="Shows information about the bot.",
                      aliases=["bi", "info", "cpu", "ram", "bot"])
    async def botinfo(self, ctx):
        appinfo = await self.client.application_info()
        e = Embed(description=appinfo.description)
        data = funcs.readJson("data/findseed.json")
        dt = self.client.user.created_at
        e.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        e.add_field(name="Owner", value=f"`{appinfo.owner}`")
        e.add_field(name="Library", value=f"`discord.py {__version__}`")
        e.add_field(name="Creation Date", value="`%s %s %s`" % (dt.day, funcs.monthNumberToName(dt.month), dt.year))
        e.add_field(name="Server Count", value="`{:,}`".format(len(self.client.guilds)))
        e.add_field(name="User Count", value="`{:,}`".format(len(set([i for i in self.client.users if not i.bot]))))
        e.add_field(name="!findseed Calls", value="`{:,}`".format(data['calls']))
        e.add_field(name="CPU Usage", value=f"`{psutil.cpu_percent()}%`")
        e.add_field(name="Memory Usage", value=f"`{dict(psutil.virtual_memory()._asdict())['percent']}%`")
        e.add_field(name="Memory Available",
                    value="`{:,} MB`".format(
                        round(float(dict(psutil.virtual_memory()._asdict())['available']) / 1024 / 1024, 2)
                    ))
        e.add_field(name="Disk Usage", value=f"`{dict(psutil.disk_usage('/')._asdict())['percent']}%`")
        e.add_field(name="Disk Space Available",
                    value="`{:,} GB`".format(
                        round(float(dict(psutil.disk_usage('/')._asdict())['free']) / 1024 / 1024 / 1024, 2)
                    ))
        e.set_footer(text=f"Bot has been up for {funcs.timeDifferenceStr(time(), self.starttime)}.")
        await ctx.send(embed=e)

    @commands.cooldown(1, 3, commands.BucketType.user)
    @commands.command(name="help", description="Shows a list of commands.", usage="[command]",
                      aliases=["cmds", "cmd", "h", "commands", "command"])
    async def help(self, ctx, *cmd):
        prefix = self.client.command_prefix
        if not cmd:
            e = Embed(
                title=f"{self.client.user.name} Commands List",
                description=f"Use `{prefix}help <command>` for help with a specific command."
            )
            for cog in sorted(self.client.cogs):
                commandsList = list(filter(
                    lambda x: not x.hidden, sorted(
                        self.client.get_cog(cog).get_commands(),
                        key=lambda y: y.name
                    )
                ))
                value = ", ".join(f"`{prefix}{str(command)}`" for command in commandsList)
                if value:
                    e.add_field(name=cog + " ({:,})".format(len(commandsList)), value=value, inline=False)
        else:
            try:
                command = self.client.get_command(cmd[0].replace(prefix, ""))
                if command.hidden and ctx.author != (await self.client.application_info()).owner:
                    raise Exception()
                name = command.name
                usage = command.usage
                aliases = sorted(command.aliases)
                e = Embed(title=f"{prefix}{name} ({command.cog_name})", description=command.description)
                e.set_footer(text="Command usage: <> = Required; [] = Optional")
                if usage:
                    e.add_field(name="Usage", value=f"```{prefix}{name} {usage}```")
                if aliases:
                    e.add_field(
                        name="Aliases", value=", ".join(f"`{prefix}{alias}`" for alias in aliases)
                    )
            except Exception:
                e = funcs.errorEmbed(None, "Unknown command.")
        await ctx.send(embed=e)

    @commands.command(name="umenable", description="Enables unprompted messages for your server.",
                      aliases=["ume", "eum", "enableum"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def umenable(self, ctx):
        data = funcs.readJson("data/unprompted_messages.json")
        serverList = list(data["servers"])
        if ctx.guild.id not in serverList:
            serverList.append(ctx.guild.id)
            data["servers"] = serverList
            funcs.dumpJson("data/unprompted_messages.json", data)
            return await ctx.send("`Enabled unprompted messages for this server.`")
        await ctx.send(embed=funcs.errorEmbed(None, "Unprompted messages are already enabled."))

    @commands.command(name="umdisable", description="Disables unprompted messages for your server.",
                      aliases=["umd", "dum", "disableum"])
    @commands.guild_only()
    @commands.has_permissions(manage_guild=True)
    async def umdisable(self, ctx):
        data = funcs.readJson("data/unprompted_messages.json")
        serverList = list(data["servers"])
        if ctx.guild.id in serverList:
            serverList.remove(ctx.guild.id)
            data["servers"] = serverList
            funcs.dumpJson("data/unprompted_messages.json", data)
            return await ctx.send("`Disabled unprompted messages for this server.`")
        await ctx.send(embed=funcs.errorEmbed(None, "Unprompted messages are not enabled."))

    @commands.cooldown(1, 120, commands.BucketType.user)
    @commands.command(name="msgbotowner", description="Sends a message to the bot owner. Spam will result in a blacklist.",
                      usage="<message>")
    async def msgbotowner(self, ctx, *, output: str=""):
        try:
            output = output.replace("`", "")
            user = (await self.client.application_info()).owner
            msgtoowner = f"**{str(ctx.author)} ({ctx.author.mention}) has left a message for you:**" + \
                         f"\n\n```{output}```\nMessage ID: `{ctx.message.id}`\nChannel ID: `{ctx.channel.id}`" + \
                         f"\nUser ID: `{ctx.author.id}`"
            if len(msgtoowner) > 2000:
                raise Exception("The message is too long.")
            await user.send(msgtoowner)
            await ctx.send(f"{ctx.author.mention} **You have left a message for the bot owner:**\n\n" + \
                           f"```{output}```\nPlease ensure that your DMs are enabled and expect a reply soon.")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))


def setup(client: commands.Bot):
    client.add_cog(General(client))
