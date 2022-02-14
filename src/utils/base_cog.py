from discord.ext import commands

from src.bot_instance import BotInstance


class BaseCog(commands.Cog):
    def __init__(self, botInstance: BotInstance, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client = botInstance

    @property
    def name(self):
        return self.qualified_name or type(self).__name__

    @classmethod
    def setup(cls, botInstance):
        botInstance.add_cog(cls(botInstance))
