from asyncio import TimeoutError, sleep

from discord import ButtonStyle
from discord.ui import View, button

from other_utils.funcs import errorEmbed, printError


class PageButtons(View):
    def __init__(self, ctx, client, msg, embeds: list, timeout: int=300):
        super().__init__(timeout=timeout)
        self.__ctx = ctx
        self.__client = client
        self.__msg = msg
        self.__embeds = embeds
        self.__page = 1
        self.__allpages = len(self.__embeds)

    async def __edit(self):
        await self.__msg.edit(embed=self.__embeds[self.__page - 1])

    async def interaction_check(self, interaction):
        return interaction.user == self.__ctx.author

    async def on_timeout(self):
        await self.__msg.edit(view=None)

    async def on_error(self, error, item, interaction):
        printError(self.__ctx, error)

    @button(emoji="🗑️", style=ButtonStyle.danger)
    async def delete(self, button, interaction):
        await self.__msg.edit(content="Deleting this message...", embed=None)
        await sleep(1)
        await self.__msg.delete()

    @button(emoji="⏮", style=ButtonStyle.primary)
    async def prev(self, button, interaction):
        if self.__page > 1:
            self.__page -= 1
            await self.__edit()

    @button(emoji="⏭", style=ButtonStyle.primary)
    async def next(self, button, interaction):
        if self.__page < self.__allpages:
            self.__page += 1
            await self.__edit()

    @button(emoji="❓", style=ButtonStyle.secondary)
    async def gotopage(self, button, interaction):
        if self.__allpages > 1:
            mlist = [
                await self.__ctx.send(
                    f"{self.__ctx.author.mention} Which page would you like to go to? (1-{'{:,}'.format(self.__allpages)})"
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
                        if not 1 <= page <= self.__allpages:
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
