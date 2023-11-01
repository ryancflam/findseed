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
        self.__prevButton = self.get_item("prev_button")
        self.__nextButton = self.get_item("next_button")
        self.__gtpButton = self.get_item("gtp_button")
        self.__prevButton.disabled = True
        if self.__pages == 1:
            self.__nextButton.disabled = True
            self.__gtpButton.disabled = True

    async def __edit(self, interaction):
        if self.__page == 1:
            self.__prevButton.disabled = True
        elif self.__page > 1:
            self.__prevButton.disabled = False
        if self.__page == self.__pages:
            self.__nextButton.disabled = True
        elif self.__page < self.__pages:
            self.__nextButton.disabled = False
        await self._getmsg().edit(embed=self.__embeds[self.__page - 1], view=self)
        await interaction.response.defer()

    @ui.button(emoji=PREV, style=ButtonStyle.primary, custom_id="prev_button")
    async def prev(self, _, interaction):
        self.__page -= 1
        await self.__edit(interaction)

    @ui.button(emoji=NEXT, style=ButtonStyle.primary, custom_id="next_button")
    async def next(self, _, interaction):
        self.__page += 1
        await self.__edit(interaction)

    @ui.button(emoji=GO_TO_PAGE, style=ButtonStyle.secondary, custom_id="gtp_button")
    async def gotopage(self, _, interaction):
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
        await self.__edit(interaction)
