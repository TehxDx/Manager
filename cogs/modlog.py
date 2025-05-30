"""
    Modlog Cog
"""
import asyncio
import discord
from discord.ext import commands
import logging
import functools
from datetime import datetime

# was looking for a solution, so code wasnt repetitive, found this on stackoverflow and adjusted to my needs.
# https://stackoverflow.com/questions/739654/how-to-make-function-decorators-with-optional-arguments/739680#739680
def modlog_verify(func):
    @functools.wraps(func)
    async def wrapper(self, *args, **kwargs):
        guild = None
        for arg in args:
            if isinstance(arg, discord.Guild):
                guild = arg
                break
            if hasattr(arg, "guild"):
                guild = arg.guild
                break
        if not guild:
            logging.warning("[ModLog] No guild found in event args")
            return None

        if not self.enabled or guild.id != self.guild:
            return None

        return await func(self, *args, **kwargs)
    return wrapper

class Modlog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.enabled = self.bot.config["modlog"]
        self.channel = self.bot.config["modlog_channel"]
        self.guild = self.bot.config["modlog_guild"]

    # channel creation listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            embed = discord.Embed(
                title="Channel Created",
                description=f"A new channel has been created:\n"
                            f"**Name**: {channel.name}\n"
                            f"**ID**: {channel.id}\n"
                            f"**Type**: {channel.type}\n",
                color=discord.Color.brand_green()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Channel Created] Failed to send modlog: channel not found")
            return

    # channel deletion listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            embed = discord.Embed(
                title="Channel Deleted",
                description=f"A channel has been deleted:\n"
                            f"**Name**: {channel.name}\n"
                            f"**ID**: {channel.id}\n"
                            f"**Type**: {channel.type}\n",
                color=discord.Color.brand_red()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Channel Deleted] Failed to send modlog: channel not found")
            return

    # channel update listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            embed = discord.Embed(
                title="Channel Updated",
                description="A channel has been updated",
                color=discord.Color.yellow()
            )
            if before.name != after.name:
                embed.add_field(name="Name", value=f"**Before**: {before.name}\n**After**: {after.name}")
            if before.category != after.category:
                embed.add_field(name="Category", value=f"**Before**: {before.category}\n**After**: {after.category}")
            if before.overwrites != after.overwrites:
                embed.add_field(name="Overwrites", value="Permission has been changed.")
            if len(embed.fields) > 0:
                await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Channel Updated] Failed to send modlog: channel not found")
            return

    # role creation listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_role_create(self, role: discord.Role):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            unix_time = int(role.created_at.timestamp())
            embed = discord.Embed(
                title="Role Created",
                description=f"A new role has been created:\n"
                            f"\u200b \n" # empty space and line break
                            f"**Name**: {role.name}\n"
                            f"**Mention**: {role.mention}\n"
                            f"**Mentionable**: {role.mentionable}\n"
                            f"\u200b \n" # empty space and line break
                            f"**ID**: {role.id}\n"
                            f"**Color**: {role.color}\n"
                            f"**Hoisted**: {role.hoist}\n"
                            f"**Position**: {role.position}\n"
                            f"**Managed**: {role.managed}\n"
                            f"**Created At**: <t:{unix_time}:R>\n",
                color=discord.Color.brand_green()
            )
            await mod_channel.send(embed=embed)

    #role update listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_role_update(self, before: discord.Role, after: discord.Role):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            embed = discord.Embed(
                title="Role Updated",
                description=f"{before.mention} role has been updated",
                color=discord.Color.yellow()
            )
            if before.name != after.name:
                embed.add_field(
                    name="Name Changed",
                    value=f"**Before**: {before.name}\n"
                          f"**After**: {after.name}",
                    inline=False
                )
            if before.permissions != after.permissions:
                old_perms = [perm for perm, val in before.permissions if val]
                new_perms = [perm for perm, val in after.permissions if val]

                # lets compare the changes
                added = set(new_perms) - set(old_perms)
                removed = set(old_perms) - set(new_perms)

                # works as intended, lets make it alittle more visually appealing
                if added:
                    embed.add_field(
                        name="Added Permissions",
                        value="\n".join(f":green_square: `{added}`"),
                        inline=False
                    )
                if removed:
                    embed.add_field(
                        name="Removed Permissions",
                        value="\n".join(f":red_square: `{removed}`"),
                    )

            if len(embed.fields) > 0:
                await mod_channel.send(embed=embed)

    @commands.Cog.listener()
    @modlog_verify
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        # waiting for audit log to update
        await asyncio.sleep(2)
        try:
            async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                if entry.target.id == user.id:
                    moderator = entry.user
                    reason = entry.reason or "No reason provided."

                    mod_channel = self.bot.get_channel(self.channel)
                    if mod_channel:
                        logging.info(f"[Banned] {user.id} in {guild.name}")
                        embed = discord.Embed(
                            title="Member Banned",
                            description=f"**Member**: {user.mention}\n**Moderator**: {moderator.mention}\n**Reason**: {reason}",
                            color=discord.Color.brand_red()
                        )
                        await mod_channel.send(embed=embed)
                    else:
                        logging.error(f"[Banned] Failed to send modlog: channel not found")
                        return
                return
        except Exception as e:
            print(f"Failed to send modlog: {e}")
            logging.error(f"Failed to send modlog: {e}")


async def setup(bot):
    await bot.add_cog(Modlog(bot))
