from asyncio import TimeoutError, sleep

from discord import ButtonStyle
from discord.ui import View, button

from other_utils.funcs import errorEmbed, printError


class PageButtons(View):
    def __init__(self, ctx, client, msg, embeds: list, timeout: int=300):
        super().__init__(timeout=timeout)
        self.ctx = ctx
        self.client = client
        self.msg = msg
        self.embeds = embeds
        self.page = 1
        self.allpages = len(self.embeds)

    async def interaction_check(self, interaction):
        return interaction.user == self.ctx.author

    async def on_timeout(self):
        await self.msg.edit(view=None)

    async def on_error(self, error, item, interaction):
        printError(self.ctx, error)

    async def edit(self):
        await self.msg.edit(embed=self.embeds[self.page - 1])

    @button(emoji="🗑️", style=ButtonStyle.danger)
    async def delete(self, button, interaction):
        await self.msg.edit(content="Deleting this message...", embed=None)
        await sleep(1)
        await self.msg.delete()

    @button(emoji="⏮", style=ButtonStyle.primary)
    async def prev(self, button, interaction):
        if self.page > 1:
            self.page -= 1
            await self.edit()

    @button(emoji="⏭", style=ButtonStyle.primary)
    async def next(self, button, interaction):
        if self.page < self.allpages:
            self.page += 1
            await self.edit()

    @button(emoji="❓", style=ButtonStyle.secondary)
    async def gotopage(self, button, interaction):
        if self.allpages > 1:
            await self.edit()
            mlist = [
                await self.ctx.send(
                    f"{self.ctx.author.mention} Which page would you like to go to? (1-{'{:,}'.format(self.allpages)})"
                )
            ]
            while True:
                try:
                    userm = await self.client.wait_for(
                        "message", check=lambda umsg: umsg.author == self.ctx.author
                                                      and umsg.channel == self.ctx.channel, timeout=30
                    )
                    mlist.append(userm)
                    try:
                        page = int(userm.content.replace(",", "").replace(" ", ""))
                        if not 1 <= page <= self.allpages:
                            raise Exception
                        break
                    except:
                        mlist.append(await self.ctx.send(embed=errorEmbed(None, "Invalid page, please try again.")))
                except TimeoutError:
                    page = 1
                    break
            for m in mlist:
                try:
                    await m.delete()
                except:
                    pass
            self.page = page
            await self.edit()
