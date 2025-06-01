"""
    Admin Commands
"""
import datetime

import discord
from discord.ext import commands
from discord import app_commands
import logging

class Admin(commands.Cog):

    # admin subgroup
    admin = app_commands.Group(name="admin", description="Admin Commands")
    admin_action = app_commands.Group(name="action", description="Kick/Ban/Timeout", parent=admin)
    admin_remove = app_commands.Group(name="remove", description="Ban/Timeout", parent=admin)
    admin_list = app_commands.Group(name="list", description="Ban/Kick List", parent=admin)

    def __init__(self, bot):
        self.bot = bot
        # unit map for timeout
        # that way I can limit the if/elif statements and merge it to 1 simple if
        self.unit_map = {
            "s": "seconds",
            "m": "minutes",
            "h": "hours",
            "d": "days",
            "w": "weeks"
        }

    # kick - kicks a user from the guild and adds to lowDB
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @admin_action.command(name="kick", description="Kick a user from the server")
    @app_commands.describe(
        user="The user to kick",
        reason="The reason for the kick"
    )
    async def kick(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        try:
            # insert kicked user into the lowDB
            users = self.bot.database.get("kicked", [])
            insert = {
                "discord_id": user.id,
                "guild_id": interaction.guild.id,
                "reason": reason,
                "kicked_by": interaction.user.id
            }
            users.append(insert)
            self.bot.database["kicked"] = users
            await user.kick(reason=reason)
            logging.info(f"User {user.name} has been kicked by {interaction.user.name} for reason: {reason}")
            await interaction.response.send_message(f"User {user.mention} has been kicked.", ephemeral=True)
        except discord.Forbidden or discord.NotFound:
            # lets log that we cant kick a user
            logging.error(f"Kick failed for user {user.name}")
            await interaction.response.send_message("I don't have permission to kick this user.", ephemeral=True)

    # ban - bans a user and insert the data to the lowDB
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_action.command(name="ban", description="Ban a user from the server")
    @app_commands.describe(
        user="The user to ban",
        reason="The reason for the ban"
    )
    async def ban(self, interaction: discord.Interaction, user: discord.Member, reason: str = None):
        try:
            users = self.bot.database.get("banned", [])
            # insert banned user into the lowDB
            insert = {
                "discord_id": user.id,
                "guild_id": interaction.guild.id,
                "reason": reason,
                "banned_by": interaction.user.id
            }
            users.append(insert)
            self.bot.database["banned"] = users
            await user.ban(reason=reason)
            logging.info(f"User {user.name} has been banned by {interaction.user.name} for reason: {reason}")
            await interaction.response.send_message(f"User {user.mention} has been banned.", ephemeral=True)
        except discord.Forbidden or discord.NotFound:
            # lets log that we cant ban the user
            logging.error(f"Ban failed for user {user.name}")
            await interaction.response.send_message("I don't have permission to ban this user.", ephemeral=True)

    # unban - unbans a user and removes them from banned in lowDB
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_remove.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user="Discord ID"
    )
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        try:
            banned = self.bot.database.get("banned", [])
            update = [user_list for user_list  in banned if user_list["discord_id"] != user.id]
            self.bot.database["banned"] = update
            await interaction.guild.unban(user)
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
            timeouts = self.bot.database.get("timeouts", [])
            # lowDB structure
            insert = {
                "discord_id": user.id,
                "guild_id": interaction.guild.id,
                "reason": reason,
                "timeout_by": interaction.user.id,
                "timeout_until": unix_timestamp
            }
            timeouts.append(insert)
            self.bot.database["timeouts"] = timeouts
            await user.timeout(length, reason=reason)
            logging.info(f"User {user.name} has been timed out by {interaction.user.name} for reason: {reason}")
            return await interaction.response.send_message(
                f"User {user.mention} has been timed out until <t:{unix_timestamp}:F>.",
                ephemeral=True
            )
        except ValueError:
            logging.error(f"Invalid duration: {duration}")
            return await interaction.response.send_message(
                "Invalid duration. Please use a number followed by a unit.", ephemeral=True
            )
        except discord.Forbidden or discord.NotFound:
            logging.error(f"Timeout failed for user {user.name}")
            return await interaction.response.send_message(
                "I don't have permission to timeout this user.", ephemeral=True
            )
        # i thought about combining this exception with the above
        # but this provides better logging
        except discord.HTTPException as e:
            logging.error(f"Timeout failed for user {user.name}: {e}")
            return await interaction.response.send_message(
                "An error occurred while trying to timeout this user.", ephemeral=True
            )

    # bans
    # grabs all the data from a user in banned lowDB
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_list.command(name="bans", description="List all banned users")
    async def listbanned(self, interaction: discord.Interaction):
        banned = self.bot.database.get("banned", [])
        if not banned:
            return await interaction.response.send_message("There are no banned users.", ephemeral=True)
        embed = discord.Embed(
            title="List of Banned Users",
            description="List of all banned users in this server.",
            color=discord.Color.brand_red()
        )
        for user in banned[:20]:
            user_banned = await self.bot.fetch_user(user["discord_id"])
            embed.add_field(name=f"{user_banned.name} | {user_banned.id}", value=f"Reason: {user['reason']}")

        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # kicked
    # grabs all the kicked users from kicked in lowDB
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @admin_list.command(name="kicked", description="List all kicked users")
    async def listkicked(self, interaction: discord.Interaction):
        kicked = self.bot.database.get("kicked", [])
        if not kicked:
            return await interaction.response.send_message("There are no kicked users.", ephemeral=True)
        embed = discord.Embed(
            title="List of Kicked Users",
            description="List of all kicked users in this server.",
            color=discord.Color.yellow()
        )
        for user in kicked[:20]:
            user_kicked = await self.bot.fetch_user(user["discord_id"])
            embed.add_field(name=f"{user_kicked.name} | {user_kicked.id}", value=f"Reason: {user['reason']}")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

    # timeouts
    # grabs all timeouts of users from lowDB
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(moderate_members=True)
    @admin_list.command(name="timeouts", description="List all timed out users")
    async def listtimeouts(self, interaction: discord.Interaction):
        timeouts = self.bot.database.get("timeouts", [])
        if not timeouts:
            return await interaction.response.send_message("There are no timed out users.", ephemeral=True)
        embed = discord.Embed(
            title="List of Timed Out Users",
            description="List of all timed out users in this server.",
            color=discord.Color.orange()
        )
        for user in timeouts[:20]:
            user_timeout = await self.bot.fetch_user(user["discord_id"])
            embed.add_field(name=f"{user_timeout.name} | {user_timeout.id}", value=f"Reason: {user['reason']}")
        return await interaction.response.send_message(embed=embed, ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))

