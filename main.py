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
async def on_guild_join(server):
    appinfo = await client.application_info()
    await appinfo.owner.send(
        f"{client.user.name} has been added to `{server.name}`."
    )


@client.event
async def on_guild_remove(server):
    appinfo = await client.application_info()
    await appinfo.owner.send(
        f"{client.user.name} has been removed from `{server.name}`."
    )


@client.event
async def on_message(message):
    ctx = await client.get_context(message)
    if ctx.valid:
        with open(
            f"{funcs.getPath()}/blacklist.json", "r", encoding="utf-8"
        ) as f:
            data = load(f)
        serverList = list(data["servers"])
        userList = list(data["users"])
        allowed = True
        for serverID in serverList:
            server = client.get_guild(serverID)
            if server:
                member = server.get_member(message.author.id)
                if member:
                    allowed = False
                    break
        if allowed and message.author.id not in userList and \
                (not message.guild or message.guild.id not in serverList):
            if client.is_ready():
                await client.process_commands(message)
            else:
                await message.channel.send(
                    f"{client.user.name} is not ready yet, please wait a bit!"
                )
        f.close()


def main():
    for cog in listdir(f"{funcs.getPath()}/cogs"):
        if cog.endswith(".py"):
            client.load_extension(f"cogs.{cog[:-3]}")
    client.run(info.token, bot=True, reconnect=True)


if __name__ == "__main__":
    main()
