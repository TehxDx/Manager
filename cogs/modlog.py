"""
    Modlog Cog
"""
import asyncio
import discord
from discord.ext import commands
import logging

class Modlog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.enabled = self.bot.config["modlog"]
        self.channel = self.bot.config["modlog_channel"]

    # channel creation listener
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        if self.enabled:
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
        else:
            return

    # channel deletion listener
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        if self.enabled:
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
        else:
            return

    @commands.Cog.listener()
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        await asyncio.sleep(2)
        try:
            if self.enabled:
                async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
                    if entry.target.id == user.id:
                        moderator = entry.user
                        reason = entry.reason or "No reason provided."

                        mod_channel = self.bot.get_channel(self.channel)
                        if mod_channel:
                            logging.info(f"[Banned] {user.id} in {guild.name}")
                            embed = discord.Embed(
                                title="Member Banned",
                                description=f"**Member:** {user.mention}\n**Moderator:** {moderator.mention}\n**Reason:** {reason}",
                                color=discord.Color.brand_red()
                            )
                            await mod_channel.send(embed=embed)
                        else:
                            logging.error(f"[Banned] Failed to send modlog: channel not found")
                            return
                    return
            else:
               return
        except Exception as e:
            print(f"Failed to send modlog: {e}")
            logging.error(f"Failed to send modlog: {e}")


async def setup(bot):
    await bot.add_cog(Modlog(bot))
