#!/usr/bin/python3

from os import listdir
from json import load

from discord import Activity, ActivityType, Intents, Status
from discord.ext import commands

import info
from other_utils import funcs

BLOCKED_MSG = "Seeing the way you approached me in the last two days and " + \
              "the toxic way you approach those you don't know I have dec" + \
              "ided to blacklist this server from using the findseed bot." + \
              "\n\nI tried to be patient, I noticed the strange behavior " + \
              "as soon as I joined for the first time. I didn't feel like" + \
              " I was being treated with respect seeing you called me wei" + \
              "rd terms and repeated what I said while I don't know you a" + \
              "nd never even spoke to you.\n\nBut the debacle yesterday m" + \
              "ade it very clear to me: you're filled with prejudice, you" + \
              " see sharing a statement in a serious channel as pretentio" + \
              "us and pretend respect and understanding without giving an" + \
              "y. In addition to that you're only approachable in one on " + \
              'one "parent" conversations since you continuously get infl' + \
              "uenced among yourselves. I still find it hard to believe y" + \
              "ou were so self-righteous to say I was being offensive whi" + \
              "le you literally joked around in a serious channel. Not gi" + \
              "ving meaning to words is a sign of immaturity.\n\nOne pers" + \
              "on was very cooperative yesterday and in a mature one on o" + \
              "ne discussion she revealed you repeat what I say when you'" + \
              "re confused and that you tend to be skeptical of intellect" + \
              "ual statements (only God knows why you're so antagonistic " + \
              "towards well thought out statements but whatever). Had you" + \
              " put at least a fraction of an effort to explain this to m" + \
              "e from the start I would have known you were not the right" + \
              " audience for such discussions and a lot of time would hav" + \
              "e been spared.\n\nI admit your way of talking to me left m" + \
              "e confused and that I misinterpreted it but You did the ex" + \
              "cellent job of confusing me even more and any attempt to r" + \
              'eason was taken as "pretentious" while it was simply commo' + \
              "n sense and me trying to understand stuff.\n\nThe radical " + \
              "thought that must be shifted is that people can't look at " + \
              "their own dirty shoes and instead stare down at the other'" + \
              "s.\n\nNow enjoy the bot you can't use."

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
        if message.author.id not in userList and allowed and \
                (not message.guild or message.guild.id not in serverList):
            if client.is_ready():
                await client.process_commands(message)
            else:
                await message.channel.send(
                    f"{client.user.name} is not ready yet, please wait a bit!"
                )
        else:
            server = client.get_guild(723394668691193877)
            if server and server.get_member(message.author.id):
                await message.channel.send(BLOCKED_MSG)
        f.close()


def main():
    for cog in listdir(f"{funcs.getPath()}/cogs"):
        if cog.endswith(".py"):
            client.load_extension(f"cogs.{cog[:-3]}")
    client.run(info.token, bot=True, reconnect=True)


if __name__ == "__main__":
    main()
