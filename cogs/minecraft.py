import json, discord, requests, base64, aiohttp, io
from discord import app_commands
from discord.ext import commands

class Minecraft(commands.Cog):

    minecraft = app_commands.Group(name="minecraft", description="Minecraft commands")

    def __init__(self, bot):
        self.bot = bot
        self.mc_url = "https://api.mojang.com/users/profiles/minecraft/"
        self.render = "https://crafatar.com/renders/body/"
        self.head = "https://crafatar.com/avatars/"
        self.header = {"Host": "crafatar.com"}


    @minecraft.command(name="lookup", description="Looks up a user's Minecraft profile")
    @app_commands.describe(user="Username")
    async def lookup(self, interaction: discord.Interaction, user: str):
        await interaction.response.defer(ephemeral=True)
        attach_files = []
        try:
            fetch = requests.get(self.mc_url + user)
            data = fetch.json()

            embed = discord.Embed(
                title=f"Minecraft Profile",
                color=discord.Color.green(),
                description=f"{data['name']} (`{data['id']}`)"
            )
            embed.set_image(url=f"https://mineskin.eu/armor/body/{data['name']}/100.png")
            embed.set_thumbnail(url=f"https://mineskin.eu/helm/{data['name']}/100.png")
            embed.set_footer(text="Images from Mineskin.eu")
            await interaction.followup.send(embed=embed, files=attach_files)

        except Exception as e:
            print(f"An error occurred during lookup: {e}")
            await interaction.followup.send("An error occurred while looking up the profile.")



async def setup(bot):
    await bot.add_cog(Minecraft(bot))