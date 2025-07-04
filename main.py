"""
    Manager Discord Bot
        written by: _xdx

    Version: 0.1.0B
"""
import discord
from discord.ext import commands
from dotenv import load_dotenv
import os, platform, asyncio
import logging
from lib.database.database import ManagerDB
from views.ticket import TicketView
from views.ticket_close import TicketClose
from views.captcha_button import CaptchaButton

# setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(filename="logs/latest.log", encoding="utf-8", mode="w"),
        logging.StreamHandler()
    ]
)

# .env file load, make sure you change your token
load_dotenv()

# managerbot class - this will load cogs and sync them to the tree
class ManagerBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if os.getenv("MOD_ENABLED") is not None and os.getenv("MOD_ENABLED").lower() == "true":
            self.config = {
                "modlog_channel": int(os.getenv("MOD_CHANNEL")),
                "modlog_guild": int(os.getenv("MOD_GUILD"))
            }
        self.pending_captcha = {} # captcha system
        self.database = ManagerDB() # init the database

        """
            Note: Removal of lowDB support - Since it has limitations at the moment and requires me to rebuild it,
            lowDB will have to be a project for another time
        """

    async def setup_hook(self) -> None:
        await self.load_cogs()
        await self.tree.sync()
        self.add_view(TicketView(bot=self))
        self.add_view(TicketClose(bot=self))
        self.add_view(CaptchaButton(bot=self))

    async def load_cogs(self):
        for file in os.listdir("./cogs"):
            if file.endswith(".py"):
                try:
                    await self.load_extension(f"cogs.{file[:-3]}")
                    logging.info(f"Loaded cogs.{file[:-3]}")
                    print(f"+| {file}")
                except Exception as e:
                    logging.error(f"Failed to load cogs.{file[:-3]}")
                    print(f">>> Failed to load {file}")
                    print(f">>> {e}")

intents = discord.Intents.default()
intents.members = True
intents.message_content = True
Manager = ManagerBot(command_prefix="!", intents=intents, help_command=None)

@Manager.event
async def on_ready():
    print("=|" * 4 + " Manager Bot " + "|=" * 4)
    print(f"- Discord.py Version: {discord.__version__}")
    print(f"- Python Version: {platform.python_version()}")
    print(f"- Running on: {platform.system()} {platform.release()} ({os.name})")
    print("=|" * 4 + " Manager Bot " + "|=" * 4)
    for cmd in Manager.tree.get_commands():
        print(f"/{cmd.name} → Loaded")
    logging.info(
        f"PYV: {platform.python_version()}"
        f" | DPYV: {discord.__version__}"
        f" | Running on: {platform.system()} {platform.release()} ({os.name})"
    )

# bot start
async def start_bot():
    try:
        await Manager.start(os.getenv("DISCORD_TOKEN"))
    except Exception as e:
        print(f"Failed to start bot: {e}")
        logging.error(f"Failed to start bot: {e}")
    finally:
        await Manager.close()

if __name__ == "__main__":
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print("Stopping bot...")
        logging.info("Stopping bot...")