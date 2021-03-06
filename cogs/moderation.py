from discord import Embed, Member
from discord.ext import commands

from other_utils import funcs


class Moderation(commands.Cog, name="Moderation"):
    def __init__(self, client: commands.Bot):
        self.client = client

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="clear", description="Clears channel messages.", usage="<amount>",
                      aliases=["prune", "purge"])
    @commands.bot_has_permissions(read_message_history=True, manage_messages=True)
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount=""):
        if amount == "":
            e = funcs.errorEmbed(None, "Please enter a value between 1 and 99.")
        else:
            x = int(amount) + 1
            if not 2 <= x <= 100:
                e = funcs.errorEmbed(None, "Please enter a value between 1 and 99.")
            else:
                success, fails = -1, 0
                async for msg in ctx.channel.history(limit=x):
                    try:
                        await msg.delete()
                        success += 1
                    except:
                        fails += 1
                e = Embed(
                    title="Result",
                    description=f"Removed {success} message{'' if success == 1 else 's'} " + \
                                f"with {fails} fail{'' if fails == 1 else 's'}."
                )
        await ctx.send(embed=e)

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="kick", description="Kicks a user from a server.",
                      usage="<@mention> [reason]")
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason=None):
        try:
            await member.kick(reason=reason)
            try:
                await member.send(f"You have been kicked from **{ctx.guild.name}**" + \
                                  f"{'!' if not reason else ' for: `{}`'.format(reason)}")
            except:
                pass
            await ctx.send(f"Successfully kicked user **{member}**" + \
                           f"{'.' if not reason else ' for: `{}`'.format(reason)}")
        except Exception:
            await ctx.send(embed=funcs.errorEmbed(None, "Cannot kick that user."))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="ban", description="Bans a user from a server.",
                      usage="<@mention> [reason]")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason=None):
        try:
            await member.ban(reason=reason)
            try:
                await member.send(f"You have been banned from **{ctx.guild.name}**" + \
                                  f"{'!' if not reason else ' for: `{}`'.format(reason)}")
            except:
                pass
            await ctx.send(f"Successfully banned user **{member}**" + \
                           f"{'.' if not reason else ' for: `{}`'.format(reason)}")
        except Exception:
            await ctx.send(embed=funcs.errorEmbed(None, "Cannot ban that user."))

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="unban", description="Unbans a user on a server.",
                      usage="<username#discriminator>")
    @commands.bot_has_permissions(ban_members=True, manage_guild=True)
    @commands.has_permissions(ban_members=True, manage_guild=True)
    async def unban(self, ctx, *, member=""):
        try:
            bannedusers = await ctx.guild.bans()
            username, discriminator = member.rsplit("#", 1)
            for ban in bannedusers:
                user = ban.user
                if (user.name, user.discriminator) == (username, discriminator):
                    await ctx.guild.unban(user)
                    return await ctx.send(f"Successfully unbanned user **{user}**.")
        except Exception:
            await ctx.send(embed=funcs.errorEmbed(None, "An error occurred. Unknown user?"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="banlist", description="Returns a list of banned users on a server.",
                      aliases=["bans"])
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def banlist(self, ctx):
        bannedusers = await ctx.guild.bans()
        string = "\n".join(
            f"- {ban.user.name}#{ban.user.discriminator}" + \
            f" (Reason: {ban.reason})" for ban in bannedusers
        )
        if string == "":
            string = "None"
        await ctx.send(funcs.formatting(string))


def setup(client: commands.Bot):
    client.add_cog(Moderation(client))
