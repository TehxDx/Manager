"""
    Ticket view button
"""
import discord
from discord.utils import get
from discord import ButtonStyle, ui
import json
import logging
from lib.embed_build import embed_loader
from views.ticket_close import TicketClose

class TicketView(ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.database = bot.database

    @ui.button(label="🎟️ Open a ticket", style=ButtonStyle.green, custom_id="persistent_view:ticket")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        fetch = self.database.ticket.ticket_setup_fetch(message_id=interaction.message.id)
        # check if they have any tickets
        verify = self.database.ticket.ticket_search(guild_id=interaction.guild.id, user_id=interaction.user.id)
        # if they do, lets check them
        if verify:
            for items in verify:
                # if the status shows 1 (True), lets check it
                if items[5] == 1:
                    guild = self.bot.get_guild(items[1])
                    channel = guild.get_channel(items[3])
                    if channel:
                        # if the ticket is open, and channel exist reply to the interaction with the channel
                        return await interaction.response.send_message(f"You already have an active ticket. {channel.mention}", ephemeral=True)
                    else:
                        # if the channel doesn't exist, lets change the status to 0 (False) closing it out
                        self.database.ticket.ticket_update(
                            guild_id=interaction.guild.id,
                            user_id=interaction.user.id,
                            channel_id=items[3],
                            status=False
                        )

        if fetch:
            # discord member
            member = interaction.user
            # get the category
            category = get(interaction.guild.categories, id=fetch[4])
            if not category:
                # did not find the category, and to prevent further issues, deleting the ticket setup from the database
                logging.error(f"[!] Ticket Setup {fetch[0]} could not find the assigned category {fetch[4]} - Deleting ticket setup")
                self.database.ticket.ticket_setup_drop(guild_id=interaction.guild.id, message_id=fetch[4])
                return await interaction.response.send_message("There was an error opening the ticket", ephemeral=True)
            roles = json.loads(fetch[6])
            overwrites = {
                interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False, view_channel=False),
                member: discord.PermissionOverwrite(
                    read_messages=True,
                    send_messages=True,
                    view_channel=True,
                    read_message_history=True
                ),
                interaction.guild.me: discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    embed_links=True
                )
            }
            if roles:
                support_roles = [get(interaction.guild.roles, id=role_id) for role_id in roles]
                support_roles = [role for role in support_roles if role]
                role_string = "".join(f"{role.mention} " for role in support_roles)
                for role in support_roles:
                    overwrites[role] = discord.PermissionOverwrite(
                        read_messages=True,
                        send_messages=True,
                        view_channel=True,
                        read_message_history=True
                    )
            else:
                logging.info(f"[!] Ticket Setup {fetch[0]} could not find the assigned roles.")
                role_string = "**This ticket setup has no roles assigned to it.**"

            create_channel = f"ticket-{interaction.user.name}"
            try:
                view = TicketClose(self.bot)
                embed = embed_loader(name=fetch[7], file="embeds/messages.json")
                new_channel = await interaction.guild.create_text_channel(name=create_channel, category=category, overwrites=overwrites)
                message = await new_channel.send(f"{interaction.message.author.mention}", embed=embed, view=view)
                # ping assigned roles
                await new_channel.send(f"{role_string}")
                # add the ticket to the database
                self.database.ticket.ticket_add(
                    guild_id=interaction.guild.id,
                    user_id=interaction.user.id,
                    channel_id=new_channel.id,
                    ticket_setup=fetch[0],
                    status=True
                )
                logging.info("[+] Ticket Opened Successfully")
                return await interaction.response.send_message("A ticket has been opened!", ephemeral=True)
            except discord.HTTPException or discord.Forbidden as e:
                logging.error(f"[!] Error creating a ticket channel: {e}")
                return await interaction.response.send_message("There was an error opening the ticket.", ephemeral=True)
        else:
            return await interaction.response.send_message(f"{fetch}")