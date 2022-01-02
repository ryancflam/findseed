# Hidden category

from discord.ext import commands

from other_utils import funcs


class Errors(commands.Cog, name="Errors", description="Error handler category.", command_attrs=dict(hidden=True)):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                embed=funcs.errorEmbed(f"Slow down, {ctx.message.author.name}!",
                                        f"Please try again in {round(error.retry_after, 2)} seconds.")
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.send(
                embed=funcs.errorEmbed("Insufficient privileges!", "Only the bot owner can use this.")
            )
        elif isinstance(error, commands.NoPrivateMessage):
            await ctx.send(
                embed=funcs.errorEmbed(None, "This command can only be used in servers.")
            )
        elif isinstance(error, commands.PrivateMessageOnly):
            await ctx.send(
                embed=funcs.errorEmbed(None, "This command can only be used in DM.")
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send(
                embed=funcs.errorEmbed(
                    "Invalid arguments!", "Correct usage: " + \
                    f"`{self.client.command_prefix}{ctx.command.name} {ctx.command.usage}`"
                ).set_footer(text="Command usage: <> = Required; [] = Optional")
            )
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(
                embed=funcs.errorEmbed(
                    "Insufficient privileges!", "You are missing the following permission(s): " + \
                                                ", ".join(f"`{perm}`" for perm in error.missing_perms)
                )
            )
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(
                embed=funcs.errorEmbed(None, "Bot does not have permission to perform such action.")
            )


def setup(client: commands.Bot):
    client.add_cog(Errors(client))
