# Hidden category

from discord.ext import commands

from src.utils import funcs
from src.utils.base_cog import BaseCog


class ErrorHandling(BaseCog, name="Error Handling", description="A cog for handling errors.", command_attrs=dict(hidden=True)):
    def __init__(self, botInstance, *args, **kwargs):
        super().__init__(botInstance, *args, **kwargs)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id in (await funcs.readJson("data/whitelist.json"))["users"]:
                ctx.command.reset_cooldown(ctx)
                return await self.client.process_commands(ctx.message)
            retry = round(error.retry_after, 2)
            await ctx.reply(
                embed=funcs.errorEmbed(f"Slow down, {ctx.message.author.name}!",
                                       f"Please try again in {retry} second{'' if retry == 1 else 's'}.")
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.reply(
                embed=funcs.errorEmbed("Insufficient privileges!", "Only the bot owner can use this.")
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.reply(
                embed=funcs.errorEmbed(None, "This command can only be used in servers.")
            )
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.reply(
                embed=funcs.errorEmbed(None, "This command can only be used in DM.")
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.reply(
                embed=funcs.errorEmbed(
                    "Invalid arguments!", "Correct usage: " +
                    f"`{self.client.command_prefix}{ctx.command.name} {ctx.command.usage}`"
                ).set_footer(text="Command usage: <> = Required; [] = Optional")
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.reply(
                embed=funcs.errorEmbed(
                    "Insufficient privileges!",
                    "You are missing the following permission(s): " +
                    ", ".join(f"`{perm}`" for perm in sorted(error.missing_permissions))
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.reply(
                embed=funcs.errorEmbed(
                    "Insufficient privileges!",
                    f"{self.client.user.name} is missing the following permission(s): " +
                    ", ".join(f"`{perm}`" for perm in sorted(error.missing_permissions))
                )
            )


if __name__ != "__main__":
    setup = ErrorHandling.setup
