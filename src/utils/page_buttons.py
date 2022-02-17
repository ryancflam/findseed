from asyncio import TimeoutError, sleep

from discord import ButtonStyle, ui

from src.utils.funcs import errorEmbed, printError

DELETE = "🗑️"
PREV = "⏮"
NEXT = "⏭"
GO_TO_PAGE = "❓"


class PageButtons(ui.View):
    def __init__(self, ctx, client, msg, embeds, timeout: int=300):
        super().__init__(timeout=timeout)
        self.__ctx = ctx
        self.__client = client
        self.__msg = msg
        self.__embeds = embeds
        self.__page = 1
        self.__pages = len(self.__embeds)

    async def __edit(self):
        await self.__msg.edit(embed=self.__embeds[self.__page - 1])

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

    @ui.button(emoji=PREV, style=ButtonStyle.primary)
    async def prev(self, _, __):
        if self.__page > 1:
            self.__page -= 1
            await self.__edit()

    @ui.button(emoji=NEXT, style=ButtonStyle.primary)
    async def next(self, _, __):
        if self.__page < self.__pages:
            self.__page += 1
            await self.__edit()

    @ui.button(emoji=GO_TO_PAGE, style=ButtonStyle.secondary)
    async def gotopage(self, _, __):
        if self.__pages > 1:
            mlist = [
                await self.__ctx.send(
                    f"{self.__ctx.author.mention} Which page would you like to go to? (1-{'{:,}'.format(self.__pages)})"
                )
            ]
            while True:
                try:
                    userm = await self.__client.wait_for(
                        "message", check=lambda umsg: umsg.author == self.__ctx.author
                                                      and umsg.channel == self.__ctx.channel, timeout=30
                    )
                    mlist.append(userm)
                    try:
                        page = int(userm.content.replace(",", "").replace(" ", ""))
                        if not 1 <= page <= self.__pages:
                            raise Exception
                        break
                    except:
                        mlist.append(await self.__ctx.send(embed=errorEmbed(None, "Invalid page, please try again.")))
                except TimeoutError:
                    page = 1
                    break
            for m in mlist:
                try:
                    await m.delete()
                except:
                    pass
            self.__page = page
            await self.__edit()
