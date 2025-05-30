"""
    Admin Commands
"""
import discord
from discord.ext import commands
from discord import app_commands

class Admin(commands.Cog):

    # admin subgroup
    admin = app_commands.Group(name="admin", description="Admin Commands")
    admin_commands = app_commands.Group(name="commands", description="Kick/Ban", parent=admin)
    admin_list = app_commands.Group(name="list", description="Ban/Kick List", parent=admin)

    def __init__(self, bot):
        self.bot = bot

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @admin_commands.command(name="kick", description="Kick a user from the server")
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
            await interaction.response.send_message(f"User {user.mention} has been kicked.", ephemeral=True)
        except discord.Forbidden or discord.NotFound:
            await interaction.response.send_message("I don't have permission to kick this user.", ephemeral=True)


    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_commands.command(name="ban", description="Ban a user from the server")
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
            await interaction.response.send_message(f"User {user.mention} has been banned.", ephemeral=True)
        except discord.Forbidden or discord.NotFound:
            await interaction.response.send_message("I don't have permission to ban this user.", ephemeral=True)

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_commands.command(name="unban", description="Unban a user from the server")
    @app_commands.describe(
        user="The user to unban"
    )
    async def unban(self, interaction: discord.Interaction, user: discord.User):
        try:
            banned = self.bot.database.get("banned", [])
            update = [user_list for user_list  in banned if user_list["discord_id"] != user.id]
            self.bot.database["banned"] = update
            await interaction.guild.unban(user)
            await interaction.response.send_message(f"User {user.mention} has been unbanned.", ephemeral=True)
        except discord.NotFound or discord.Forbidden:
            await interaction.response.send_message(
                "I either do not have access to the banned users list or the user is not banned.",
                ephemeral=True
            )

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(ban_members=True)
    @admin_list.command(name="list-banned", description="List all banned users")
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

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(kick_members=True)
    @admin_list.command(name="list-kicked", description="List all kicked users")
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

async def setup(bot):
    await bot.add_cog(Admin(bot))

