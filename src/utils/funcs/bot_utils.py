from json import dumps, loads
from os import path

from aiofiles import open, os
from plotly import graph_objects as go

PATH = path.dirname(path.realpath(__file__)).rsplit("src", 1)[0]


def printError(ctx, error):
    print(f"Error ({ctx.command.name}): {error}")


def formatCogName(cog):
    return cog.casefold().replace(" ", "_").replace(".py", "")


def reloadCog(client, cog):
    try:
        cog = formatCogName(cog)
        client.reload_extension(f"src.bot_cogs.{cog}")
        print(f"Reloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def loadCog(client, cog):
    try:
        cog = formatCogName(cog)
        client.load_extension(f"src.bot_cogs.{cog}")
        print(f"Loaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def unloadCog(client, cog):
    try:
        cog = formatCogName(cog)
        client.unload_extension(f"src.bot_cogs.{cog}")
        print(f"Unloaded cog: {cog}")
    except Exception as ex:
        raise Exception(ex)


def getResource(cog, resource):
    return f"/resources/{formatCogName(cog)}/{resource}"


async def deleteTempFile(file: str):
    if path.exists(f"{PATH}/temp/{file}"):
        await os.remove(f"{PATH}/temp/{file}")


async def readTxt(pathstr, lines=False):
    async with open(f"{PATH}/{pathstr}", "r", encoding="utf-8") as f:
        if lines:
            lines = await f.readlines()
            content = [i[:-1] for i in lines if i[:-1]]
        else:
            content = await f.read()
    await f.close()
    return content


async def readJson(pathstr):
    async with open(f"{PATH}/{pathstr}", "r", encoding="utf-8") as f:
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


async def userNotBlacklisted(client, message):
    if message.author.id in (await readJson("data/whitelist.json"))["users"]:
        return True
    data = await readJson("data/blacklist.json")
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
    return allowed and message.author.id not in userList \
           and (not message.guild or message.guild.id not in serverList)


async def testKaleido():
    print("Testing Kaleido...")
    try:
        go.Figure().write_image(f"{PATH}/temp/test.png")
        await deleteTempFile("test.png")
        print("Kaleido installed and ready")
    except:
        raise Exception("Kaleido is not installed!")
