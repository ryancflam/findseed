from os import listdir, path
from sys import exit
from time import time

from aiofiles.os import mkdir
from aioshutil import rmtree
from discord import Activity, Intents
from discord.ext import commands, tasks
from statcord import Client

from src.utils import funcs

try:
    import config
    try:
        if not config.ready():
            raise Exception
    except:
        print("Warning - config.py is not ready, please check for missing fields")
        exit()
except ModuleNotFoundError:
    f = open(f"{funcs.PATH}/config.py", "w")
    template = open(f"{funcs.PATH}/config.py.template", "r")
    f.write(template.read())
    template.close()
    f.close()
    print("Generated file: config.py - please fill in the fields before using")
    exit()


class BotInstance(commands.AutoShardedBot):
    def __init__(self, loop):
        super().__init__(
            command_prefix="b" * (not config.production) + config.prefix,
            intents=Intents(
                message_content=True,
                guilds=True,
                members=True,
                bans=True,
                emojis=False,
                integrations=False,
                webhooks=False,
                invites=False,
                voice_states=False,
                presences=True,
                guild_messages=True,
                dm_messages=True,
                guild_reactions=True,
                dm_reactions=True,
                guild_typing=True,
                dm_typing=True
            ),
            case_insensitive=True,
            strip_after_prefix=True,
            chunk_guilds_at_startup=True,
            slash_commands=False
        )
        self.startTime = time()
        self.loop.create_task(self.__generateFiles())
        self.remove_command("help")
        self.__getTickers.start()
        self.__eventLoop = loop
        self.__token = config.botToken
        self.__activityName = config.activityName
        self.__activityType = config.activityType
        self.__status = config.status
        self.__statcord = Client(self, config.statcordKey)
        self.__statcord.start_loop()
        self.__btcPresence = self.__activityName.casefold() == "bitcoin"
        self.__btcPrice = None
        self.__btcATH = None
        self.__ethPrice = None
        self.__ethATH = None

    def startup(self):
        for cog in listdir(f"{funcs.PATH}/{funcs.COGS_PATH}"):
            if cog.endswith(".py"):
                funcs.loadCog(self, cog)
        super().run(self.__token, reconnect=True)

    def kill(self):
        print("Stopping bot...")
        try:
            for cog in sorted(self.cogs):
                funcs.unloadCog(self, cog, force=True)
            self.__eventLoop.stop()
            return exit()
        except Exception as ex:
            return ex

    @staticmethod
    async def __generateDir(name):
        if not path.exists(f"{funcs.PATH}/{name}"):
            await mkdir(f"{funcs.PATH}/{name}")
            print("Generated directory: " + name)

    async def __generateFiles(self):
        self.emoji = await funcs.readJson(funcs.getResource(resource="emoji.json"))
        if path.exists(f"{funcs.PATH}/temp"):
            await rmtree(f"{funcs.PATH}/temp")
            print("Removed directory: temp")
        await self.__generateDir("temp")
        await funcs.generateJson("blacklist", {"servers": [], "users": []})
        await funcs.generateJson("whitelist", {"users": []})
        await funcs.generateJson("channels_following_repo", {"channels": []})

    async def __invokeCommand(self, message):
        ctx = await self.get_context(message)
        if ctx.valid and not self.is_ready() and await funcs.userNotBlacklisted(self, message):
            return await message.channel.send(f"{self.user.name} is not ready yet, please wait!")
        if self.is_ready() and await funcs.userNotBlacklisted(self, message):
            if ctx.valid and not ctx.author.bot:
                if not funcs.commandIsEE(ctx.command):
                    await message.channel.trigger_typing()
                await self.process_commands(message)

    @tasks.loop(hours=24.0)
    async def __getTickers(self):
        self.tickers = await funcs.getTickers()

    @tasks.loop(minutes=2.0)
    async def __bitcoin(self):
        try:
            res = await funcs.getRequest(
                "https://api.coingecko.com/api/v3/coins/markets",
                params={"vs_currency": "usd", "ids": ("bitcoin" if self.__btcPresence else "ethereum")}
            )
            data = res.json()[0]
            if self.__btcPresence:
                self.__btcATH = data["ath"]
                self.__btcPrice = data["current_price"]
            else:
                self.__ethATH = data["ath"]
                self.__ethPrice = data["current_price"]
            ext = "🎉" if data["ath"] < data["current_price"] else ""
            msg = " @ ${:,}{}".format(data["current_price"], ext)
        except Exception as ex:
            print("Error - " + str(ex))
            if self.__btcPresence and self.__btcPrice:
                ext = "🎉" if self.__btcATH and self.__btcATH < self.__btcPrice else ""
                msg = " @ ${:,}{}".format(self.__btcPrice, ext)
            elif not self.__btcPresence and self.__ethPrice:
                ext = "🎉" if self.__ethATH and self.__ethATH < self.__ethPrice else ""
                msg = " @ ${:,}{}".format(self.__ethPrice, ext)
            else:
                msg = ""
        await self.__presence(("BTC" if self.__btcPresence else "ETH") + msg)
        self.__btcPresence = not self.__btcPresence

    async def __presence(self, name):
        await self.change_presence(activity=Activity(name=name, type=self.__activityType), status=self.__status)

    async def on_ready(self):
        owner = (await self.application_info()).owner
        await owner.send("Bot is online.")
        try:
            await funcs.testKaleido()
        except Exception as ex:
            print(f"Warning - {ex}")
        data = await funcs.readJson("data/whitelist.json")
        wl = list(data["users"])
        if owner.id not in wl:
            wl.append(owner.id)
            data["users"] = wl
            await funcs.dumpJson("data/whitelist.json", data)
        print(f"Logged in as Discord user: {self.user}")
        if self.__btcPresence:
            print("Using Bitcoin/Ethereum price status")
            self.__bitcoin.start()
        else:
            await self.__presence(self.__activityName)

    async def on_message(self, message):
        await self.__invokeCommand(message)

    async def on_message_edit(self, before, after):
        if before.content != after.content:
            await self.__invokeCommand(after)

    async def on_command(self, ctx):
        self.__statcord.command_run(ctx)
