from time import time

from discord import ButtonStyle, Embed
from discord.ui import Button, View

from src.utils.funcs import bot_utils, http_requests


def numberEmojis():
    return {0: ":zero:", 1: ":one:", 2: ":two:", 3: ":three:", 4: ":four:",
            5: ":five:", 6: ":six:", 7: ":seven:", 8: ":eight:", 9: ":nine:"}


def removeMention(userID):
    userID = str(userID)
    if userID.startswith("<@!") and userID.endswith(">"):
        userID = userID[3:-1]
    elif userID.startswith("<@") and userID.endswith(">"):
        userID = userID[2:-1]
    return userID


def commandIsOwnerOnly(command):
    return "<function is_owner.<locals>.predicate" in [str(i).split(" at")[0] for i in command.checks]


def commandIsEE(command):
    return command.cog.name == "Easter Eggs"


def commandsListEmbed(client, menu: int=0):
    e = Embed(
        title=f"{'Miscellaneous' if menu == 1 else 'Bot Owner' if menu == 2 else 'All' if menu == 3 else client.user.name} Commands"
    )
    cmds = 0
    for cog in sorted(client.cogs):
        commandsList = list(filter(
            lambda x: (x.hidden and not commandIsEE(x) and not commandIsOwnerOnly(x)) if menu == 1
            else commandIsOwnerOnly(x) if menu == 2
            else not commandIsOwnerOnly(x) and not commandIsEE(x) if menu == 3
            else not x.hidden,
            sorted(client.get_cog(cog).get_commands(), key=lambda y: y.name)
        ))
        value = ", ".join(f"`{client.command_prefix}{str(command)}`" for command in commandsList)
        if value:
            e.add_field(name=cog + " ({:,})".format(len(commandsList)), value=value, inline=False)
            cmds += len(commandsList)
    e.title += " ({:,})".format(cmds)
    if menu == 1:
        e.description = "Miscellaneous commands hidden from the main commands menu."
        allc = False
    elif menu == 2:
        e.description = "Bot owner commands."
        allc = False
    else:
        allc = True
    moreinfo = f", or {client.command_prefix}category <category> for more information about a specific category"
    e.set_footer(text=f"Use {client.command_prefix}help <command> for help with a specific command{moreinfo if allc else ''}.")
    return e


def errorEmbed(error, message):
    return Embed(title=f":no_entry: {error or 'Error'}", colour=0xe74c3c, description=message)


def newButtonView(btype: int=1, label=None, emoji=None, url=None, view=None):
    if not label and not emoji:
        raise Exception("No label or emoji.")
    view = view or View()
    if btype == 0:
        style = ButtonStyle.danger
    elif btype == 1:
        style = ButtonStyle.primary
    elif btype == 2:
        style = ButtonStyle.secondary
    else:
        style = ButtonStyle.success
    view.add_item(Button(label=label, style=style, url=url, emoji=emoji))
    return view


async def readTxtAttachment(message):
    attach = message.attachments[0]
    filename = f"{time()}-{attach.filename}"
    filepath = f"{bot_utils.PATH}/temp/{filename}"
    await attach.save(filepath)
    try:
        content = await bot_utils.readTxt("temp/" + filename)
    except:
        content = None
    await bot_utils.deleteTempFile(filename)
    return content


async def easterEggsPredicate(ctx):
    return ctx.guild and ctx.guild.id in (await bot_utils.readJson("data/easter_eggs.json"))["servers"]


async def sendImage(ctx, url: str, name: str="image.png", message=None):
    try:
        await ctx.reply(message, file=(await http_requests.getImageFile(url, name=name)))
    except:
        try:
            await ctx.send(message, file=(await http_requests.getImageFile(url, name=name)))
        except Exception as ex:
            bot_utils.printError(ctx, ex)


async def sendTime(ctx, mins, secs):
    await ctx.send(
        "`Elapsed time: {:,} minute{} and {} second{}.`".format(mins, "" if mins == 1 else "s", secs, "" if secs == 1 else "s")
    )


async def sendEmbedToChannels(embed: Embed, channels: list):
    for channel in channels:
        if channel:
            try:
                await channel.send(embed=embed)
            except:
                pass
