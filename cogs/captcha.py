"""
    Captcha Verification System
"""
import discord, os, logging
from discord.ext import commands
from discord import app_commands
from lib.embed_build import embed_loader
from views.captcha_button import CaptchaButton

class Captcha(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.database = bot.database
        self.verify_channel = os.getenv("CAPTCHA_CHANNEL")

    captcha = app_commands.Group(name="captcha", description="Captcha verification system")
    setup = app_commands.Group(name="setup", description="Setup captcha", parent=captcha)

    @app_commands.guild_only()
    @app_commands.checks.has_permissions(administrator=True)
    @setup.command(name="post", description="Enable captcha verification system")
    async def post(self, interaction: discord.Interaction):
        guild = interaction.guild
        channel = guild.get_channel(int(self.verify_channel))
        embed = embed_loader(name="captcha", file="embeds/core.json")
        if embed:
            try:
                view = CaptchaButton(bot=self)
                await channel.send(embed=embed, view=view)
                await interaction.response.send_message("I've posted it", ephemeral=True)
            except discord.Forbidden:
                logging.info(f"[!][Captcha] I do not have permissions to post in {channel.name}")
                return
            except discord.NotFound:
                logging.info(f"[!][Captcha] {channel.name} not found, check your .env settings")

    # create a listener for the DM
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        if message.author.bot or message.guild:
            return

        # check if the user is in the self.pending_captcha
        pending = self.bot.pending_captcha.get(message.author.id)

        # if they aren't, ignore their DM
        if not pending:
            return

        # if found lets strip, and capitalize the code they send
        if message.content.strip().upper() == pending["code"]: # if code matches, then lets role them
            guild = self.bot.get_guild(pending["guild_id"])
            member = guild.get_member(message.author.id)
            role = guild.get_role(pending["role_id"])

            if member and role:
                await member.add_roles(role) # added the role
                await message.channel.send(f":white_check_mark: You have been verified!") # send the message to let them know
                del self.bot.pending_captcha[message.author.id] # removes them from the self.pending_captcha
                return
            else:
                logging.error(f"[!][Captcha] Could not verify {message.author.name}'s captcha.")
                return await message.channel.send("There was an internal error, please contact support.")
        else:
            return await message.channel.send("Incorrect code! Please try again.")

async def setup(bot):
    # I am struggling with this --- lets do this a round-a-bout way
    tick_enabled = os.getenv("CAPTCHA_SYSTEM")
    return_type = tick_enabled is not None and tick_enabled.lower() == 'true'
    if return_type is True:
        logging.info("[Captcha] Captcha verification system enabled")
        await bot.add_cog(Captcha(bot))
    else:
        logging.info("[Captcha] Captcha verification system disabled")