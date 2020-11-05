from discord.ext import commands

import funcs


class Errors(commands.Cog, name="Errors"):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.channel.send(
                embed=funcs.errorEmbed(f"Slow down, {ctx.message.author.name}!",
                                        f"Please try again in {round(error.retry_after, 2)} seconds.")
            )
        elif isinstance(error, commands.NotOwner):
            await ctx.channel.send(
                embed=funcs.errorEmbed("Insufficient privileges!", "Only the bot owner can use this.")
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.channel.send(
                embed=funcs.errorEmbed("Invalid arguments!", "Correct usage: " + \
                                       f"`{self.client.command_prefix}{ctx.command.name} {ctx.command.usage}`")
            )


def setup(client):
    client.add_cog(Errors(client))
