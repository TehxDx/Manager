"""
    Captcha button
"""
import discord
from discord import ButtonStyle, ui
import os, io, string, random
from PIL import Image, ImageDraw, ImageFont
import logging

class CaptchaButton(ui.View):

    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.captcha_role = int(os.getenv("CAPTCHA_ROLE"))

    @ui.button(label="👤 Verify Me", style=ButtonStyle.green, custom_id="persistent_view:captcha")
    async def captcha(self, interaction: discord.Interaction, button: ui.Button):
        guild = interaction.guild
        member = guild.get_member(interaction.user.id)
        role = guild.get_role(self.captcha_role)

        # if the role doesn't exist, let them know
        if not role:
            logging.error(f"[!] [Captcha Button] Role not found {self.captcha_role}")
            return await interaction.response.send_message(":warning: This role does not exist, please contact support.", ephemeral=True)

        # check if the user has the role
        if role in member.roles:
            logging.info(f"[-] [Captcha Button] {interaction.user.name} is already verified.")
            return await interaction.response.send_message(":white_check_mark: You are already verified!", ephemeral=True)

        captcha, image = self.generate_captcha() # generate the captcha code and image

        try:
            # send it to the user in DM
            await interaction.user.send("Please solve the captcha to verify:")
            await interaction.user.send(file=discord.File(fp=image, filename="captcha.png"))
            # logging it
            logging.info(f"[+] [Captcha Button] {interaction.user.name} has been sent a captcha.")
        except discord.Forbidden:
            # logging that they had their DM's disabled
            logging.error(f"[!] [Captcha Button] {interaction.user.name} has DM's disabled.")
            return await interaction.response.send_message(f"I can't DM you. Please enable DMs from server members.",
                                                           ephemeral=True)
        # adding them to memory to hold onto the code
        self.bot.pending_captcha[interaction.user.id] = {
            "code": captcha,
            "guild_id": guild.id,
            "role_id": role.id,
        }
        return await interaction.response.send_message(f"I've DM'd you the code!", ephemeral=True)

    @staticmethod
    def generate_captcha():
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        image = Image.new('RGB', (240, 100), color=(255, 255, 255))
        draw = ImageDraw.Draw(image)

        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()

        draw.text((30, 25), code, font=font, fill=(0, 0, 0))

        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        return code, buffer