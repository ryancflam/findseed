from asyncio import TimeoutError

from discord import ButtonStyle, ui

from src.utils.delete_button import DeleteButton
from src.utils.funcs import errorEmbed

PREV = "⏮"
NEXT = "⏭"
GO_TO_PAGE = "❓"


class PageButtons(DeleteButton):
    def __init__(self, ctx, client, msg, embeds: list, timeout: int=300):
        super().__init__(ctx=ctx, client=client, msg=msg, timeout=timeout)
        self.__embeds = embeds
        self.__page = 1
        self.__pages = len(self.__embeds)

    async def __edit(self):
        await self._getmsg().edit(embed=self.__embeds[self.__page - 1])

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
                await self._getctx().send(
                    f"{self._getctx().author.mention} Which page would you like to go to? (1-{'{:,}'.format(self.__pages)})"
                )
            ]
            while True:
                try:
                    userm = await self._getclient().wait_for(
                        "message", check=lambda umsg: umsg.author == self._getctx().author
                                                      and umsg.channel == self._getctx().channel, timeout=30
                    )
                    mlist.append(userm)
                    try:
                        page = int(userm.content.replace(",", "").replace(" ", ""))
                        if not 1 <= page <= self.__pages:
                            raise Exception
                        break
                    except:
                        mlist.append(await self._getctx().send(embed=errorEmbed(None, "Invalid page, please try again.")))
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
