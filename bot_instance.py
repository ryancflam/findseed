import asyncio
from json import dump
from os import listdir, makedirs, path
from shutil import rmtree
from sys import exit
from time import time

from discord import Activity, Intents
from discord.ext.commands import Bot

from other_utils.funcs import getPath, getRequest, loadCog, reloadCog, userNotBlacklisted

PATH = getPath()

try:
    import config
except ModuleNotFoundError:
    f = open(f"{PATH}/config.py", "w")
    if path.exists(f"{PATH}/config.py.template"):
        template = open(f"{PATH}/config.py.template", "r")
        f.write(template.read())
        template.close()
    f.close()
    print("Generated file: config.py [please modify before using]")
    exit()


class BotInstance(Bot):
    def __init__(self, loop: asyncio.AbstractEventLoop):
        super().__init__(
            command_prefix="b" * (not config.production) + config.prefix,
            intents=Intents.all(),
            case_insensitive=True
        )
        self.__loop = loop
        self.__token = config.botToken
        self.__activityName = config.activityName
        self.__activityType = config.activityType
        self.__status = config.status
        self.remove_command("help")
        self.generateFiles()

    @staticmethod
    def generateJson(name, data: dict):
        file = f"{PATH}/data/{name}.json"
        if not path.exists(file):
            fobj = open(file, "w")
            dump(data, fobj, sort_keys=True, indent=4)
            fobj.close()
            print(f"Generated file: {name}.json")

    @staticmethod
    def generateDir(name):
        if not path.exists(f"{PATH}/{name}"):
            makedirs(f"{PATH}/{name}")
            print("Generated directory: " + name)

    def generateFiles(self):
        self.generateDir("data")
        if path.exists(f"{getPath()}/temp"):
            rmtree(f"{getPath()}/temp")
            print("Removed directory: temp")
        self.generateDir("temp")
        self.generateJson(
            "findseed",
            {
                "calls": 0,
                "highest": {
                    "found": 0,
                    "number": 0,
                    "time": int(time())
                }
            }
        )
        self.generateJson("finddream", {"iteration": 0, "mostPearls": 0, "mostRods": 0})
        self.generateJson("blacklist", {"servers": [], "users": []})
        self.generateJson("unprompted_bots", {"ids": []})
        self.generateJson("unprompted_messages", {"servers": []})
        self.generateJson("easter_eggs", {"servers": []})

    def startup(self):
        for cog in listdir(f"{PATH}/cogs"):
            if cog.endswith(".py"):
                loadCog(self, cog[:-3])
        super().run(self.__token, bot=True, reconnect=True)

    def kill(self):
        try:
            self.__loop.stop()
            tasks = asyncio.gather(*asyncio.Task.all_tasks(), loop=self.__loop)
            tasks.cancel()
            self.__loop.run_forever()
            tasks.exception()
            return None
        except Exception as ex:
            return ex

    async def bitcoin(self):
        btc = True
        while True:
            try:
                res = await getRequest(
                    "https://api.coingecko.com/api/v3/coins/markets",
                    params={"vs_currency": "usd", "ids": ("bitcoin" if btc else "ethereum")}
                )
                data = res.json()[0]
                ext = "🎉" if data["ath"] < data["current_price"] else ""
                msg = " @ ${:,}{}".format(data["current_price"], ext)
            except:
                msg = ""
            await self.presence(("BTC" if btc else "ETH") + msg)
            await asyncio.sleep(60)
            btc = not btc

    async def presence(self, name):
        await self.change_presence(activity=Activity(name=name, type=self.__activityType), status=self.__status)

    async def on_ready(self):
        if config.githubWebhooks:
            try:
                reloadCog(self, "github_webhooks")
            except:
                pass
        print(f"Logged in as: {self.user}")
        await (await self.application_info()).owner.send("Bot is online.")
        if self.__activityName.casefold() == "bitcoin":
            await self.loop.create_task(self.bitcoin())
        else:
            await self.presence(self.__activityName)

    async def on_message(self, message):
        ctx = await self.get_context(message)
        if ctx.valid and not self.is_ready() and userNotBlacklisted(self, message):
            return await message.channel.send(f"{self.user.name} is not ready yet, please wait!")
        if self.is_ready() and userNotBlacklisted(self, message):
            while message.content.startswith(f"{self.command_prefix} "):
                message.content = message.content.replace(f"{self.command_prefix} ", f"{self.command_prefix}", 1)
            if ctx.valid:
                await message.channel.trigger_typing()
            await self.process_commands(message)
