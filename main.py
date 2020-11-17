#!/usr/bin/python3

import asyncio
from os import listdir
from json import load

from discord import Activity, Intents
from discord.ext import commands

import info
from other_utils import funcs


class FindseedBot(commands.Bot):
    def __init__(self, loop: asyncio.AbstractEventLoop, prefix, path, token):
        super().__init__(
            command_prefix=prefix,
            intents=Intents.all(),
            case_insensitive=True
        )
        self.__loop = loop
        self.__path = path
        self.__token = token
        self.remove_command("help")

    async def on_ready(self):
        print(f"Logged in as {self.user}")
        await self.change_presence(
            activity=Activity(name="for seeds...", type=3),
            status="idle"
        )

    async def on_guild_join(self, server):
        appinfo = await self.application_info()
        await appinfo.owner.send(
            f"{self.user.name} has been added to `{server.name}`."
        )

    async def on_guild_remove(self, server):
        appinfo = await self.application_info()
        await appinfo.owner.send(
            f"{self.user.name} has been removed from `{server.name}`."
        )

    async def on_message(self, message):
        ctx = await self.get_context(message)
        if ctx.valid:
            with open(
                f"{self.__path}/blacklist.json", "r", encoding="utf-8"
            ) as f:
                data = load(f)
            serverList = list(data["servers"])
            userList = list(data["users"])
            allowed = True
            for serverID in serverList:
                server = self.get_guild(serverID)
                if server:
                    member = server.get_member(message.author.id)
                    if member:
                        allowed = False
                        break
            if allowed and message.author.id not in userList and \
                    (not message.guild or message.guild.id not in serverList):
                if self.is_ready():
                    await self.process_commands(message)
                else:
                    await message.channel.send(
                        f"{self.user.name} is not ready yet, please wait!"
                    )
            f.close()

    def startup(self):
        for cog in listdir(f"{self.__path}/cogs"):
            if cog.endswith(".py"):
                self.load_extension(f"cogs.{cog[:-3]}")
        super().run(self.__token, bot=True, reconnect=True)

    def kill(self):
        try:
            self.__loop.stop()
            tasks = asyncio.gather(
                *asyncio.Task.all_tasks(),
                loop=self.__loop
            )
            tasks.cancel()
            self.__loop.run_forever()
            tasks.exception()
            return None
        except Exception as ex:
            return ex


loop = asyncio.get_event_loop()
client = FindseedBot(
    loop=loop, prefix=info.prefix, path=funcs.getPath(), token=info.token
)

if __name__ == "__main__":
    try:
        task = loop.create_task(client.startup())
        loop.run_until_complete(task)
        loop.run_forever()
    except (KeyboardInterrupt, RuntimeError):
        print(f"Shutting down - {client.kill()}")
    except Exception as ex:
        print(f"Error - {ex}")
    finally:
        loop.close()
