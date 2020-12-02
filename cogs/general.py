import psutil
from json import load
from time import time

from discord import Embed, __version__
from discord.ext import commands

import info
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
        newmsg = f":ping_pong: Pong! `{ping} ms`"
        if ping >= 1000:
            newmsg += "\n\nWell that was slow..."
        await msg.edit(content=newmsg)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="invite", description="Invite the bot to your server.")
    async def invite(self, ctx):
        e = Embed(
            description=f"[Invite Link](https://discord.com/oauth2/authorize?client_id={self.client.user.id}" + \
                        "&permissions=473196598&scope=bot)"
        )
        await ctx.send(embed=e)

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="botinfo", description="Shows information about the bot.",
                      aliases=["bi", "info", "cpu", "ram", "bot"])
    async def botinfo(self, ctx):
        appinfo = await self.client.application_info()
        e = Embed(description=appinfo.description)
        with open(f"{funcs.getPath()}/data.json", "r", encoding="utf-8") as f:
            data = load(f)
        f.close()
        e.set_author(name=self.client.user.name, icon_url=self.client.user.avatar_url)
        e.add_field(name="Owner", value=f"`{appinfo.owner}`")
        e.add_field(name="Library", value=f"`discord.py {__version__}`")
        e.add_field(name="Creation Date", value=f"`{info.creationDate}`")
        e.add_field(name="Server Count", value=f"`{len(self.client.guilds)}`")
        e.add_field(name="User Count", value=f"`{len(set([i for i in self.client.users if not i.bot]))}`")
        e.add_field(name="!findseed Calls", value=f"`{data['calls']}`")
        e.add_field(name="CPU Usage", value=f"`{psutil.cpu_percent()}%`")
        e.add_field(name="Memory Usage", value=f"`{dict(psutil.virtual_memory()._asdict())['percent']}%`")
        e.add_field(name="Memory Available",
                    value=f"`{round(float(dict(psutil.virtual_memory()._asdict())['available'])/1024/1024, 2)} MB`")
        e.add_field(name="Disk Usage", value=f"`{dict(psutil.disk_usage('/')._asdict())['percent']}%`")
        e.add_field(name="Disk Space Available",
                    value=f"`{round(float(dict(psutil.disk_usage('/')._asdict())['free'])/1024/1024/1024, 2)} GB`")
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
                value = ", ".join(
                        f"`{prefix}{str(command)}`" for command in filter(
                            lambda x: not x.hidden, sorted(
                                self.client.get_cog(cog).get_commands(),
                                key=lambda y: y.name
                        )
                    )
                )
                if value:
                    e.add_field(name=cog, value=value, inline=False)
        else:
            if self.client.get_command(cmd[0].replace(prefix, "")):
                command = self.client.get_command(cmd[0].replace(prefix, ""))
                name = command.name
                usage = command.usage
                aliases = sorted(command.aliases)
                e = Embed(title=f"{prefix}{name}", description=command.description)
                e.set_footer(text="Command usage: <> = Required; [] = Optional")
                if usage:
                    e.add_field(name="Usage", value=f"```{prefix}{name} {usage}```")
                if aliases:
                    e.add_field(
                        name="Aliases", value=", ".join(f"`{prefix}{alias}`" for alias in aliases)
                    )
            else:
                e = funcs.errorEmbed(None, "Unknown command.")
        await ctx.send(embed=e)


def setup(client: commands.Bot):
    client.add_cog(General(client))
