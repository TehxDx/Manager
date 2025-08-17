"""
    Joke Command(s)
        Dad Jokes powered by: https://icanhazdadjoke.com/
        Jokes powered by: https://jokeapi.dev/
"""
from discord import app_commands
from discord.ext import commands
import os, random, logging, requests, discord

class Jokes(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.dad_joke_url= "https://icanhazdadjoke.com/"
        """
            JokeAPI Configuration, I've included Safe mode for friendly jokes, however, removing ?safe-mode will
                include all types of nsfw jokes.
                
            Additionally, it is available in other languages, please check their API documentation for specific
                configurations. 
        """
        self.joke_api_url = "https://v2.jokeapi.dev/joke/Any?safe-mode" # only provides safe jokes and filters out bad ones.
        self.headers = {
            "User-Agent": "ManagerBot/1.0",
            "Accept": "application/json",
        }

    @app_commands.command(name="dadjoke", description="Get a random dad joke!")
    async def dadjoke(self, interaction: discord.Interaction):
        logging.info(f"[DadJoke] {interaction.user.name} has requested a dad joke!")
        # fetch the dadjoke api
        fetch = requests.get(self.dad_joke_url, headers=self.headers)
        if fetch.status_code != 200:
            # if status code is anything other than success, reply with a basic error message and log it
            logging.error(f"[DadJoke] Could not fetch a dad joke. {fetch.status_code}")
            # send error response to the user
            return await interaction.response.send_message("Could not fetch a dadjoke. Please try again later.")
        else:
            # format the json
            response = fetch.json()
            # make the response in an embed
            embed = discord.Embed(
                color=discord.Color.dark_magenta(),
            )
            embed.description = response["joke"]
            # ship the joke inside the embed to the user
            return await interaction.response.send_message(embed=embed)

    @app_commands.command(name="joke", description="Get a random joke!")
    async def joke(self, interaction: discord.Interaction):
        fetch = requests.get(self.joke_api_url, headers=self.headers)
        if fetch.status_code != 200:
            # if status code is anything other than success, reply with a basic error message and log it
            logging.error(f"[Joke] Could not fetch a joke. {fetch.status_code}")
            # send error response to the user
            return await interaction.response.send_message("Could not fetch a joke. Please try again later.")
        else:
            # format the json
            response = fetch.json()
            # make the response in an embed
            embed = discord.Embed(
                color=discord.Color.dark_magenta(),
            )
            if response['type'] == "single":
                # if single (one-liner jokes), just add into description
                embed.description = response['joke']
            else:
                # if two part (setup and delivery), show setup, then hide using || for the answer
                embed.description = f"{response['setup']}\n|| {response['delivery']} ||"
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
