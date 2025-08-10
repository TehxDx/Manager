"""
    Games COG
"""
from discord.ext import commands
from discord import app_commands
import os, random, logging, discord

class Games(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.magic_8_ball = [
            'It is certain',
            'It is decidedly so',
            'Without a doubt',
            'Yes',
            'Yes definitely',
            'You may rely on it',
            'As I see it, yes',
            'Most likely',
            'Outlook good',
            'Reply hazy, try again',
            'Ask again later',
            'Better not tell you now',
            'Cannot predict now',
            'Concentrate and ask again',
            "Don't count on it",
            'My reply is no',
            'My sources say no',
            'Outlook not so good',
            'Very doubtful'
        ]

    """
        Rock paper scissors game
    """
    @app_commands.command(name="rps", description="Rock Paper Scissors")
    @app_commands.describe(selection="Rock/Paper/Scissors")
    async def rps(self, interaction: discord.Interaction, selection: str):
        choices = ['rock', 'paper', 'scissors']
        pick = random.choice(choices)
        # winning conditions
        w_conditions = {
            'rock': 'scissors',
            'paper': 'rock',
            'scissors': 'paper'
        }
        userinput = selection.lower()
        if userinput not in choices:
            return await interaction.response.send_message("Response not accepted. Only `rock`, `paper`, `scissors` is accepted.", ephemeral=True)
        elif pick == userinput:
            return await interaction.response.send_message(f"I chose **{pick}**. It's a tie! 🤝")
        elif w_conditions[userinput] == pick:
            return await interaction.response.send_message(f"I chose **{pick}**. You won! 🎉")
        else:
            return await interaction.response.send_message(f"I chose **{pick}**. I won! 🤖")

    """
        Coinflip game
    """
    @app_commands.command(name="coinflip", description="Coin Flip")
    @app_commands.describe(coin="Heads/Tails")
    async def coinflip(self, interaction: discord.Interaction, coin: str):
        choices = ['heads', 'tails']
        userinput = coin.lower()
        pick = random.choice(choices)

        if userinput not in choices:
            return await interaction.response.send_message("Response not accepted. Only `heads`, `tails` is accepted.", ephemeral=True)
        elif pick == userinput:
            return await interaction.response.send_message(f"The coin landed on {pick}... {interaction.user.mention}, somehow you won....")
        else:
            return await interaction.response.send_message(f"The coin landed on {pick}, haha nice try {interaction.user.mention}")

    """
        Magic 8 Ball game
    """
    @app_commands.command(name="8ball", description="Ask a question, and shake the magic 8-ball")
    @app_commands.describe(question="Question")
    async def _8ball(self, interaction: discord.Interaction, question: str):
        choice = random.choice(self.magic_8_ball)
        return await interaction.response.send_message(choice)

async def setup(bot):
    # I am struggling with this --- lets do this a round-a-bout way
    games_enabled = os.getenv("GAMES_SYSTEM")
    return_type = games_enabled is not None and games_enabled.lower() == 'true'
    if return_type is True:
        logging.info("[Games] Games System is enabled")
        await bot.add_cog(Games(bot))
    else:
        logging.info("[Games] Games System not enabled")
