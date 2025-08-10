"""
    Modlog Cog
"""
import discord, logging, functools, os
from discord.ext import commands
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
            if hasattr(arg, "guild") and isinstance(arg.guild, discord.Guild):
                guild = arg.guild
                break

        if not guild:
            # keep seeing this warning fire, however, after alot of probing, I noticed it was only firing when a
            # ephemeral event happened. so you will see this warning message, anytime the bot sends a ephemeral because
            # it fires on_message_edit without the guild details in the payload. will most likely remove later.
            logging.warning(f"[ModLog] No guild found for event '{func.__name__}' | Most likely a ephemeral event. [IGNORE]")
            return

        if guild.id != self.guild:
            return
        return await func(self, *args, **kwargs)
    return wrapper

class Modlog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.config["modlog_channel"]
        self.guild = self.bot.config["modlog_guild"]

    # channel creation listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_channel_create(self, channel: discord.abc.GuildChannel):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Channel Created] {channel.id} created in {channel.guild.name}")
            embed = discord.Embed(
                title="Channel Created",
                description=f"A new channel has been created:\n"
                            f"**Name**: {channel.name}\n"
                            f"**ID**: {channel.id}\n"
                            f"**Type**: {channel.type}",
                color=discord.Color.brand_green()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Channel Created] Failed to send modlog: channel not found")

    # channel deletion listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Channel Deleted] {channel.id} deleted in {channel.guild.name}")
            embed = discord.Embed(
                title="Channel Deleted",
                description=f"A channel has been deleted:\n"
                            f"**Name**: {channel.name}\n"
                            f"**ID**: {channel.id}\n"
                            f"**Type**: {channel.type}",
                color=discord.Color.brand_red()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Channel Deleted] Failed to send modlog: channel not found")

    # channel update listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_channel_update(self, before: discord.abc.GuildChannel, after: discord.abc.GuildChannel):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Channel Updated] {before.id} updated in {before.guild.name}")
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

    # role creation listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_role_create(self, role: discord.Role):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Role Created] {role.id} created in {role.guild.name}")
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
                            f"**Created At**: <t:{unix_time}:R>",
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
                        value="\n".join(f":green_square: `{perm}`" for perm in added), # this adds a green square for each added perm
                        inline=False
                    )
                if removed:
                    embed.add_field(
                        name="Removed Permissions",
                        value="\n".join(f":red_square: `{perm}`" for perm in removed), # this adds a red square for each removed perm
                    )

            if len(embed.fields) > 0:
                await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Role Updated] Failed to send modlog: channel not found")

    # role deletion listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_guild_role_delete(self, role: discord.Role):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Role Deleted] {role.id} deleted in {role.guild.name}")
            embed = discord.Embed(
                title="Role Deleted",
                description=f"**Role Deleted**\n"
                            f"**Name**: {role.name}\n"
                            f"**Role ID**: {role.id}",
                color=discord.Color.brand_red()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Role Deleted] Failed to send modlog: channel not found")

    # member update listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            embed = discord.Embed(
                title="Member Updated",
                description=f"A member has been updated\n"
                            f"\u200b \n"
                            f"Member: {after.mention}",
                color=discord.Color.yellow()
            )

            if before.nick != after.nick:
                embed.add_field(
                    name="Nickname Changed",
                    value=f"`{before.nick}` → `{after.nick}`", # if a nick name doesnt exist, it shows none... I need to fix
                    inline=False
                )

            if before.roles != after.roles:
                # compare roles to catch changes
                added_roles = set(after.roles) - set(before.roles)
                removed_roles = set(before.roles) - set(after.roles)

                if added_roles:
                    embed.add_field(
                        name="Roles Added",
                        value="\n".join(f":green_square: {role.mention}" for role in added_roles), # adds a green square for each new role added
                        inline=False
                    )
                if removed_roles:
                    embed.add_field(
                        name="Roles Removed",
                        value="\n".join(f":red_square: {role.mention}" for role in removed_roles), # adds a red square for each role removed
                        inline=False
                    )

            if len(embed.fields) > 0:
                await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Member Updated] Failed to send modlog: channel not found")

    # member join listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_member_join(self, member: discord.Member):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Member Joined] {member.id} joined {member.guild.name}")
            unix_time = int(member.created_at.timestamp())
            joined_time = int(member.joined_at.timestamp())
            embed = discord.Embed(
                title="Member Joined",
                description=f"**Member**: {member.mention}\n"
                            f"**Member ID**: `{member.id}`\n"
                            f"**Account Created**: <t:{unix_time}:R>\n"
                            f"**Joined Server**: <t:{joined_time}:R>\n",
                color=discord.Color.green()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Member Joined] Failed to send modlog: channel not found")

    # member leave listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_member_remove(self, member: discord.Member):
        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Member Left] {member.id} left {member.guild.name}")
            unix_time = int(datetime.now().timestamp())
            embed = discord.Embed(
                title="Member Left",
                description=f"**Member**: {member.mention}\n"
                            f"**Member ID**: `{member.id}`\n"
                            f"**Left Server**: <t:{unix_time}:R>\n",
                color=discord.Color.brand_red()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Member Left] Failed to send modlog: channel not found")

    # member ban listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_member_ban(self, guild: discord.Guild, user: discord.User):
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.ban):
            # who banned the user
            if entry.target.id == user.id:
                moderator = entry.user
                reason = entry.reason or "No reason provided."

                mod_channel = self.bot.get_channel(self.channel)
                if mod_channel:
                    logging.info(f"[Banned] {user.id} in {guild.name}")
                    embed = discord.Embed(
                        title="Member Banned",
                        description=f"**Member**: {user.mention}\n"
                                    f"**Banned By**: {moderator.mention} | `{moderator.id}`\n"
                                    f"**Reason**: {reason}",
                        color=discord.Color.brand_red()
                    )
                    await mod_channel.send(embed=embed)
                else:
                    logging.error(f"[Banned] Failed to send modlog: channel not found")

    # member unban listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_member_unban(self, guild: discord.Guild, user: discord.User):
        mod_channel = self.bot.get_channel(self.channel)
        async for entry in guild.audit_logs(limit=1, action=discord.AuditLogAction.unban):
            if entry.target.id == user.id:
                # who unbanned the user
                moderator = entry.user
                if mod_channel:
                    logging.info(f"[Unbanned] {user.id} in {guild.name}")
                    embed = discord.Embed(
                        title="Member Unbanned",
                        description=f"**Member**: {user.mention}\n"
                                    f"**Unbanned By**: {moderator.mention} | `{moderator.id}`",
                        color=discord.Color.green()
                    )
                    await mod_channel.send(embed=embed)
                else:
                    logging.error(f"[Unbanned] Failed to send modlog: channel not found")

    # now lets watch other audit log entries
    @commands.Cog.listener()
    @modlog_verify
    async def on_audit_log_entry_create(self, entry: discord.AuditLogEntry):
        """
            Placeholder for future audit log entries

            Plans - Kicks, and timeouts, but I need to figure out what else I can pull
        """
        return

    # message deletes
    @commands.Cog.listener()
    @modlog_verify
    async def on_message_delete(self, message: discord.Message):
        # no need to log the bot
        if message.author.bot:
            return

        mod_channel = self.bot.get_channel(self.channel)
        if mod_channel:
            logging.info(f"[Message Deleted] {message.id} deleted in {message.guild.name}")
            embed = discord.Embed(
                title="Message Deleted",
                description=f"**Message Deleted**\n"
                            f"**Message ID**: `{message.id}`\n"
                            f"**Message Author**: {message.author.mention} | `{message.author.id}`\n"
                            f"**Message Channel**: {message.channel.mention}\n"
                            f"\u200b \n"
                            f"**Message Content**:\n"
                            f"```{message.content}```", # what they deleted
                color=discord.Color.red()
            )
            await mod_channel.send(embed=embed)
        else:
            logging.error(f"[Message Deleted] Failed to send modlog: channel not found")

    # message edit listener
    @commands.Cog.listener()
    @modlog_verify
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        # ignore the bot
        if before.author.bot:
            return

        if before.content != after.content:
            mod_channel = self.bot.get_channel(self.channel)
            if mod_channel:
                logging.info(f"[Message Edited] {before.id} edited in {before.guild.name}")
                embed = discord.Embed(
                    title="Message Edited",
                    description=f"**Message Edited**\n"
                                f"**Message ID**: `{before.id}`\n"
                                f"**Message Author**: {before.author.mention} | `{before.author.id}`\n"
                                f"**Message Channel**: {before.channel.mention}\n"
                                f"\u200b \n"
                                f"**Before**:\n"
                                f"```{before.content}```\n" # what was the content before
                                f"\u200b \n"
                                f"**After**:\n"
                                f"```{after.content}```", # the new content now
                    color=discord.Color.yellow()
                )
                await mod_channel.send(embed=embed)
            else:
                logging.error(f"[Message Edited] Failed to send modlog: channel not found")


async def setup(bot):
    # I am struggling with this --- lets do this a round-a-bout way
    mod_enabled = os.getenv("MOD_ENABLED")
    return_type = mod_enabled is not None and mod_enabled.lower() == 'true'
    if return_type is True:
        logging.info("[ModLog] Logging is enabled")
        await bot.add_cog(Modlog(bot))
    else:
        logging.info("Modlog is disabled")
