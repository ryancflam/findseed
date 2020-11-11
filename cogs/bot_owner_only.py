from os import system
from sys import exit
from ast import parse
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

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not self.botDisguise:
            return
        if message.channel == self.destChannel \
                or message.author == self.destChannel and isinstance(message.channel, discord.DMChannel):
            await self.originChannel.send(f"{message.author} » {message.content}" + \
                                          f"{message.attachments[0].url if message.attachments else ''}")

    def disableBotDisguise(self):
        self.botDisguise = False
        self.destChannel = None
        self.originChannel = None

    async def awaitBDStop(self, ctx):
        count = 0
        while self.botDisguise:
            count += 1
            if count == 120:
                await ctx.send("Friendly reminder that you are still in bot disguise mode!")
                count = 0
            try:
                msg = await self.client.wait_for(
                    "message", check=lambda m: m.channel == ctx.channel and m.author == ctx.author,
                    timeout=1
                )
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
                        await self.destChannel.send(msg.content)
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
            serverList += "- " + str(server) + f" ({server.member_count})\n"
        serverList = serverList[:-1]
        newList = serverList[:1998]
        await ctx.send(f"`{newList}`")

    @commands.command(name="eval", description="Evaluates Python code. Proceed with caution.",
                      aliases=["evaluate"], usage="<code>")
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


def setup(client:commands.Bot):
    client.add_cog(BotOwnerOnly(client))
