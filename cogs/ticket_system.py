"""
    Ticket System

    /ticket setup [embed] [channel] [category]
    - [embed]: grabs the embed under [embed] from core.json
    - [channel]: what channel to post said [embed] to
    - [category]: what category to create new tickets in
"""
import os
import logging
import discord
from discord.ext import commands
from discord import app_commands
from views.ticket import TicketView
from lib.embed_build import embed_loader
import datetime

class TicketSystem(commands.Cog):

    ticket = app_commands.Group(name="ticket", description="Ticket system")

    def __init__(self, bot):
        self.bot = bot

    # ticket setup
    # this requires them to identify what embed they want to use from core.json
    # as well, what channel to post it in, and what category to create the ticket channels in
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @app_commands.checks.bot_has_permissions(
        manage_channels=True, # need to ensure it can create channels
        send_messages=True, # reads messages
        embed_links=True, # send embeded links
        manage_permissions=True # this is critical as the bot needs to manage permissions
    )
    @ticket.command(name="setup", description="Setup ticket system")
    @app_commands.describe(
        embed="Embed Name",
        channel="Channel Name",
        category="What category is the tickets to be created in?"
    )
    async def setup(self, interaction: discord.Interaction, embed: str, channel: discord.TextChannel, category: discord.CategoryChannel):
        await interaction.response.defer(ephemeral=True)
        # guild_id, discord_id, message_id, category, channel, roles (empty list), timestamp
        embed = embed_loader(name=embed,  file="embeds/core.json")
        message = await channel.send(embed=embed, view=TicketView())
        push = self.bot.database.setup_ticket(
            guild_id=interaction.guild.id,
            discord_id=interaction.user.id,
            message_id=message.id,
            category=category.id,
            channel=channel.id,
            roles="[]",
            timestamp=int(datetime.datetime.now(datetime.timezone.utc).timestamp()) # unix timestamp
        )
        data = push[0]
        user = self.bot.get_user(data[2])
        get_chan = self.bot.get_channel(data[5])
        get_cat = self.bot.get_channel(data[4])
        await interaction.followup.send(f"# Ticket Setup Complete\n"
                                        f"> Posted embed with button to {channel.mention}\n"
                                        f"> Category that new tickets will be created in: `{category.name}`\n"
                                        f"# Next step\n"
                                        f"> Add what roles can manage the ticket\n"
                                        f"> - /ticket add_roles [id] [role]\n"
                                        f"\u200b\n"
                                        f"> :card_box: Ticket System #: {data[0]}\n"
                                        f"> :bust_in_silhouette: Created by: {user.mention} | `{data[2]}`\n"
                                        f"> :envelope_with_arrow: Channel: {get_chan.mention} | `{data[5]}`\n"
                                        f"> :white_medium_square: Category for tickets: {get_cat} | `{data[4]}`\n")
        return


async def setup(bot):
    # I am struggling with this --- lets do this a round-a-bout way
    tick_enabled = os.getenv("TICKET_SYSTEM")
    return_type = tick_enabled is not None and tick_enabled.lower() == 'true'
    if return_type is True:
        logging.info("[Ticket] Ticket System is enabled")
        await bot.add_cog(TicketSystem(bot))
    else:
        logging.info("[Ticket] Ticket system not enabled")
