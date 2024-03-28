from os import getenv
from dotenv import load_dotenv
from interactions import Client, Intents, listen, slash_command, SlashContext, ComponentContext, component_callback
from interactions.api.events import CommandError, MemberUpdate
from functions import create_resolve_guest_buttons, create_action_rows_horizontally
import traceback
import re


# Load Env Variables
load_dotenv()
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
GUILD_ID = getenv("GUILD_ID")
SCOPES = [GUILD_ID]


# Server Variables
guest_role = 1221723231862657056


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
    blossomz_bot_channel = event.client.get_channel(1222459301201973359)

    # Resolve Guest Role
    if after.has_role(guest_role):
        content = f"{event.after.display_name} has the Guest role. Which role do you want to change it to?"
        components = create_resolve_guest_buttons(event.after.display_name)
        action_rows = create_action_rows_horizontally(components)

        await blossomz_bot_channel.send(content=content, components=action_rows)


# Component Listeners
resolve_guest_button_regex = re.compile(r"(\w+)_button_(\w+)")
@component_callback(resolve_guest_button_regex)
async def resolve_guest_button_callback(ctx: ComponentContext):
    match = resolve_guest_button_regex.match(ctx.custom_id)
    if match:
        chosen_option = match.group(1)
        display_name = match.group(2)

        match (chosen_option):
            case "member":
                await ctx.send(f"{display_name}'s role has been changed from Guest to Member.")
            case "best_friend":
                await ctx.send(f"{display_name}'s role has been changed from Guest to Best Friend.")
            case "friend":
                await ctx.send(f"{display_name}'s role has been changed from Guest to Friend.")
            case "guest":
                await ctx.send(f"{display_name} will continue having the Guest role.")
            case _:
                raise Exception(f"No option was selected for resolving {display_name}'s Guest role.")
            

# Slash Commands
@slash_command(name="hello", description="Says Hello", scopes=SCOPES)
async def hello(ctx: SlashContext):
    await ctx.send("Hello!")

@slash_command(name="give_guest_role", description="Gives the Guest role", scopes=SCOPES)
async def give_guest_role(ctx: SlashContext):
    if not ctx.member.has_role(guest_role):
        await ctx.member.add_role(role=guest_role)
        await ctx.send("You now have the guest role.")
    else:
        await ctx.member.remove_role(role=guest_role)
        await ctx.send("You now no longer have the guest role.")

# Start Bot
bot.start()