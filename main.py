#!/usr/bin/python3

from os import listdir
from json import load

from discord import Activity, ActivityType, Intents, Status
from discord.ext import commands

import info
from other_utils import funcs


client = commands.Bot(
    command_prefix=info.prefix, intents=Intents.all(), case_insensitive=True
)
client.remove_command("help")


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    activity = Activity(name="for seeds...", type=ActivityType.watching)
    await client.change_presence(activity=activity, status=Status.idle)


@client.event
async def on_message(message):
    if client.is_ready():
        with open(
                f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8"
        ) as f:
            data = load(f)
        serverList = list(data["servers"])
        userList = list(data["users"])
        if message.author.id not in userList and \
                (not message.guild or message.guild.id not in serverList):
            await client.process_commands(message)
        f.close()


def main():
    for cog in listdir(f"{funcs.getPath()}/cogs"):
        if cog.endswith(".py"):
            client.load_extension(f"cogs.{cog[:-3]}")
    client.run(info.token, bot=True, reconnect=True)


if __name__ == "__main__":
    main()
