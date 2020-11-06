#!/usr/bin/python3
from os import listdir

from discord import Intents, Game
from discord.ext import commands

import info
from other_utils import funcs


client = commands.Bot(command_prefix=info.prefix, intents=Intents.all(), case_insensitive=True)
client.remove_command("help")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    await client.change_presence(activity=Game("with seeds!"))


def main():
    for cog in listdir(f"{funcs.getPath()}/cogs"):
        if cog.endswith(".py"):
            client.load_extension(f"cogs.{cog[:-3]}")
    client.run(info.token, bot=True, reconnect=True)


if __name__ == "__main__":
    main()
