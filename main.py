from os import getenv
from dotenv import load_dotenv
from interactions import Client, Intents, listen, slash_command, SlashContext
from interactions.api.events import CommandError
import traceback


# Load Env Variables
load_dotenv()
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
GUILD_ID = getenv("GUILD_ID")
SCOPES = [GUILD_ID]


# Initialise Bot
bot = Client(token=DISCORD_TOKEN, intents=Intents.DEFAULT)


# Listeners
@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}")

@listen(CommandError, disable_default_listeners=True)  # tell the dispatcher that this replaces the default listener
async def on_command_error(self, event: CommandError):
    traceback.print_exception(event.error)
    if not event.ctx.responded:
        await event.ctx.send("Something went wrong.")


# Slash Commands
@slash_command(name="test", description="hello world", scopes=SCOPES)
async def hello(ctx: SlashContext):
    await ctx.send("Hello!")


# Start Bot
bot.start()