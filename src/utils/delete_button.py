from asyncio import sleep

from discord import ButtonStyle, ui

from src.utils.funcs import printError

DELETE = "🗑️"


class DeleteButton(ui.View):
    def __init__(self, ctx, client, msg, timeout: int=300):
        super().__init__(timeout=timeout)
        self.__ctx = ctx
        self.__client = client
        self.__msg = msg

    def _getctx(self):
        return self.__ctx

    def _getclient(self):
        return self.__client

    def _getmsg(self):
        return self.__msg

    async def interaction_check(self, interaction):
        return interaction.user == self.__ctx.author

    async def on_timeout(self):
        await self.__msg.edit(view=None)

    async def on_error(self, error, _, __):
        printError(self.__ctx, error)

    @ui.button(emoji=DELETE, style=ButtonStyle.danger)
    async def delete(self, _, __):
        await self.__msg.edit(content="Deleting this message...", embed=None, view=None)
        await sleep(1)
        await self.__msg.delete()
