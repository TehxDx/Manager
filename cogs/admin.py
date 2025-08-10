"""
    Admin Commands
"""
import os, datetime, discord, logging
from discord.ext import commands
from discord import app_commands
from lib.embed_build import embed_loader

class Admin(commands.Cog):

    # admin subgroup
    admin = app_commands.Group(name="admin", description="Admin Commands")
    admin_action = app_commands.Group(name="action", description="Kick/Ban/Timeout", parent=admin)
    admin_remove = app_commands.Group(name="remove", description="Ban/Timeout", parent=admin)
    admin_list = app_commands.Group(name="list", description="Ban/Kick List", parent=admin)
    admin_embed = app_commands.Group(name="embed", description="Admin Embeds", parent=admin)

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        # unit map for timeout
        # that way I can limit the if/elif statements and merge it to 1 simple if
        self.unit_map = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks"
        }

    # kick - kicks a user from the guild and adds to the database
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @admin_action.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="The reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        try:
            await user.kick(reason=reason)
            self.database.kick.add_kick(
                user_id=user.id,
                discord_name=user.name,
                guild_id=interaction.guild.id,
                reason=reason,
                kicked_by=interaction.user.id,
            )
            logging.info(f"[+]User {user.name} has been kicked by {interaction.user.name} for reason: {reason}")
            await interaction.response.send_message(f"User {user.mention} has been kicked.", ephemeral=True)
        except discord.Forbidden or discord.NotFound:
            # lets log that we cant kick a user
            logging.error(f"[!] Kick failed for user {user.name}")
            await interaction.response.send_message("I don't have permission to kick this user.", ephemeral=True)

    # ban - bans a user and insert the data to the database
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_action.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        reason="The reason for the ban"
    )
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str):
        try:
            await user.ban(reason=reason)
            self.database.ban.add_ban(
                guild_id=interaction.guild.id,
                user_id=user.id,
                discord_name=user.name,
                banned_by=interaction.user.id,
                reason=reason
            )
            logging.info(f"[+] User {user.name} has been banned by {interaction.user.name} for reason: {reason}")
            await interaction.response.send_message(f"User {user.mention} has been banned.", ephemeral=True)
        except discord.Forbidden or discord.NotFound:
            # lets log that we cant ban the user
            logging.error(f"[!] Ban failed for user {user.name}")
            await interaction.response.send_message("I don't have permission to ban this user.", ephemeral=True)

    # unban - unbans a user and removes them from banned the database
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_remove.command(name="ban", description="Unban a user from the server")
    @app_commands.describe(
        user="Discord ID"
    )
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        try:
            await interaction.guild.unban(user)
            self.database.ban.unban(guild_id=interaction.guild.id, user_id=user.id)
            logging.info(f"User {user.name} has been unbanned by {interaction.user.name}")
            await interaction.response.send_message(f"User {user.mention} has been unbanned.", ephemeral=True)
        except discord.NotFound or discord.Forbidden:
            # lets log it if we can not unban a user
            logging.error(f"Unban failed for user {user.name}")
            await interaction.response.send_message(
                "I either do not have access to the banned users list or the user is not banned.",
                ephemeral=True
            )

    # timeout command, admins who use this command must have moderate_members permissions
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @admin_action.command(name="timeout", description="Timeout a user from the server")
    @app_commands.describe(
        user="The user to timeout",
        duration="The duration of the timeout",
        reason="The reason for the timeout"
    )
    async def timeout(self, interaction: discord.Interaction, user: discord.Member, duration: str, reason: str):
        try:
            # int the time value
            split_value = int(duration[:-1])
            # make sure its lowercase
            split_unit = duration[-1].lower()
            if split_unit in self.unit_map:
                # match split_unit to unit_map for deltatime
                length = datetime.timedelta(**{self.unit_map[split_unit]: split_value})
            else:
                return await interaction.response.send_message(
                    "Invalid unit. Please use one of the following: s, m, h, d, w.", ephemeral=True
                )
            # discord has a 28day api limit on timeouts
            if length > datetime.timedelta(days=28):
                return await interaction.response.send_message(
                    "Timeout duration cannot be longer than 28 days.", ephemeral=True
                )
            # lets make sure its more than 0 seconds too...
            if length <= datetime.timedelta(seconds=0):
                return await interaction.response.send_message(
                    "Timeout duration cannot be less than 1 second.", ephemeral=True
                )
            if length == datetime.timedelta(days=28):
                # because if you put exactly 28 days, the api will kick it out
                length = datetime.timedelta(days=28, seconds=-30)
            # lets convert the timestamp to unix and int it
            unix_timestamp = int((datetime.datetime.now(datetime.timezone.utc) + length).timestamp())
            await user.timeout(length, reason=reason)
            self.database.timeout.add_timeout(
                user_id=user.id,
                discord_name=user.name,
                guild_id=interaction.guild.id,
                reason=reason,
                timeout_by=interaction.user.id,
                timeout_until=unix_timestamp
            )
            logging.info(f"[+] User {user.name} has been timed out by {interaction.user.name} for reason: {reason}")
            return await interaction.response.send_message(
                f"User {user.mention} has been timed out until <t:{unix_timestamp}:F>.",
                ephemeral=True
            )
        except ValueError:
            logging.error(f"[!] Invalid duration: {duration} from {interaction.user.name}")
            return await interaction.response.send_message(
                "Invalid duration. Please use a number followed by a unit.", ephemeral=True
            )
        except discord.Forbidden or discord.NotFound:
            logging.error(f"[!] Timeout failed for user {user.name} from {interaction.user.name}")
            return await interaction.response.send_message(
                "I don't have permission to timeout this user.", ephemeral=True
            )
        # i thought about combining this exception with the above
        # but this provides better logging
        except discord.HTTPException as e:
            logging.error(f"[!] Timeout failed for user {user.name}: {e}")
            return await interaction.response.send_message(
                "An error occurred while trying to timeout this user.", ephemeral=True
            )

    # bans
    # grabs the last 5 banned from the database
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_list.command(name="bans", description="List all banned users")
    async def listbanned(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fetch = self.database.ban.ban_list(guild_id=interaction.guild.id)
        if not fetch:
            return await interaction.followup.send("There is no bans in the database to list.")
        embed = embed_loader(name="bans", file="embeds/core.json")
        for item in fetch:
            try:
                banned_by = self.bot.get_user(item[5])
                embed.add_field(
                    name=f"ID: #{item[0]}",
                    value=f"User Details:\n`{item[3]}` | `{item[2]}`\n"
                          f"Banned By: {banned_by.mention} | `{banned_by.id}`\n"
                          f"Timestamp: <t:{item[6]}:F>\n"
                          f"Reason: ```{item[4]}```",
                          inline=False
                )
            except discord.Forbidden or discord.NotFound:
                pass
            except Exception as e:
                logging.error(f"Failed to list banned users: {e}")
        return await interaction.followup.send(embed=embed)

    # kicked
    # grabs last 5 kicked users from database
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @admin_list.command(name="kicks", description="List all kicked users")
    async def listkicked(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        kicked = self.database.kick.kick_list(guild_id=interaction.guild.id)
        if not kicked:
            return await interaction.followup.send("There is no kicks in the database to list.")
        embed = embed_loader(name="kicks", file="embeds/core.json")
        for item in kicked:
            try:
                kicked_by = self.bot.get_user(item[5])
                embed.add_field(
                    name=f"ID: #{item[0]}",
                    value=f"User Details:\n`{item[2]}` | `{item[1]}`\n"
                          f"Kicked By: {kicked_by.mention} | `{kicked_by.id}`\n"
                          f"Timestamp: <t:{item[6]}:F>\n"
                          f"Reason: ```{item[4]}```",
                    inline=False
                )
            except discord.Forbidden or discord.NotFound:
                pass
            except Exception as e:
                logging.error(f"Failed to list kicked users: {e}")
        return await interaction.followup.send(embed=embed)

    # timeouts
    # grabs the last 5 timeouts from the database
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @admin_list.command(name="timeouts", description="List all timed out users")
    async def listtimeouts(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        timeouts = self.database.timeout.timeout_list(guild_id=interaction.guild.id)
        if not timeouts:
            return await interaction.followup.send("There is no timeouts in the database to list.")
        embed = embed_loader(name="timeouts", file="embeds/core.json")
        for item in timeouts:
            try:
                timeout_by = self.bot.get_user(item[5])
                embed.add_field(
                    name=f"ID: #{item[0]}",
                    value=f"User Details:\n`{item[2]}` | `{item[1]}`\n"
                          f"Timeout By: {timeout_by.mention} | `{timeout_by.id}`\n"
                          f"Timeout Until: <t:{item[6]}:F>\n"
                          f"Timestamp: <t:{item[7]}:F>\n"
                          f"Reason: ```{item[4]}```",
                    inline=False
                )
            except discord.Forbidden or discord.NotFound:
                pass
            except Exception as e:
                logging.error(f"Failed to list timeout users: {e}")
        return await interaction.followup.send(embed=embed)

    # post - embed posting
    # this requires a custom embed to be set in embeds/messages.json
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @admin_embed.command(name="post", description="Create an embed")
    @app_commands.describe(
        name="The name of the embed"
    )
    async def embed(self, interaction: discord.Interaction, name: str, channel: discord.TextChannel = None):
        fetch = embed_loader(name=name, file="embeds/messages.json")
        if fetch:
            if channel:
                await interaction.response.send_message(
                    f"Embed {name} created by {interaction.user.name} in {channel.mention}",
                    ephemeral=True
                )
                return await channel.send(embed=fetch)
            logging.info(f"Embed {name} created by {interaction.user.name}")
            return await interaction.response.send_message(embed=fetch)
        else:
            logging.error(f"Embed {name} not found")
            return await interaction.response.send_message("Embed not found.", ephemeral=True)

    # embed help
    # added a simple help command to creating custom embeds
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @admin_embed.command(name="help", description="Embed Help")
    async def help(self, interaction: discord.Interaction):
        message = ("## Embed Helper\n"
                   "- Locate embeds/messages.json\n"
                   "☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰\n"
                   "```json\n"
                   "{\n"
                   "  \"example\": {\n"
                   "    \"title\": \"Example Embed\",\n"
                   "    \"description\": \"Example Description\",\n"
                   "    \"color\": \"7c2715\"\n"
                   "    \"fields\": [\n"
                   "      {\n"
                   "        \"name\": \"Name\",\n"
                   "        \"value\": \"Value\",\n"
                   "        \"inline\": true\n"
                   "      },\n"
                   "    ],\n"
                   "    \"footer\": {\n"
                   "      \"text\": \"Footer text here\",\n"
                   "      \"icon\": \"https://example.com/example.png\"\n"
                   "    },\n"
                   "    \"thumbnail\": \"https://example.com/example.png\",\n"
                   "    \"image\": \"https://example.com/example.png\"\n"
                   "  }\n"
                   "}```\n"
                   "☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰☰\n"
                   "- Save the above example to the file\n"
                   "- Use the command `/admin embed post example` to post the embed\n")
        await interaction.response.send_message(message, ephemeral=True)

    # purge command to help clean up a channel - limited to 40 but max is 100
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_messages=True)
    @admin.command(name="purge", description="Select between 1 - 40 messages to delete")
    async def purge(self, interaction: discord.Interaction, amount: int):
        await interaction.response.defer(ephemeral=True)
        if not 1 <= amount <= 40:
            await interaction.response.send_message("The amount has to be within 1-40", ephemeral=True)
        purge = await interaction.channel.purge(limit=amount)
        return await interaction.followup.send(f"I purged {len(purge)} message(s)")

    # how to check permissions that the bot needs
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @admin.command(name="permissions", description="Permissions Check for myself")
    async def permissions(self, interaction: discord.Interaction):
        required_perms = {
            "View Channels": interaction.guild.me.guild_permissions.view_channel,
            "Send Messages": interaction.guild.me.guild_permissions.send_messages,
            "Manage Channels": interaction.guild.me.guild_permissions.manage_channels,
            "Kick Members": interaction.guild.me.guild_permissions.kick_members, # important to kick users
            "Ban Members": interaction.guild.me.guild_permissions.ban_members, # important to ban users
            "Moderate Members (Timeout)": interaction.guild.me.guild_permissions.moderate_members, # important to timeout
            "View Audit Log": interaction.guild.me.guild_permissions.view_audit_log, # important to watch audit log to get specific information
            "Create Instant Invite": interaction.guild.me.guild_permissions.create_instant_invite,
            "Manage Roles": interaction.guild.me.guild_permissions.manage_roles
        }

        missing = [name for name, has_perm in required_perms.items() if not has_perm]

        if missing:
            embed = discord.Embed(
                title=":no_entry_sign: Missing Bot Permissions",
                description="\n".join(f"• `{perm}`" for perm in missing),
                color=discord.Color.brand_red() # correction
            )
            embed.set_footer(text="Permission Checker - ManagerBot")
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        return await interaction.response.send_message("All permissions are met.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))

