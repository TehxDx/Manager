"""
    Joke Command(s)
        Dad Jokes powered by: https://icanhazdadjoke.com/
        Jokes powered by: https://jokeapi.dev/
"""
import discord
from discord import app_commands
from discord.ext import commands
import requests
import logging
import os

class Jokes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dad_joke_url= "https://icanhazdadjoke.com/"
        self.joke_api_url = "https://v2.jokeapi.dev/joke/Any?safe-mode" # only provides safe jokes and filters out bad ones.
        self.headers = {
            "User-Agent": "ManagerBot/1.0",
            "Accept": "application/json",
        }

    @app_commands.command(name="dadjoke", description="Get a random dad joke!")
    async def dadjoke(self, interaction: discord.Interaction):
        logging.info(f"[DadJoke] {interaction.user.name} has requested a dad joke!")

        fetch = requests.get(self.dad_joke_url, headers=self.headers)
        if fetch.status_code != 200:
            logging.error(f"[DadJoke] Could not fetch a dad joke. {fetch.status_code}")
            return await interaction.response.send_message("Could not fetch a dadjoke. Please try again later.")
        else:
            response = fetch.json()
            return await interaction.response.send_message(response['joke'])

    @app_commands.command(name="joke", description="Get a random joke!")
    async def joke(self, interaction: discord.Interaction):
        fetch = requests.get(self.joke_api_url, headers=self.headers)
        if fetch.status_code != 200:
            logging.error(f"[Joke] Could not fetch a joke. {fetch.status_code}")
            return await interaction.response.send_message("Could not fetch a joke. Please try again later.")
        else:
            response = fetch.json()
            embed = discord.Embed(
                title="I got a joke for you!",
                color=discord.Color.dark_magenta(),
                description="_Powered by: Jokeapi.dev_"
            )
            if response['type'] == "single":
                print(response)
                embed.add_field(name=response['joke'], value="\u200b", inline=False)
            else:
                embed.add_field(name=response['setup'], value="\u200b", inline=False)
                embed.add_field(name="\u200b", value=f"||{response['delivery']}||", inline=False)
            embed.set_footer(text=f"Category: {response['category']}")
            return await interaction.response.send_message(embed=embed)


async def setup(bot):
    # I am struggling with this --- lets do this a round-a-bout way
    joke_enabled = os.getenv("JOKECOMMANDS")
    return_type = joke_enabled is not None and joke_enabled.lower() == 'true'
    if return_type is True:
        logging.info("[Jokes] Joke commands is enabled")
        await bot.add_cog(Jokes(bot))
    else:
        logging.info("[Jokes] Joke commands not enabled")
