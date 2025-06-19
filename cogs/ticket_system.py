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
import json
from views.ticket import TicketView
from lib.embed_build import embed_loader

class TicketSystem(commands.Cog):

    ticket = app_commands.Group(name="ticket", description="Ticket system")

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database

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
        category="What category is the tickets to be created in?",
        ticket_embed="Ticket Embed to post for new tickets (embeds/messages.json)"
    )
    async def setup(self, interaction: discord.Interaction, embed: str, channel: discord.TextChannel, category: discord.CategoryChannel, ticket_embed: str):
        await interaction.response.defer(ephemeral=True)
        embed = embed_loader(name=embed,  file="embeds/core.json")
        ticket_send_embed = embed_loader(name=ticket_embed, file="embeds/messages.json")
        if embed is None:
            logging.error(f"[!] Could not find {embed} in core.json")
            return await interaction.followup.send(f"Please check the spelling on your embed for the support channel.\n"
                                                   f"{embed} - Not found in `embeds/core.json`")
        if ticket_send_embed is None:
            logging.error(f"[!] Could not find {ticket_embed} in messages.json")
            return await interaction.followup.send(f"Please check the spelling on your embed to send to new tickets.\n"
                                                   f"{ticket_embed} - Not found in `embeds/messages.json`")
        view = TicketView(self.bot)
        message = await channel.send(embed=embed, view=view)
        push = self.database.ticket.ticket_setup(
            guild_id=interaction.guild.id,
            discord_id=interaction.user.id,
            message_id=message.id,
            category=category.id,
            channel=channel.id,
            roles="[]",
            ticket_embed=ticket_embed
        )
        user = self.bot.get_user(push[2]) # get user object
        get_chan = self.bot.get_channel(push[5]) # get channel object
        return await interaction.followup.send(f"# Ticket Setup Complete\n"
                                        f"> Posted embed with button to {channel.mention}\n"
                                        f"> Category that new tickets will be created in: `{category.name}`\n"
                                        f"# Next step\n"
                                        f"> Add what roles can manage the ticket\n"
                                        f"> - /ticket add_roles [id] [role]\n"
                                        f"\u200b\n"
                                        f"> :card_box: Ticket System #**{push[0]}**\n"
                                        f"> :bust_in_silhouette: Created by: {user.mention} | `{push[2]}`\n"
                                        f"> :envelope_with_arrow: Channel: {get_chan.mention} | `{push[5]}`\n"
                                        f"> :white_medium_square: Category for tickets: {category.mention} | `{push[4]}`\n")

    @app_commands.guild_only
    @app_commands.checks.has_permissions(administrator=True)
    @ticket.command(name="add_role", description="Add a role to existing ticket setup")
    @app_commands.describe(ticket_id="Ticket ID", role="Role Name")
    async def add_role(self, interaction: discord.Interaction, ticket_id: int, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        fetch = self.database.ticket.ticket_setup_fetch(guild_id=interaction.guild.id, ticket_id=ticket_id)
        if fetch:
            role_list = json.loads(fetch[6]) # need to convert it from string back to list
            if role.id in role_list: # checking is the role thats trying to be added already exist in the dataset
                return await interaction.followup.send(f"> {role.mention} is already assigned to this ticket.")
            role_list.append(role.id) # if not, add it to the list
            push = self.database.ticket.ticket_setup_role_modifier(
                guild_id=interaction.guild.id,
                ticket_id=ticket_id,
                roles=str(role_list) # convert it back to a string
            )
            role_men_build = json.loads(push[6]) # lets return the list back to the member who executed the command
            mentions = [] # empty list to build on
            for role in role_men_build:
                ld_guild = interaction.guild.get_role(role) # verify all the roles in the list
                if ld_guild:
                    mentions.append(ld_guild.mention) # append to mentions list
                else:
                    mentions.append(f"Role ID: {role} (Deleted)") # if the role no longer exist, append it so they know

            list_mentions = "\n> - ".join(mentions) # build the string to send
            return await interaction.followup.send(
                f"# Role Added Successfully\n"
                f"> Ticket System ID: #**{push[0]}**\n"
                f"> ## Current Role(s) Assigned\n"
                f"> - {list_mentions}"
            )
        else:
            return await interaction.followup.send(f"## Could not ")

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @ticket.command(name="remove_role", description="Remove a role to existing ticket setup")
    @app_commands.describe(ticket_id="Ticket ID", role="Role Name")
    async def remove_role(self, interaction: discord.Interaction, ticket_id: int, role: discord.Role):
        await interaction.response.defer(ephemeral=True)
        fetch = self.database.ticket.ticket_setup_fetch(guild_id=interaction.guild.id, ticket_id=ticket_id)
        if fetch:
            roles = json.loads(fetch[6])
            if role.id in roles:
                roles.remove(role.id)
            push = self.database.ticket.ticket_setup_role_modifier(
                guild_id=interaction.guild.id,
                ticket_id=ticket_id,
                roles=str(roles)
            )
            role_men_build = json.loads(push[6])
            mentions = [] # empty list to build on
            for role in role_men_build:
                ld_guild = interaction.guild.get_role(role) # verify all the roles in the list
                if ld_guild:
                    mentions.append(ld_guild.mention) # append to mentions list
                else:
                    mentions.append(f"Role ID: {role} (Deleted)")
            if mentions:
                list_mentions = "\n> - ".join(mentions)
            else:
                list_mentions = "There is currently no role assigned to this ticket."
            return await interaction.followup.send(
                f"# Role Removed Successfully\n"
                f"> Ticket System ID: #**{push[0]}**\n"
                f"> ## Current Role(s) Assigned\n"
                f"> - {list_mentions}"
            )
        else:
            return await interaction.followup.send(f"# Ticket ID not found")

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @ticket.command(name="list", description="List ticket setups")
    async def list_ticket_setups(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        fetch = self.database.ticket.ticket_setup_fetch(guild_id=interaction.guild.id, fetch_all=True)
        if not fetch:
            return await interaction.followup.send("No ticket setups found.", ephemeral=True)
        embed = discord.Embed(
            title="Current Ticket Setups",
            description="Below is the list of available ticket setup for configurations",
            color=discord.Color.green()
        )
        for items in fetch[:5]: # 5 to reduce rate limiting
            try:
                # this could lead to rate limiting, I reduced the amount to 5 to aid in this
                fetch_channel = interaction.guild.get_channel(items[5])
                await fetch_channel.fetch_message(items[3])

                roles = json.loads(items[6])
                role_string = "\n".join(f"> <@&{role}>" for role in roles) # "mention" roles
                role_count = len(roles) # count roles, not get object so to limit rate limiting.

                embed.add_field(
                    name=f"Ticket Setup ID: #**{items[0]}**",
                    value=f"Ticket Message ID: `{items[3]}`\n"
                          f"Ticket Channel: <#{items[5]}> | `{items[5]}`\n"
                          f"Ticket Category: <#{items[4]}> | `{items[4]}`\n"
                          f"Role Count Assigned: `{role_count}`\n"
                          f"Roles Assigned: \n"
                          f"{role_string}",
                    inline=False
                )
            except discord.HTTPException: # catch the error from fetch_message
                logging.info(f"[!] Ticket Setup ID {items[0]} message doesn't exist, removing")
                self.database.ticket.ticket_setup_drop(guild_id=interaction.guild.id, message_id=items[3]) # delete the ticket setup
        return await interaction.followup.send(embed=embed)

async def setup(bot):
    # I am struggling with this --- lets do this a round-a-bout way
    tick_enabled = os.getenv("TICKET_SYSTEM")
    return_type = tick_enabled is not None and tick_enabled.lower() == 'true'
    if return_type is True:
        logging.info("[Ticket] Ticket System is enabled")
        await bot.add_cog(TicketSystem(bot))
    else:
        logging.info("[Ticket] Ticket system not enabled")
