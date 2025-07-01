import discord
from discord import ButtonStyle, ui
import json
import logging

class TicketClose(discord.ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.database = bot.database

    @ui.button(label="Close Ticket", style=ButtonStyle.red, custom_id="persistent_view:ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # check if the user has administrator permissions
        checks = interaction.user.guild_permissions.administrator
        # need to get the roles the interaction user has
        roles = []
        for role in interaction.user.roles:
            roles.append(role.id)
        # find the specific ticket this channel is tied to
        fetch = self.database.ticket.ticket_search_spec(guild_id=interaction.guild.id, channel_id=interaction.channel.id)
        if fetch:
            # grab the ticket setup data to get roles allowed to close
            ticket_setup = self.database.ticket.ticket_setup_fetch(ticket_id=fetch[4], guild_id=interaction.guild.id)
            ticket_roles = json.loads(ticket_setup[6])
            if set(roles) & set(ticket_roles) or checks:
                guild = self.bot.get_guild(fetch[1])
                channel = guild.get_channel(fetch[3])
                # update the ticket to closed status
                self.database.ticket.ticket_update(
                    guild_id=interaction.guild.id,
                    user_id=fetch[2],
                    channel_id=interaction.channel.id,
                    status=False
                )
                await channel.send("# Closing Ticket...")
                # log that the ticket was closed
                logging.info(f"[-] Ticket #{fetch[0]} has been closed by {interaction.user.name}.")
                return await channel.delete()
            else:
                # if they do not have a matching role, they can not close the ticket
                return await interaction.response.send_message("You do not have access to close this ticket", ephemeral=True)
        return await interaction.response.send_message("I can not close this ticket", ephemeral=True)
