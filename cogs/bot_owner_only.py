from asyncio import TimeoutError
from contextlib import redirect_stdout
from io import StringIO
from platform import system
from subprocess import PIPE, Popen, STDOUT
from textwrap import indent

import discord
from discord.ext import commands

from other_utils import funcs


class BotOwnerOnly(commands.Cog, name="Bot Owner Only", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client
        self.botDisguise = False
        self.destChannel = None
        self.originChannel = None
        self.bdReminder = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if (message.channel == self.destChannel
                or message.author == self.destChannel and isinstance(message.channel, discord.DMChannel)) \
                and self.botDisguise and message.author != self.client.user:
            self.bdReminder = 0
            await self.originChannel.send(f"**{message.author}** » {message.content}" + \
                                          f"{message.attachments[0].url if message.attachments else ''}")

    def disableBotDisguise(self):
        self.botDisguise = False
        self.destChannel = None
        self.originChannel = None
        self.bdReminder = 0

    async def awaitBDStop(self, ctx):
        while self.botDisguise:
            self.bdReminder += 1
            if self.bdReminder == 120:
                await ctx.send("Friendly reminder that you are still in bot disguise mode!")
                self.bdReminder = 0
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                    timeout=1
                )
                self.bdReminder = 0
                content = msg.content
                prefix = self.client.command_prefix
                if content.casefold().startswith(("!q", f"{prefix}bd", f"{prefix}botdisguise")):
                    await ctx.send("Exiting bot disguise mode.")
                    self.disableBotDisguise()
            except TimeoutError:
                continue

    @commands.command(name="resetbotdisguise", description="Resets bot disguise mode.", aliases=["rbd"])
    @commands.is_owner()
    async def resetbotdisguise(self, ctx):
        self.disableBotDisguise()
        await ctx.send(":ok_hand:")

    @commands.command(name="botdisguise", description="Enables bot disguise mode.", aliases=["bd"])
    @commands.is_owner()
    async def botdisguise(self, ctx):
        if self.botDisguise:
            return
        await ctx.send("Please enter channel ID, or `cancel` to cancel.")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=30
            )
            content = msg.content
            if content.casefold().startswith(("c", self.client.command_prefix)):
                return await ctx.send("Cancelling.")
            channelID = int(content)
            self.destChannel = self.client.get_channel(channelID)
            if not self.destChannel:
                self.destChannel = self.client.get_user(channelID)
                if not self.destChannel:
                    return await ctx.send(embed=funcs.errorEmbed(None, "Invalid channel. Cancelling."))
            self.botDisguise = True
            self.originChannel = ctx.channel
            self.client.loop.create_task(self.awaitBDStop(ctx))
            await ctx.send("You are now in bot disguise mode! Type `!q` to quit.")
            while self.botDisguise:
                try:
                    msg = await self.client.wait_for(
                        "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                        timeout=1
                    )
                except TimeoutError:
                    continue
                if not msg.content.casefold().startswith(("!q", self.client.command_prefix)):
                    try:
                        await self.destChannel.send(f"{msg.content}" + \
                                                    f"{msg.attachments[0].url if msg.attachments else ''}")
                    except Exception as ex:
                        await ctx.send(embed=funcs.errorEmbed(None, str(ex)))
        except TimeoutError:
            return await ctx.send("Cancelling.")
        except ValueError:
            return await ctx.send(embed=funcs.errorEmbed(None, "Invalid channel. Cancelling."))

    @commands.command(name="code", description="Returns statistics about the bot source code.", aliases=["sloc"])
    @commands.is_owner()
    async def code(self, ctx):
        await ctx.send("Getting repository code statistics. Please wait...")
        url = "https://api.codetabs.com/v1/loc/?github=ryancflam/findseed"
        res = await funcs.getRequest(url)
        data = res.json()
        for i in range(len(data)):
            if data[i]["language"] != "Python":
                continue
            files = data[i]["files"]
            totalLines = data[i]["lines"]
            blanks = data[i]["blanks"]
            comments = data[i]["comments"]
            linesOfCode = data[i]["linesOfCode"]
            e = discord.Embed(title="!findseed Code Statistics", description=url)
            e.add_field(name="Files of Code", value="`{:,}`".format(files))
            e.add_field(name="Total Lines", value="`{:,}`".format(totalLines))
            e.add_field(name="Blank Lines", value="`{:,}`".format(blanks))
            e.add_field(name="Comment Lines", value="`{:,}`".format(comments))
            e.add_field(name="Lines of Code", value="`{:,}`".format(linesOfCode))
            return await ctx.send(embed=e)

    @commands.command(name="restart", description="Restarts the host server.", aliases=["res", "reboot"])
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Are you sure? You have 10 seconds to confirm by typing `yes`.")
        try:
            await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author \
                                           and m.content.casefold() == "yes",
                timeout=10
            )
        except TimeoutError:
            return await ctx.send("Cancelling restart.")
        gitpull = ""
        await ctx.send("Pull from Git repository?")
        try:
            await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author \
                                           and m.content.casefold() == "yes",
                timeout=10
            )
            gitpull = f"cd {funcs.getPath()} && git pull && "
        except TimeoutError:
            await ctx.send("Not git-pulling. Commencing restart...")
        else:
            await ctx.send("Git-pulling. Commencing restart...")
        obj = Popen(
            f"{gitpull}sudo reboot", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
            close_fds=False if system() == "Windows" else True
        )
        await ctx.send(embed=discord.Embed(description=funcs.formatting(obj.stdout.read().decode("utf-8"))))
        obj.kill()

    @commands.command(name="gitpull", description="Pulls from the source repository.", aliases=["gp", "pull"])
    @commands.is_owner()
    async def gitpull(self, ctx):
        obj = Popen(
            f"cd {funcs.getPath()} && git pull", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
            close_fds=False if system() == "Windows" else True
        )
        await ctx.send(embed=discord.Embed(description=funcs.formatting(obj.stdout.read().decode("utf-8"))))
        obj.kill()

    @commands.command(name="say", description="Makes the bot say anything.", aliases=["tell"])
    @commands.is_owner()
    async def say(self, ctx, *, output: str=""):
        if output == "":
            e = funcs.errorEmbed(None, "Cannot send empty message.")
            return await ctx.send(embed=e)
        await ctx.send(output.replace("@everyone", "everyone").replace("@here", "here"))

    @commands.command(name="servers", description="Returns a list of servers the bot is in.", aliases=["sl", "serverlist"])
    @commands.is_owner()
    async def servers(self, ctx):
        serverList = ""
        for server in self.client.guilds:
            serverList += f"- {str(server.id)}: " + str(server) + f" ({server.member_count})\n"
        serverList = serverList[:-1]
        newList = serverList[:1998]
        await ctx.send(f"`{newList}`")

    @commands.command(name="reloadcog", description="Reloads a cog.", usage=["<cog name>"])
    @commands.is_owner()
    async def reloadcog(self, ctx, *, cog: str=""):
        if cog == "":
            return await ctx.send(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        try:
            self.client.reload_extension(f"cogs.{cog.casefold().replace(' ', '_').replace('.py', '')}")
            print(f"Reloaded cog: {cog}")
            await ctx.send(":ok_hand:")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="loadcog", description="Loads a cog.", usage=["<cog name>"], aliases=["enablecog"])
    @commands.is_owner()
    async def loadcog(self, ctx, *, cog: str=""):
        if cog == "":
            return await ctx.send(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        try:
            self.client.load_extension(f"cogs.{cog.casefold().replace(' ', '_').replace('.py', '')}")
            print(f"Loaded cog: {cog}")
            await ctx.send(":ok_hand:")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="unloadcog", description="Unloads a cog.", usage=["<cog name>"], aliases=["disablecog"])
    @commands.is_owner()
    async def unloadcog(self, ctx, *, cog: str=""):
        if cog == "":
            return await ctx.send(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        try:
            self.client.unload_extension(f"cogs.{cog.casefold().replace(' ', '_').replace('.py', '')}")
            print(f"Unloaded cog: {cog}")
            await ctx.send(":ok_hand:")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="eval", description="Evaluates Python code. Proceed with caution.",
                      aliases=["evaluate"], usage="<code>")
    @commands.is_owner()
    async def eval(self, ctx, *, code):
        code = "\n".join(code.split("\n")[1:][:-3]) if code.startswith("```") and code.endswith("```") else code
        localvars = {
            "discord": discord,
            "commands": commands,
            "ctx": ctx,
            "__import__": __import__,
            "funcs": funcs,
            "client": self.client
        }
        stdout = StringIO()
        try:
            with redirect_stdout(stdout):
                exec(f"async def func():\n{indent(code, '    ')}", localvars)
                obj = await localvars["func"]()
                result = f"{stdout.getvalue()}"
                e = discord.Embed(description=funcs.formatting(str(result)))
                if obj:
                    e.add_field(name="Returned", value=funcs.formatting(str(obj), limit=1024))
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.command(name="blacklistserver", description="Blacklists a server.",
                      aliases=["bls"], usage="<server ID>")
    @commands.is_owner()
    async def blacklistserver(self, ctx, *, serverID=None):
        if not serverID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            serverID = int(serverID)
            data = funcs.readJson("data/blacklist.json")
            serverList = list(data["servers"])
            if serverID not in serverList:
                serverList.append(serverID)
                data["servers"] = serverList
                funcs.dumpJson("data/blacklist.json", data)
                return await ctx.send("Added.")
            await ctx.send(embed=funcs.errorEmbed(None, "Already in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="blacklistuser", description="Blacklists a user.",
                      aliases=["blu"], usage="<user ID>")
    @commands.is_owner()
    async def blacklistuser(self, ctx, *, userID=None):
        if not userID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            if userID == ctx.author.id:
                return await ctx.send(embed=funcs.errorEmbed(
                    None, "Are you trying to blacklist yourself, you dumb retard??!@?@?#!?"
                ))
            data = funcs.readJson("data/blacklist.json")
            userList = list(data["users"])
            if userID not in userList:
                userList.append(userID)
                data["users"] = userList
                funcs.dumpJson("data/blacklist.json", data)
                return await ctx.send("Added.")
            await ctx.send(embed=funcs.errorEmbed(None, "Already in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unblacklistserver", description="Unblacklists a server.",
                      aliases=["ubls"], usage="<server ID>")
    @commands.is_owner()
    async def unblacklistserver(self, ctx, *, serverID=None):
        if not serverID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            serverID = int(serverID)
            data = funcs.readJson("data/blacklist.json")
            serverList = list(data["servers"])
            if serverID in serverList:
                serverList.remove(serverID)
                data["servers"] = serverList
                funcs.dumpJson("data/blacklist.json", data)
                return await ctx.send("Removed.")
            await ctx.send(embed=funcs.errorEmbed(None, "Not in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unblacklistuser", description="Unblacklists a user.",
                      aliases=["ublu"], usage="<user ID>")
    @commands.is_owner()
    async def unblacklistuser(self, ctx, *, userID=None):
        if not userID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = funcs.readJson("data/blacklist.json")
            userList = list(data["users"])
            if userID in userList:
                userList.remove(userID)
                data["users"] = userList
                funcs.dumpJson("data/blacklist.json", data)
                return await ctx.send("Removed.")
            await ctx.send(embed=funcs.errorEmbed(None, "Not in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="blacklist", description="Gets the blacklist.", aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        data = funcs.readJson("data/blacklist.json")
        serverList = list(data["servers"])
        userList = list(data["users"])
        await ctx.send(
            f"```Servers: {'None' if not serverList else ', '.join(str(server) for server in serverList)}" + \
            f"\nUsers: {'None' if not userList else ', '.join(str(user) for user in userList)}```"
        )

    @commands.command(name="leaveserver", description="Makes the bot leave a given server.",
                      aliases=["leaveguild", "serverleave", "guildleave"], usage="<server ID>")
    @commands.is_owner()
    async def leaveserver(self, ctx, *, serverID=None):
        if not serverID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            server = self.client.get_guild(int(serverID))
            if server:
                return await server.leave()
            await ctx.send(embed=funcs.errorEmbed(None, "Unknown server."))
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="addunpromptedbot", description="Adds a Discord bot to the list of allowed unprompted bots.",
                      aliases=["aub"], usage="<bot user ID>")
    @commands.is_owner()
    async def addunpromptedbot(self, ctx, *, userID=None):
        if not userID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = funcs.readJson("data/unprompted_bots.json")
            userList = list(data["ids"])
            if userID not in userList:
                userList.append(userID)
                data["ids"] = userList
                funcs.dumpJson("data/unprompted_bots.json", data)
                return await ctx.send("Added.")
            await ctx.send(embed=funcs.errorEmbed(None, "Already in unprompted bots list."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="removeunpromptedbot", description="Removes a Discord bot from the list of allowed unprompted bots.",
                      aliases=["rub"], usage="<bot user ID>")
    @commands.is_owner()
    async def removeunpromptedbot(self, ctx, *, userID=None):
        if not userID:
            return await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = funcs.readJson("data/unprompted_bots.json")
            userList = list(data["ids"])
            if userID in userList:
                userList.remove(userID)
                data["ids"] = userList
                funcs.dumpJson("data/unprompted_bots.json", data)
                return await ctx.send("Removed.")
            await ctx.send(embed=funcs.errorEmbed(None, "Not in unprompted bots list."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unpromptedbots", description="Gets the list of unprompted bots.", aliases=["ub"])
    @commands.is_owner()
    async def unpromptedbots(self, ctx):
        userList = list(funcs.readJson("data/unprompted_bots.json")["ids"])
        await ctx.send(
            f"```Allowed unprompted bots: {'None' if not userList else ', '.join(str(user) for user in userList)}```"
        )

    @commands.command(name="exec", description="Executes terminal commands. Proceed with caution.",
                      aliases=["terminal", "execute", "ex"], usage="<input>")
    @commands.is_owner()
    async def exec(self, ctx, *, cmd):
        try:
            obj = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False if system() == "Windows" else True)
            e = discord.Embed(description=funcs.formatting(obj.stdout.read().decode("utf-8")))
            obj.kill()
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.send(embed=e)

    @commands.command(name="reply", description="Replies to a user message.", usage="<message ID> <channel ID> <message>")
    @commands.is_owner()
    async def reply(self, ctx, msgid, cid, *, output: str=""):
        try:
            output = output.replace("`", "")
            ch = self.client.get_channel(int(cid))
            msg = await ch.fetch_message(int(msgid))
            user = self.client.get_user(msg.author.id)
            if "msgbotowner" not in msg.content.casefold():
                raise Exception("Not a `msgbotowner` message!")
            original = msg.content[(12 + len(self.client.command_prefix)):]
            await user.send(f"**The bot owner has replied:**\n\n```{output}```\nYour message: `{original}` ({ch.mention})")
            await ctx.send(f"Reply sent.\n\nYour reply: ```{output}```\nUser (ID): `{str(user)} ({user.id})`\nMessage ID:" + \
                           f" `{msgid}`\nChannel ID: `{cid}`\nMessage: `{original}`")
        except Exception as ex:
            await ctx.send(embed=funcs.errorEmbed(None, str(ex)))


def setup(client: commands.Bot):
    client.add_cog(BotOwnerOnly(client))
