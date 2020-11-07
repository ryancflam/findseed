from os import system
from sys import exit
from ast import parse
from asyncio import TimeoutError
from subprocess import check_output, CalledProcessError

import discord
from discord.ext import commands

from other_utils import funcs


class BotOwnerOnly(commands.Cog, name="Bot Owner Only"):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.command(name="restart", description="Restarts the host server.", aliases=["res", "reboot"])
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Are you sure? You have 10 seconds to confirm by typing `yes`.")
        try:
            await self.client.wait_for(
                "message", check=lambda m: m.channel == ctx.message.channel and m.author == ctx.author, timeout=10
            )
        except TimeoutError:
            await ctx.send("Cancelling restart.")
            return
        await ctx.send("Restarting...")
        system("sudo reboot")
        exit()

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

    @commands.command(name="terminal", description="Executes terminal commands. Proceed with caution.",
                      aliases=["exec"], usage="<command(s)>")
    @commands.is_owner()
    async def eval(self, ctx, *, cmd:str=""):
        if cmd == "":
            e = funcs.errorEmbed(None, "Cannot process empty input.")
        else:
            cmdList = cmd.split(" ")
            output = None
            try:
                output = check_output(cmdList)
                output = output.decode("unicode_escape")
            except CalledProcessError:
                e = funcs.errorEmbed(None, f"```\n{output}```")
            else:
                e = discord.Embed(description=funcs.formatting("\n" + output))
        await ctx.send(embed=e)


def setup(client:commands.Bot):
    client.add_cog(BotOwnerOnly(client))
