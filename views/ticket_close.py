import discord
from discord import ButtonStyle, ui
import logging

class TicketClose(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.database = bot.database

    @ui.button(label="Close Ticket", style=ButtonStyle.red, custom_id="persistent_view:ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        return
