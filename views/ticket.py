"""
    Ticket view button
"""
import discord
from discord import ButtonStyle, ui


class TicketView(ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label="🎟️ Open a ticket", style=ButtonStyle.green, custom_id="persistent_view:ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Test")