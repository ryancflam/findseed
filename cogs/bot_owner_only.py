from os import system
from sys import exit
from ast import parse
from json import load, dump
from asyncio import TimeoutError

import discord
from discord.ext import commands

import info
from other_utils import funcs


class BotOwnerOnly(commands.Cog, name="Bot Owner Only"):
    def __init__(self, client:commands.Bot):
        self.client = client
        self.botDisguise = False
        self.destChannel = None
        self.originChannel = None
        self.bdReminder = 0

    @commands.Cog.listener()
    async def on_message(self, message):
        if not self.botDisguise or message.author == self.client.user:
            return
        if message.channel == self.destChannel \
                or message.author == self.destChannel and isinstance(message.channel, discord.DMChannel):
            self.bdReminder = 0
            await self.originChannel.send(f"{message.author} » {message.content}" + \
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
                if content.casefold().startswith("!q") or content.casefold().startswith(f"{info.prefix}bd") \
                        or content.casefold().startswith(f"{info.prefix}botdisguise"):
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
            if content.casefold().startswith("c") or content.startswith(info.prefix):
                await ctx.send("Cancelling.")
                return
            channelID = int(content)
            self.destChannel = self.client.get_channel(channelID)
            if not self.destChannel:
                self.destChannel = self.client.get_user(channelID)
                if not self.destChannel:
                    await ctx.send(embed=funcs.errorEmbed(None, "Invalid channel. Cancelling."))
                    return
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
                if not msg.content.casefold().startswith("!q") and not msg.content.startswith(info.prefix):
                    try:
                        await self.destChannel.send(f"{msg.content}" + \
                                                    f"{msg.attachments[0].url if msg.attachments else ''}")
                    except Exception as ex:
                        await ctx.send(embed=funcs.errorEmbed(None, str(ex)))
        except TimeoutError:
            await ctx.send("Cancelling.")
            return
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid channel. Cancelling."))
            return

    @commands.command(name="code", description="Returns statistics about the bot source code.",
                      aliases=["sloc", "loc"])
    @commands.is_owner()
    async def code(self, ctx):
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
            e = discord.Embed(title=f"{self.client.user.name} Code Statistics", description=url)
            e.add_field(name="Files of Code", value=f"`{files}`")
            e.add_field(name="Total Lines", value=f"`{totalLines}`")
            e.add_field(name="Blank Lines", value=f"`{blanks}`")
            e.add_field(name="Comment Lines", value=f"`{comments}`")
            e.add_field(name="Lines of Code", value=f"`{linesOfCode}`")
            await ctx.send(embed=e)
            return

    @commands.command(name="restart", description="Restarts the host server.", aliases=["res", "reboot"])
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Are you sure? You have 10 seconds to confirm by typing `yes`.")
        try:
            await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author, timeout=10
            )
        except TimeoutError:
            await ctx.send("Cancelling restart.")
            return
        await ctx.send("Restarting...")
        system("sudo reboot")
        exit()

    @commands.command(name="gitpull", description="Pulls from the source repository.", aliases=["gp", "pull"])
    @commands.is_owner()
    async def gitpull(self, ctx):
        system("cd findseed && git pull")
        await ctx.send(":ok_hand:")

    @commands.command(name="pip", description="Executes a Pip command.", aliases=["pip3"], usage="<input>")
    @commands.is_owner()
    async def pip(self, ctx, *, cmd:str=""):
        if cmd == "":
            await ctx.send(embed=funcs.errorEmbed(None, "Cannot process empty input."))
            return
        system(f"pip3 {cmd}")
        await ctx.send(":ok_hand:")

    @commands.command(name="say", description="Makes the bot say anything.", aliases=["tell"])
    @commands.is_owner()
    async def say(self, ctx, *, output:str=""):
        if output == "":
            e = funcs.errorEmbed(None, "Cannot send empty message.")
            await ctx.send(embed=e)
            return
        await ctx.send(output.replace("@everyone", "everyone").replace("@here", "here"))

    @commands.command(name="servers", description="Returns a list of servers the bot is in.",
                      aliases=["sl", "serverlist"])
    @commands.is_owner()
    async def servers(self, ctx):
        serverList = ""
        for server in self.client.guilds:
            serverList += f"- {str(server.id)}: " + str(server) + f" ({server.member_count})\n"
        serverList = serverList[:-1]
        newList = serverList[:1998]
        await ctx.send(f"`{newList}`")

    @commands.command(name="eval", description="Evaluates Python code. Proceed with caution.",
                      aliases=["evaluate", "calc"], usage="<code>")
    @commands.is_owner()
    async def eval(self, ctx, *, code:str=""):
        if code == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            try:
                fnName = "_eval_expr"
                code = code.strip("` ")
                code = "\n".join(f"    {i}" for i in code.splitlines())
                body = f"async def {fnName}():\n{code}"
                parsed = parse(body)
                body = parsed.body[0].body
                funcs.insertReturns(body)
                env = {
                    "bot": ctx.bot,
                    "discord": discord,
                    "commands": commands,
                    "ctx": ctx,
                    "__import__": __import__,
                    "funcs":funcs
                }
                exec(compile(parsed, filename="<ast>", mode="exec"), env)
                res = (await eval(f"{fnName}()", env))
                e = discord.Embed(description=f"```\n{str(res)}```")
            except Exception:
                e = funcs.errorEmbed(None, "Error processing input.")
        await ctx.send(embed=e)

    @commands.command(name="blacklistserver", description="Blacklists a server.",
                      aliases=["bls"], usage="<server ID>")
    @commands.is_owner()
    async def blacklistserver(self, ctx, *, serverID=None):
        if not serverID:
            await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
            return
        try:
            serverID = int(serverID)
            with open(f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8") as f:
                data = load(f)
            f.close()
            serverList = list(data["servers"])
            if serverID not in serverList:
                serverList.append(serverID)
                data["servers"] = serverList
                with open(f"{funcs.getPath()}/blacklist.json", "w") as f:
                    dump(data, f, sort_keys=True, indent=4)
                f.close()
                await ctx.send("Added.")
            else:
                await ctx.send(embed=funcs.errorEmbed(None, "Already in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="blacklistuser", description="Blacklists a user.",
                      aliases=["blu"], usage="<user ID>")
    @commands.is_owner()
    async def blacklistuser(self, ctx, *, userID=None):
        if not userID:
            await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
            return
        try:
            userID = int(userID)
            if userID == ctx.author.id:
                await ctx.send(embed=funcs.errorEmbed(
                    None, "Are you trying to blacklist yourself, you dumb retard??!@?@?#!?"
                ))
                return
            with open(f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8") as f:
                data = load(f)
            f.close()
            userList = list(data["users"])
            if userID not in userList:
                userList.append(userID)
                data["users"] = userList
                with open(f"{funcs.getPath()}/blacklist.json", "w") as f:
                    dump(data, f, sort_keys=True, indent=4)
                f.close()
                await ctx.send("Added.")
            else:
                await ctx.send(embed=funcs.errorEmbed(None, "Already in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unblacklistserver", description="Unblacklists a server.",
                      aliases=["ubls"], usage="<server ID>")
    @commands.is_owner()
    async def unblacklistserver(self, ctx, *, serverID=None):
        if not serverID:
            await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
            return
        try:
            serverID = int(serverID)
            with open(f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8") as f:
                data = load(f)
            f.close()
            serverList = list(data["servers"])
            if serverID in serverList:
                serverList.remove(serverID)
                data["servers"] = serverList
                with open(f"{funcs.getPath()}/blacklist.json", "w") as f:
                    dump(data, f, sort_keys=True, indent=4)
                f.close()
                await ctx.send("Removed.")
            else:
                await ctx.send(embed=funcs.errorEmbed(None, "Not in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="unblacklistuser", description="Unblacklists a user.",
                      aliases=["ublu"], usage="<user ID>")
    @commands.is_owner()
    async def unblacklistuser(self, ctx, *, userID=None):
        if not userID:
            await ctx.send(embed=funcs.errorEmbed(None, "Empty input."))
            return
        try:
            userID = int(userID)
            with open(f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8") as f:
                data = load(f)
            f.close()
            userList = list(data["users"])
            if userID in userList:
                userList.remove(userID)
                data["users"] = userList
                with open(f"{funcs.getPath()}/blacklist.json", "w") as f:
                    dump(data, f, sort_keys=True, indent=4)
                f.close()
                await ctx.send("Removed.")
            else:
                await ctx.send(embed=funcs.errorEmbed(None, "Not in blacklist."))
        except ValueError:
            await ctx.send(embed=funcs.errorEmbed(None, "Invalid input."))

    @commands.command(name="blacklist", description="Gets the blacklist.", aliases=["bl"])
    @commands.is_owner()
    async def blacklist(self, ctx):
        with open(f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8") as f:
            data = load(f)
        f.close()
        serverList = list(data["servers"])
        userList = list(data["users"])
        await ctx.send(
            f"```Servers: {'None' if serverList == [] else ', '.join(str(server) for server in serverList)}" + \
            f"\nUsers: {'None' if userList == [] else ', '.join(str(user) for user in userList)}```"
        )


def setup(client:commands.Bot):
    client.add_cog(BotOwnerOnly(client))
