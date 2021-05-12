import asyncio
from os import listdir

from discord import Activity, Intents
from discord.ext import commands

from other_utils.funcs import userNotBlacklisted, getRequest


class Bot(commands.Bot):
    def __init__(self, loop: asyncio.AbstractEventLoop, prefix: str, **args):
        super().__init__(
            command_prefix=prefix,
            intents=Intents.all(),
            case_insensitive=True
        )
        self.__loop = loop
        self.__path = args.get("path")
        self.__token = args.get("token")
        self.__activityName = args.get("activity")["name"]
        self.__activityType = args.get("activity")["type"]
        self.__status = args.get("activity")["status"]
        self.remove_command("help")

    def startup(self):
        for cog in listdir(f"{self.__path}/cogs"):
            if cog.endswith(".py"):
                self.load_extension(f"cogs.{cog[:-3]}")
                print(f"Loaded cog: {cog[:-3]}")
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
        await self.change_presence(
            activity=Activity(
                name=name,
                type=self.__activityType
            ),
            status=self.__status
        )

    async def on_ready(self):
        print(f"Logged in as: {self.user}")
        if self.__activityName.casefold() == "bitcoin":
            await self.loop.create_task(self.bitcoin())
        else:
            await self.presence(self.__activityName)

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
        if (await self.get_context(message)).valid and not self.is_ready() \
                and userNotBlacklisted(self, message):
            return await message.channel.send(
                f"{self.user.name} is not ready yet, please wait!"
            )
        if self.is_ready() and userNotBlacklisted(self, message):
            while message.content.startswith(f"{self.command_prefix} "):
                message.content = message.content.replace(
                    f"{self.command_prefix} ", f"{self.command_prefix}", 1
                )
            await self.process_commands(message)
