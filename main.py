from os import getenv
from dotenv import load_dotenv
from interactions import Client, Intents, listen, ComponentContext, component_callback
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
member_role = 1221723231862657059
best_friend_role = 1221723231862657058
friend_role = 1221723231862657057
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
        components = create_resolve_guest_buttons(username = event.after.username, display_name = event.after.display_name, member_id = event.after.id)
        action_rows = create_action_rows_horizontally(components)

        await blossomz_bot_channel.send(content=content, components=action_rows)


# Component Listeners
resolve_guest_button_regex = re.compile(r"(\w+)_button_(\w+)_(\w+)_([0-9]+)")
@component_callback(resolve_guest_button_regex)
async def resolve_guest_button_callback(ctx: ComponentContext):
    match = resolve_guest_button_regex.match(ctx.custom_id)
    if match:
        chosen_option = match.group(1)
        username = match.group(2)
        display_name = match.group(3)
        member_id = match.group(4)
        
        name = f"{display_name} ({username})"
        if display_name == username:
            name = display_name

        match (chosen_option):
            case "member":
                member = ctx.guild.get_member(member_id)
                await member.remove_role(guest_role)

                # Checking for extra roles
                if member.has_role(friend_role):
                    await member.remove_role(friend_role)
                if member.has_role(best_friend_role):
                    await member.remove_role(best_friend_role)   

                await member.add_role(member_role) 
                await ctx.edit_origin(content=f"{name} now has the Member role, the Guest role was removed.", components=[])

            case "best_friend":
                member = ctx.guild.get_member(member_id)
                await member.remove_role(guest_role)

                # Checking for extra roles
                if member.has_role(member_role):
                    await member.remove_role(member_role)
                if member.has_role(friend_role):
                    await member.remove_role(friend_role)   

                await member.add_role(best_friend_role) 
                await ctx.edit_origin(content=f"{name} now has the Best Friend role, the Guest role was removed.", components=[])

            case "friend":
                member = ctx.guild.get_member(member_id)
                await member.remove_role(guest_role)

                # Checking for extra roles
                if member.has_role(member_role):
                    await member.remove_role(member_role)
                if member.has_role(best_friend_role):
                    await member.remove_role(best_friend_role)   

                await member.add_role(friend_role) 
                await ctx.edit_origin(content=f"{name} now has the Friend role, the Guest role was removed.", components=[])

            case "guest":
                await ctx.send(f"{name} will continue having the Guest role.")

            case _:
                raise Exception(f"No option was selected for resolving {name}'s Guest role.")
            

# Start Bot
bot.start()