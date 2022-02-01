from datetime import timedelta

from discord import Embed, Member
from discord.ext import commands

from other_utils import funcs


class Moderation(commands.Cog, name="Moderation", description="Simple moderation and member-management commands for server staff."):
    def __init__(self, botInstance):
        self.client = botInstance

    @commands.cooldown(1, 10, commands.BucketType.user)
    @commands.command(name="clear", description="Clears channel messages.", usage="<amount>", aliases=["prune", "purge"])
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

    @commands.command(name="timeout", usage='<@mention> [Xm/h/d (replace X with number of minutes/hours/days)] [reason]',
                      description="Times out a user in your server. If the user already has a time out, this replaces it. " +
                                  "The default time out is one minute.", aliases=["mute"])
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def timeout(self, ctx, member: Member, minutes="1", *, reason=None):
        try:
            if member == self.client.user:
                return await ctx.reply(embed=funcs.errorEmbed(None, "I don't want to time out myself, so I won't do it."))
            if member == ctx.author:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Why would you do that?"))
            try:
                minutes = float(minutes)
            except:
                try:
                    if minutes.casefold().endswith("h"):
                        minutes = float(minutes[:-1]) * 60
                    elif minutes.casefold().endswith("d"):
                        minutes = float(minutes[:-1]) * 1440
                    elif minutes.casefold().endswith("m"):
                        minutes = float(minutes[:-1])
                    else:
                        raise Exception
                except:
                    return await ctx.reply(embed=funcs.errorEmbed(None, f"Invalid input: `{minutes}`"))
            await member.timeout_for(duration=timedelta(minutes=minutes), reason=reason)
            try:
                await member.send(f"You have been timed out in **{ctx.guild.name}** for {funcs.removeDotZero(minutes)} " +
                                  f"minute{'' if minutes == 1 else 's'}" +
                                  f"{'!' if not reason else ' for: `{}`'.format(reason)}")
            except:
                pass
            await ctx.reply(f"Successfully timed out user **{member}** for {funcs.removeDotZero(minutes)} " +
                            f"minute{'' if minutes == 1 else 's'}" +
                            f"{'.' if not reason else ' for: `{}`'.format(reason)}")
        except Exception:
            await ctx.reply(embed=funcs.errorEmbed(None, "Cannot time out that user."))

    @commands.command(name="untimeout", description="Removes the time out for a user in your server.",
                      usage="<@mention>", aliases=["unmute"])
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def untimeout(self, ctx, member: Member):
        if member.timed_out:
            await member.remove_timeout()
            return await ctx.reply(f"Successfully removed time out for **{member}**.")
        await ctx.reply(embed=funcs.errorEmbed(None, "That user is not timed out."))

    @commands.command(name="kick", description="Kicks a user from your server.", usage="<@mention> [reason]")
    @commands.bot_has_permissions(kick_members=True)
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: Member, *, reason=None):
        try:
            if member == self.client.user:
                return await ctx.reply(embed=funcs.errorEmbed(None, "I don't want to kick myself, so I won't do it."))
            if member == ctx.author:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Why would you do that?"))
            await member.kick(reason=reason)
            try:
                await member.send(f"You have been kicked from **{ctx.guild.name}**" + \
                                  f"{'!' if not reason else ' for: `{}`'.format(reason)}")
            except:
                pass
            await ctx.reply(f"Successfully kicked user **{member}**" + \
                           f"{'.' if not reason else ' for: `{}`'.format(reason)}")
        except Exception:
            await ctx.reply(embed=funcs.errorEmbed(None, "Cannot kick that user."))

    @commands.command(name="ban", description="Bans a user from your server.", usage="<@mention> [reason]")
    @commands.bot_has_permissions(ban_members=True)
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: Member, *, reason=None):
        try:
            if member == self.client.user:
                return await ctx.reply(embed=funcs.errorEmbed(None, "I don't want to ban myself, so I won't do it."))
            if member == ctx.author:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Why would you do that?"))
            await member.ban(reason=reason)
            try:
                await member.send(f"You have been banned from **{ctx.guild.name}**" + \
                                  f"{'!' if not reason else ' for: `{}`'.format(reason)}")
            except:
                pass
            await ctx.reply(f"Successfully banned user **{member}**" + \
                           f"{'.' if not reason else ' for: `{}`'.format(reason)}")
        except Exception:
            await ctx.reply(embed=funcs.errorEmbed(None, "Cannot ban that user."))

    @commands.command(name="warn", description="Sends a user in your server a warning.", usage="<@mention> [reason]",
                      aliases=["warning"])
    @commands.bot_has_permissions(moderate_members=True)
    @commands.has_permissions(moderate_members=True)
    async def warn(self, ctx, member: Member, *, reason=None):
        try:
            if member.bot:
                return await ctx.reply(embed=funcs.errorEmbed(None, "That user is a bot."))
            if member == ctx.author:
                return await ctx.reply(embed=funcs.errorEmbed(None, "Why would you do that?"))
            if member == member.guild.owner:
                return await ctx.reply(embed=funcs.errorEmbed(None, "That user is the owner!"))
            await member.send(f"You have received a warning in **{ctx.guild.name}**" + \
                              f"{'!' if not reason else ' for: `{}`'.format(reason)}")
            await ctx.reply(f"Successfully sent a warning to **{member}**" + \
                            f"{'.' if not reason else ' for: `{}`'.format(reason)}")
        except Exception:
            await ctx.reply(embed=funcs.errorEmbed(None, "Cannot warn that user; perhaps they have DMs disabled."))

    @commands.command(name="unban", description="Unbans a user in your server. Use the `banlist` command for the server banlist.",
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
                    return await ctx.reply(f"Successfully unbanned user **{user}**.")
        except Exception:
            await ctx.reply(embed=funcs.errorEmbed(None, "An error occurred. Unknown user?"))

    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(name="banlist", description="Returns a list of banned users in your server.", aliases=["bans", "bannedusers"])
    @commands.bot_has_permissions(manage_guild=True)
    @commands.has_permissions(manage_guild=True)
    async def banlist(self, ctx):
        bannedusers = await ctx.guild.bans()
        string = "\n".join(
            f"- {ban.user.name}#{ban.user.discriminator}" + \
            f" (Reason: {ban.reason})" for ban in bannedusers
        )
        string = string or "None"
        await ctx.reply(funcs.formatting(string))


def setup(botInstance):
    botInstance.add_cog(Moderation(botInstance))
