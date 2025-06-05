"""
    Ticket System
"""
import discord
from discord.ext import commands
from discord import app_commands

class TicketSystem(commands.Cog):

    ticket = app_commands.Group(name="ticket", description="Ticket system")

    def __init__(self, bot):
        self.bot = bot

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @ticket.command(name="setup", description="Setup ticket system")
    @app_commands.describe(
        embed="Embed Name",
        channel="Channel Name"
    )
    async def setup(self, interaction: discord.Interaction, embed: str, channel: discord.TextChannel):
        await interaction.response.defer()
        return
