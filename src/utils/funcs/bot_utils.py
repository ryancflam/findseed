from asyncio import get_event_loop
from functools import partial
from json import dumps, loads
from os import path
from time import time

from aiofiles import open, os
from discord import File
from plotly import graph_objects as go

from src.utils.base_cog import BaseCog
from src.utils.funcs.discord_ops import errorEmbed
from src.utils.funcs.string_manipulation import formatCogName

PATH = path.dirname(path.realpath(__file__)).rsplit("src", 1)[0].replace("\\", "/")
COGS_PATH = "src/bot_cogs"
RESOURCES_PATH = "resources"
VITAL_COGS = ["bot_owner_only", "general", "web_server_certificates"]


def printError(ctx, error):
    print(f"Error ({ctx.command.name}): {error}")


def getResource(cog=None, resource=None):
    return f'/{RESOURCES_PATH}/{f"{formatCogName(cogToStr(cog))}/" if cog else ""}{resource if resource else ""}'


def cogToStr(cog):
    if isinstance(cog, BaseCog):
        return cog.name
    return cog


def loadCog(client, cog):
    try:
        cog = formatCogName(cogToStr(cog))
        client.load_extension(f"{COGS_PATH.replace('/', '.')}.{cog}")
        print(f"Loaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def unloadCog(client, cog, force=False):
    try:
        cog = formatCogName(cogToStr(cog))
        if cog in VITAL_COGS and not force:
            raise Exception("Cannot unload that cog!")
        client.unload_extension(f"{COGS_PATH.replace('/', '.')}.{cog}")
        print(f"Unloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def reloadCog(client, cog, force=False):
    try:
        cog = formatCogName(cogToStr(cog))
        if cog in VITAL_COGS and not force:
            raise Exception("Cannot reload that cog!")
        client.reload_extension(f"{COGS_PATH.replace('/', '.')}.{cog}")
        print(f"Reloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def funcToCoro(func, *args, **kwargs):
    return get_event_loop().run_in_executor(None, partial(func, *args, **kwargs))


async def useImageFunc(ctx, func, *args, **kwargs):
    res = None
    attach = ctx.message.attachments[0]
    filename = f"{time()}-{attach.filename}"
    filepath = f"{PATH}/temp/{filename}"
    try:
        await attach.save(filepath)
        res = await funcToCoro(func, filepath, *args, **kwargs)
        file = File(f"{PATH}/temp/{res}")
        await ctx.reply(file=file)
    except Exception as ex:
        printError(ctx, ex)
        await ctx.reply(embed=errorEmbed(None, "An error occurred, please try again."))
    await deleteTempFile(filename)
    await deleteTempFile(res)


async def deleteTempFile(file: str):
    if path.exists(f"{PATH}/temp/{file}"):
        await os.remove(f"{PATH}/temp/{file}")


async def readTxt(pathstr, lines=False, encoding="utf-8"):
    async with open(f"{PATH}/{pathstr}", "r", encoding=encoding) as f:
        if lines:
            lines = await f.readlines()
            content = [i[:-1] for i in lines if i[:-1]]
        else:
            content = await f.read()
    await f.close()
    return content


async def writeTxt(pathstr, text):
    async with open(f"{PATH}/{pathstr}", "w") as f:
        await f.write(text)
    await f.close()


async def readJson(pathstr, encoding="utf-8"):
    async with open(f"{PATH}/{pathstr}", "r", encoding=encoding) as f:
        data = await f.read()
    await f.close()
    return loads(data)


async def dumpJson(pathstr, data):
    async with open(f"{PATH}/{pathstr}", "w") as f:
        await f.write(dumps(data, sort_keys=True, indent=4))
    await f.close()


async def generateJson(name, data: dict):
    if not path.exists(f"{PATH}/data/{name}.json"):
        await dumpJson(f"data/{name}.json", data)
        print(f"Generated file: {name}.json")


async def userIDNotBlacklisted(userID):
    if userID in (await readJson("data/whitelist.json"))["users"]:
        return True
    if userID in (await readJson("data/blacklist.json"))["users"]:
        return False
    return True


async def userNotBlacklisted(client, message):
    if message.author.id in (await readJson("data/whitelist.json"))["users"]:
        return True
    data = await readJson("data/blacklist.json")
    serverList = data["servers"]
    userList = data["users"]
    allowed = True
    for serverID in serverList:
        server = client.get_guild(serverID)
        if server:
            member = server.get_member(message.author.id)
            if member:
                allowed = False
                break
    return allowed and message.author.id not in userList \
           and (not message.guild or message.guild.id not in serverList)


async def testKaleido():
    print("Testing Kaleido...")
    try:
        await funcToCoro(go.Figure().write_image, f"{PATH}/temp/test.png")
        await deleteTempFile("test.png")
        print("Kaleido installed and ready")
    except:
        raise Exception("Kaleido is not installed!")
