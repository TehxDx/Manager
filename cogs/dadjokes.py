import discord
from discord import app_commands
from discord.ext import commands
import requests
import logging

class DadJokes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.api_url= "https://jokeapi.xyz/api/dadjoke/random"

    @app_commands.command(name="dadjoke", description="Get a random dad joke!")
    async def dadjoke(self, interaction: discord.Interaction):
        logging.info(f"{interaction.user.name} has requested a dad joke!")
        await interaction.response.defer()
        fetch = requests.get(self.api_url)

        if fetch.status_code != 200:
            logging.error(f"[DadJoke] API Fetch failed, {fetch.status_code}")
            return await interaction.followup.send("That api does not work! :(")
        else:
            logging.info(f"[DadJoke] Joke received successfully.")
            response = fetch.json()
            return await interaction.followup.send(response['Joke'])

async def setup(bot):
    await bot.add_cog(DadJokes(bot))
