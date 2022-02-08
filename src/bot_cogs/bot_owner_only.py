from asyncio import TimeoutError
from contextlib import redirect_stdout
from io import StringIO
from platform import system
from subprocess import PIPE, Popen, STDOUT
from textwrap import indent
from time import time

import discord
from discord.ext import commands

from src.utils import funcs
from src.utils.base_cog import BaseCog


class BotOwnerOnly(BaseCog, name="Bot Owner Only", description="Commands for the bot owner.", command_attrs=dict(hidden=True)):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)

    @commands.command(name="killbot", description="Kills the bot. Proceed with caution.")
    @commands.is_owner()
    async def _killbot(self, ctx):
        msg = ctx.message
        await msg.reply("Are you sure? You have 10 seconds to confirm by typing `yes`.")
        try:
            _ = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author \
                                           and m.content.casefold() == "yes",
                timeout=10
            )
        except TimeoutError:
            return await ctx.send("Cancelling.")
        await ctx.reply("Stopping bot...")
        try:
            self.client.kill()
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="restart", description="Restarts the host server. Proceed with caution", aliases=["res", "reboot"])
    @commands.is_owner()
    async def _restart(self, ctx):
        msg = ctx.message
        await msg.reply("Are you sure? You have 10 seconds to confirm by typing `yes`.")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author \
                                           and m.content.casefold() == "yes",
                timeout=10
            )
        except TimeoutError:
            return await ctx.send("Cancelling restart.")
        gitpull = ""
        await msg.reply("Pull from Git repository?")
        try:
            msg = await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author \
                                           and m.content.casefold() == "yes",
                timeout=10
            )
            gitpull = f"cd {funcs.PATH} && git pull && "
        except TimeoutError:
            await msg.reply("Not git-pulling. Commencing restart...")
        else:
            await msg.reply("Git-pulling. Commencing restart...")
        obj = Popen(
            f"{gitpull}sudo reboot", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
            close_fds=False if system() == "Windows" else True
        )
        await ctx.send(embed=discord.Embed(description=funcs.formatting(obj.stdout.read().decode("utf-8"))))
        obj.kill()
        self.client.kill()

    @commands.command(name="gitpull", description="Pulls from the source repository.", aliases=["gp", "pull"])
    @commands.is_owner()
    async def _gitpull(self, ctx):
        obj = Popen(
            f"cd {funcs.PATH} && git pull", shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
            close_fds=False if system() == "Windows" else True
        )
        await ctx.reply(embed=discord.Embed(description=funcs.formatting(obj.stdout.read().decode("utf-8"))))
        obj.kill()

    @commands.command(name="say", description="Makes the bot say anything.", aliases=["tell"])
    @commands.is_owner()
    async def _say(self, ctx, *, output: str=""):
        if output == "":
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot send empty message."))
        await ctx.send(output.replace("@everyone", "everyone").replace("@here", "here"))

    @commands.command(name="reloadcog", description="Reloads a cog.", usage="<cog name>",
                      aliases=["restartcog", "reload", "updatecog"])
    @commands.is_owner()
    async def _reloadcog(self, ctx, *, cog: str=""):
        if cog == "":
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        try:
            funcs.reloadCog(self.client, cog)
            await ctx.reply(":ok_hand:")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="loadcog", description="Loads a cog.", usage="<cog name>", aliases=["enablecog", "load"])
    @commands.is_owner()
    async def _loadcog(self, ctx, *, cog: str=""):
        if cog == "":
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        try:
            funcs.loadCog(self.client, cog)
            await ctx.reply(":ok_hand:")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="unloadcog", description="Unloads a cog.", usage="<cog name>", aliases=["disablecog", "unload"])
    @commands.is_owner()
    async def _unloadcog(self, ctx, *, cog: str=""):
        if cog == "":
            return await ctx.reply(embed=funcs.errorEmbed(None, "Cannot process empty input."))
        try:
            funcs.unloadCog(self.client, cog)
            await ctx.reply(":ok_hand:")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="activecogs", description="Lists out all active cogs.", aliases=["cogs", "loadedcogs"])
    @commands.is_owner()
    async def _activecogs(self, ctx):
        cogs = self.client.cogs
        await ctx.reply(funcs.formatting("Total: {:,}\n\n- ".format(len(cogs)) + "\n- ".join(str(cog) for cog in sorted(cogs))))

    @commands.command(name="eval", description="Evaluates Python code. Proceed with caution.",
                      aliases=["evaluate"], usage="<code>")
    @commands.is_owner()
    async def _eval(self, ctx, *, code):
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
        await ctx.reply(embed=e)

    @commands.command(name="blacklistserver", description="Blacklists a server.", aliases=["bls"], usage="<server ID>")
    @commands.is_owner()
    async def _blacklistserver(self, ctx, *, serverID=None):
        if not serverID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            serverID = int(serverID)
            data = await funcs.readJson("data/blacklist.json")
            serverList = list(data["servers"])
            if serverID not in serverList:
                serverList.append(serverID)
                data["servers"] = serverList
                await funcs.dumpJson("data/blacklist.json", data)
                return await ctx.reply("Added.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Already in blacklist."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="blacklistuser", description="Blacklists a user.", aliases=["blu"], usage="<user ID>")
    @commands.is_owner()
    async def _blacklistuser(self, ctx, *, userID=None):
        if not userID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            if userID == ctx.author.id:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Are you trying to blacklist yourself?"))
            if userID in (await funcs.readJson("data/whitelist.json"))["users"]:
                return await ctx.reply(embed=funcs.errorEmbed(None, "This user is whitelisted."))
            data = await funcs.readJson("data/blacklist.json")
            userList = list(data["users"])
            if userID not in userList:
                userList.append(userID)
                data["users"] = userList
                await funcs.dumpJson("data/blacklist.json", data)
                return await ctx.reply("Added.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Already in blacklist."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unblacklistserver", description="Unblacklists a server.", aliases=["ubls"], usage="<server ID>")
    @commands.is_owner()
    async def _unblacklistserver(self, ctx, *, serverID=None):
        if not serverID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            serverID = int(serverID)
            data = await funcs.readJson("data/blacklist.json")
            serverList = list(data["servers"])
            if serverID in serverList:
                serverList.remove(serverID)
                data["servers"] = serverList
                await funcs.dumpJson("data/blacklist.json", data)
                return await ctx.reply("Removed.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Not in blacklist."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unblacklistuser", description="Unblacklists a user.", aliases=["ublu"], usage="<user ID>")
    @commands.is_owner()
    async def _unblacklistuser(self, ctx, *, userID=None):
        if not userID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = await funcs.readJson("data/blacklist.json")
            userList = list(data["users"])
            if userID in userList:
                userList.remove(userID)
                data["users"] = userList
                await funcs.dumpJson("data/blacklist.json", data)
                return await ctx.reply("Removed.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Not in blacklist."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="blacklist", description="Gets the blacklist.", aliases=["bl"])
    @commands.is_owner()
    async def _blacklist(self, ctx):
        data = await funcs.readJson("data/blacklist.json")
        serverList = list(data["servers"])
        userList = list(data["users"])
        await ctx.reply(
            "```Servers ({:,}): ".format(len(serverList)) +
            f"{'None' if not serverList else ', '.join(str(server) for server in serverList)}" +
            "\nUsers ({:,}): ".format(len(userList)) +
            f"{'None' if not userList else ', '.join(str(user) for user in userList)}```"
        )

    @commands.command(name="whitelist", description="Gets the whitelist.", aliases=["wl"])
    @commands.is_owner()
    async def _whitelist(self, ctx):
        userList = list((await funcs.readJson("data/whitelist.json"))["users"])
        await ctx.reply(
            "```Users ({:,}): ".format(len(userList)) +
            f"{'None' if not userList else ', '.join(str(user) for user in userList)}```"
        )

    @commands.command(name="whitelistuser", description="Whitelists a user.", aliases=["wlu"], usage="<user ID>")
    @commands.is_owner()
    async def _whitelistuser(self, ctx, *, userID=None):
        if not userID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            if userID in (await funcs.readJson("data/blacklist.json"))["users"]:
                return await ctx.reply(embed=funcs.errorEmbed(None, "This user is blacklisted."))
            data = await funcs.readJson("data/whitelist.json")
            userList = list(data["users"])
            if userID not in userList:
                userList.append(userID)
                data["users"] = userList
                await funcs.dumpJson("data/whitelist.json", data)
                return await ctx.reply("Added.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Already in whitelist."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unwhitelistuser", description="Unwhitelists a user.",
                      aliases=["uwlu", "uwl", "unwhitelist"], usage="<user ID>")
    @commands.is_owner()
    async def _unwhitelistuser(self, ctx, *, userID=None):
        if not userID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = await funcs.readJson("data/whitelist.json")
            userList = list(data["users"])
            if ctx.author.id == userID:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Are you trying to unwhitelist yourself?"))
            if userID in userList:
                userList.remove(userID)
                data["users"] = userList
                await funcs.dumpJson("data/whitelist.json", data)
                return await ctx.reply("Removed.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Not in whitelist."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="leaveserver", description="Makes the bot leave a given server.",
                      aliases=["leaveguild", "serverleave", "guildleave", "botleave", "botquit"], usage="<server ID>")
    @commands.is_owner()
    async def _leaveserver(self, ctx, *, serverID=None):
        if not serverID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            server = self.client.get_guild(int(serverID))
            if server:
                await ctx.reply(":ok_hand:")
                return await server.leave()
            await ctx.reply(embed=funcs.errorEmbed(None, "Unknown server."))
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="addunpromptedbot", description="Adds a Discord bot to the list of allowed unprompted bots.",
                      aliases=["aub"], usage="<bot user ID>")
    @commands.is_owner()
    async def _addunpromptedbot(self, ctx, *, userID=None):
        if not userID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = await funcs.readJson("data/unprompted_bots.json")
            userList = list(data["ids"])
            if userID not in userList:
                userList.append(userID)
                data["ids"] = userList
                await funcs.dumpJson("data/unprompted_bots.json", data)
                return await ctx.reply("Added.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Already in unprompted bots list."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="removeunpromptedbot", description="Removes a Discord bot from the list of allowed unprompted bots.",
                      aliases=["rub"], usage="<bot user ID>")
    @commands.is_owner()
    async def _removeunpromptedbot(self, ctx, *, userID=None):
        if not userID:
            return await ctx.reply(embed=funcs.errorEmbed(None, "Empty input."))
        try:
            userID = int(userID)
            data = await funcs.readJson("data/unprompted_bots.json")
            userList = list(data["ids"])
            if userID in userList:
                userList.remove(userID)
                data["ids"] = userList
                await funcs.dumpJson("data/unprompted_bots.json", data)
                return await ctx.reply("Removed.")
            await ctx.reply(embed=funcs.errorEmbed(None, "Not in unprompted bots list."))
        except ValueError:
            await ctx.reply(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unpromptedbots", description="Gets the list of unprompted bots.", aliases=["ub"])
    @commands.is_owner()
    async def _unpromptedbots(self, ctx):
        userList = list((await funcs.readJson("data/unprompted_bots.json"))["ids"])
        await ctx.reply(
            f"```Allowed unprompted bots: {'None' if not userList else ', '.join(str(user) for user in userList)}```"
        )

    @commands.command(name="exec", description="Executes terminal commands. Proceed with caution.",
                      aliases=["terminal", "execute", "ex"], usage="<input>")
    @commands.is_owner()
    async def _exec(self, ctx, *, cmd):
        try:
            obj = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=False if system() == "Windows" else True)
            e = discord.Embed(description=funcs.formatting(obj.stdout.read().decode("utf-8")))
            obj.kill()
        except Exception as ex:
            e = funcs.errorEmbed(None, str(ex))
        await ctx.reply(embed=e)

    @commands.command(name="reply", description="Replies to a `msgbotowner` message.", usage="<message ID> <channel ID> <message>")
    @commands.is_owner()
    async def _reply(self, ctx, msgid, cid, *, output: str=""):
        try:
            output = output.replace("`", "")
            ch = self.client.get_channel(int(cid))
            msg = await ch.fetch_message(int(msgid))
            user = self.client.get_user(msg.author.id)
            if "msgbotowner" not in msg.content.casefold():
                raise Exception("Not a `msgbotowner` message!")
            original = msg.content[(12 + len(self.client.command_prefix)):]
            try:
                men = ch.mention
            except:
                men = "DM"
            await user.send(f"**The bot owner has replied:**\n\n```{output}```\nYour message: `{original}` ({men})")
            await ctx.reply(f"Reply sent.\n\nYour reply: ```{output}```\nUser (ID): `{str(user)} ({user.id})`\nMessage ID:" +
                            f" `{msgid}`\nChannel ID: `{cid}`\nMessage: `{original}`")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="changename", description="Changes the username of the bot.",
                      usage="<new username>", aliases=["namechange"])
    @commands.is_owner()
    async def _changename(self, ctx, *, username):
        try:
            await self.client.user.edit(username=username)
            await ctx.reply(":ok_hand:")
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="changepfp", description="Changes the profile picture of the bot.",
                      usage="<image attachment>", aliases=["pfpchange"])
    @commands.is_owner()
    async def _changepfp(self, ctx):
        try:
            if ctx.message.attachments:
                filename = f"{time()}"
                attach = ctx.message.attachments[0]
                filename = f"{filename}-{attach.filename}"
                filepath = f"{funcs.PATH}/temp/{filename}"
                await attach.save(filepath)
                with open(filepath, "rb") as image:
                    await self.client.user.edit(avatar=image.read())
                await funcs.deleteTempFile(filename)
                await ctx.reply(":ok_hand:")
            else:
                await ctx.reply(embed=funcs.errorEmbed(None, "No attachment detected."))
        except Exception as ex:
            await ctx.reply(embed=funcs.errorEmbed(None, str(ex)))

    @commands.command(name="ownercmds", description="Shows a list of bot owner commands.",
                      aliases=["ownercommand", "ownercommands", "owner", "ownercmd", "botowner", "botowneronly", "botownercmds"])
    @commands.is_owner()
    async def _ownercmds(self, ctx):
        await ctx.reply(embed=funcs.commandsListEmbed(self.client, menu=2))


setup = BotOwnerOnly.setup
