from os import getenv
from dotenv import load_dotenv
from interactions import Client, Intents, listen, slash_command, SlashContext
from interactions.api.events import CommandError, MemberUpdate
import traceback


# Load Env Variables
load_dotenv()
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
GUILD_ID = getenv("GUILD_ID")
SCOPES = [GUILD_ID]


# Initialise Bot
bot = Client(token=DISCORD_TOKEN, intents=Intents.DEFAULT | Intents.GUILD_MEMBERS)


# Listeners
@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}.")

@listen(CommandError, disable_default_listeners=True)  # tell the dispatcher that this replaces the default listener
async def on_command_error(event: CommandError):
    traceback.print_exception(event.error)
    if not event.ctx.responded:
        await event.ctx.send("Something went wrong.")

@listen(MemberUpdate)
async def on_member_update(event: MemberUpdate):
    before = event.before
    after = event.after

    if not before.has_role(1221723231862657056) and after.has_role(1221723231862657056):
        print(f"{event.after.display_name} has just been given the Guest role.")
    elif before.has_role(1221723231862657056) and not after.has_role(1221723231862657056):
        print(f"The Guest role has just been removed from {event.after.display_name}.")

# Slash Commands
@slash_command(name="hello", description="Says Hello", scopes=SCOPES)
async def hello(ctx: SlashContext):
    await ctx.send("Hello!")

@slash_command(name="give_guest_role", description="Gives the Guest role", scopes=SCOPES)
async def give_guest_role(ctx: SlashContext):
    if not ctx.member.has_role(1221723231862657056):
        await ctx.member.add_role(role=1221723231862657056)
        await ctx.send("You now have the guest role.")
    else:
        await ctx.member.remove_role(role=1221723231862657056)
        await ctx.send("You now no longer have the guest role.")

# Start Bot
bot.start()