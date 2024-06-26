from os import getenv
from dotenv import load_dotenv
from interactions import Client, Intents, listen, ComponentContext, component_callback, SlashContext, OptionType, slash_command, slash_option
from interactions.api.events import CommandError, MemberUpdate, MemberRemove
from config import config_values
from functions import query_database, create_resolve_guest_buttons, create_action_rows_horizontally, convert_feature_to_config_key, count_number_of_roles, get_prev_or_new_role, sift_out_prev_role, create_kick_nicely_buttons, create_send_welcome_message_buttons
from sql_queries.managing_members import sql_check_if_member_exists, sql_insert_member, sql_delete_member
from models.ConfigureSelect import generate_configure_select_component
from models.FeaturesStatus import generate_features_status
from models.Messages import error_messages, kick_message, welcome_message
from models.SheetDB import generate_payload_create_in_holding_area
from controllers.general import make_api_call
from controllers.sheetdb import create_in_holding_area
import asyncio
import traceback
import re
from datetime import datetime


# Load Env Variables
load_dotenv()
DISCORD_TOKEN = getenv("DISCORD_TOKEN")
GUILD_ID = getenv("GUILD_ID")
SCOPES = [GUILD_ID]
DATABASE_CREDENTIALS = {
    "host": getenv("DB_HOST"),
    "user": getenv("DB_USER"),
    "password": getenv("DB_PASSWORD"),
    "database_name": getenv("DB_NAME")
}


# Initialise Bot
bot = Client(token=DISCORD_TOKEN, intents=Intents.DEFAULT | Intents.GUILD_MEMBERS, delete_unused_application_cmds=True, fetch_members=True)


# Initialise Queues
queue_of_members = {}

# Listeners
@listen()
async def on_ready():
    print("Ready")
    print(f"This bot is owned by {bot.owner}.")

@listen(CommandError, disable_default_listeners=True) # tell the dispatcher that this replaces the default listener
async def on_command_error(event: CommandError):
    traceback.print_exception(event.error)
    if not event.ctx.responded:
        await event.ctx.send("Something went wrong.")

@listen(MemberUpdate)
async def on_member_update(event: MemberUpdate):
    before = event.before
    after = event.after
    managing_guests_channel = event.client.get_channel(config_values["managing_guests_channel_id"])
    blossomz_bot_channel = event.client.get_channel(config_values["blossomz_bot_channel_id"])

    # Exclude Admins
    if after.has_role(config_values["leader_role"]) or after.has_role(config_values["officer_role"]):
        return

    # Check for Multiple Roles
    number_of_roles = count_number_of_roles(after)
    
    if number_of_roles > 1:
        await blossomz_bot_channel.send(f"{after.display_name} ({after.username}) has multiple roles (member / best friend / friend / guest). Please remove the extra roles.")

    # Has only 1 role
    elif number_of_roles == 1:
        # Resolve Guest Role
        if config_values["status_managing_guests"] and after.has_role(config_values["guest_role"]):
            try:
                result = query_database(sql_check_if_member_exists(after.id), DATABASE_CREDENTIALS)

                if not result:
                    content = f"{after.display_name} has the Guest role. Which role do you want to change it to?"
                    joined_at = str(after.joined_at).split(":")[1][:-1] # Extracting the numerical timestamp, in a string format
                    components = create_resolve_guest_buttons(username = after.username, display_name = after.display_name, joined_at = joined_at, member_id = after.id)
                    action_rows = create_action_rows_horizontally(components)

                    await managing_guests_channel.send(content=content, components=action_rows)
                    query_database(sql_insert_member(after.id), DATABASE_CREDENTIALS, True)
            except Exception as e:
                print(e)
                await blossomz_bot_channel.send(error_messages["01"])

        # New Role is not Guest Role
        elif not after.has_role(config_values["guest_role"]):
            new_role = get_prev_or_new_role(after)
            prev_role = ""

            if after.id in queue_of_members:
                prev_role = queue_of_members[after.id]
                del queue_of_members[after.id]
            else:
                if before.display_name == after.display_name and before.username == after.username:
                    # User has been updated in ways other than display name / username / role (e.g. profile picture)
                    number_of_prev_roles = count_number_of_roles(before)
                    if number_of_prev_roles == number_of_roles:
                        return
                    
                    prev_role = sift_out_prev_role(before, new_role)
                else:
                    prev_role = new_role

            if prev_role != new_role:
                await blossomz_bot_channel.send(f"{after.display_name} ({after.username})'s role has been changed from '{prev_role}' to '{new_role}'.")
            else:
                if before.display_name != after.display_name:
                    await blossomz_bot_channel.send(f"{after.display_name} ({after.username}) has changed their display name from '{before.display_name}'.")
                if before.username != after.username:
                    await blossomz_bot_channel.send(f"{after.display_name} ({after.username}) has changed their discord username from '{before.username}'.")

            if config_values['status_automated_sheet_updates']:
                try:
                    payload = generate_payload_create_in_holding_area(after.display_name, after.username, prev_role, new_role, after.joined_at, after.id)
                    response = await make_api_call(create_in_holding_area, payload)
                except Exception as e:
                    print(e)
                    await blossomz_bot_channel.send(error_messages["02"])

    # A role has been removed
    elif number_of_roles == 0:
        prev_role = get_prev_or_new_role(before)
        # Store the previous role inside the queue
        queue_of_members[after.id] = prev_role

        # Wait 30 seconds
        await asyncio.sleep(30)
        if after.id in queue_of_members:
            del queue_of_members[after.id]
            await blossomz_bot_channel.send(f"{after.display_name} ({after.username})'s '{prev_role}' role was removed.")
        
            if config_values['status_automated_sheet_updates']:
                try:
                    payload = generate_payload_create_in_holding_area(after.display_name, after.username, prev_role, "", after.joined_at, after.id)
                    response = await make_api_call(create_in_holding_area, payload)
                except Exception as e:
                    print(e)
                    await blossomz_bot_channel.send(error_messages["02"])


# If the member has left the discord server
@listen(MemberRemove)
async def on_member_remove(event: MemberRemove):
    blossomz_bot_channel = event.client.get_channel(config_values["blossomz_bot_channel_id"])
    
    try:
        query_database(sql_delete_member(event.member.id), DATABASE_CREDENTIALS, True)
    except Exception as e:
        print(e)
        await blossomz_bot_channel.send(error_messages["03"])

# Component Listeners
resolve_guest_button_regex = re.compile(r"(\w+)_button_(\w+)_([0-9]+)_(\w+)_([0-9]+)")
@component_callback(resolve_guest_button_regex)
async def resolve_guest_button_callback(ctx: ComponentContext):
    match = resolve_guest_button_regex.match(ctx.custom_id)
    if match:
        chosen_option = match.group(1)
        username = match.group(2)
        display_name = match.group(4)
        joined_at = datetime.fromtimestamp(int(match.group(3)))
        member_id = match.group(5)

        name = f"{display_name} ({username})"
        if display_name == username:
            name = display_name

        match (chosen_option):
            case "member":
                member = ctx.guild.get_member(member_id)

                await member.remove_role(config_values["guest_role"]) 
                await member.add_role(config_values["member_role"]) 
                await ctx.edit_origin(content=f"{name} now has the Member role. The Guest role was removed.", components=[])

                if config_values['status_welcome_message']:
                    blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])

                    try:
                        await member.send(welcome_message)
                        await blossomz_bot_channel.send(f"A welcome message has been sent to {name}.")
                    except Exception as e:
                        print(e)
                        await blossomz_bot_channel.send(error_messages["05"])

            case "best_friend":
                member = ctx.guild.get_member(member_id)

                await member.remove_role(config_values["guest_role"])
                await member.add_role(config_values["best_friend_role"]) 
                await ctx.edit_origin(content=f"{name} now has the Best Friend role. The Guest role was removed.", components=[])

                if config_values['status_welcome_message']:
                    blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])

                    try:
                        await member.send(welcome_message)
                        await blossomz_bot_channel.send(f"A welcome message has been sent to {name} ({username}).")
                    except Exception as e:
                        print(e)
                        await blossomz_bot_channel.send(error_messages["05"])

            case "friend":
                member = ctx.guild.get_member(member_id)

                await member.remove_role(config_values["guest_role"])
                await member.add_role(config_values["friend_role"]) 
                await ctx.edit_origin(content=f"{name} now has the Friend role. The Guest role was removed.", components=[])

            case "guest":
                await ctx.edit_origin(content=f"{name} will continue having the Guest role.", components=[])
                blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
                
                if config_values['status_automated_sheet_updates']:
                    try:
                        payload = generate_payload_create_in_holding_area(display_name, username, "Guest", "Guest", joined_at, member_id)
                        response = await make_api_call(create_in_holding_area, payload)
                    except Exception as e:
                        print(e)
                        await blossomz_bot_channel.send(error_messages["02"])

            case _:
                raise Exception(f"No option was selected for resolving {name}'s Guest role.")
        
@component_callback("configure_select")
async def configure_select_callback(ctx: ComponentContext):
    selected_option = ctx.values[0]
    if selected_option == "Done":
        await ctx.defer(edit_origin=True)
        await ctx.delete(ctx.message)
    else:
        enable_feature_regex = re.compile(r"Enable '([^']+)' Feature")
        match_enable_feature = enable_feature_regex.match(selected_option)
        if match_enable_feature:
            feature = match_enable_feature.group(1)
            config_key = convert_feature_to_config_key(feature)
            config_values[config_key] = True

            await ctx.edit_origin(content=f"The '{feature}' feature is now enabled.\n\n{generate_features_status()}", components=[])
        
        else:
            disable_feature_regex = re.compile(r"Disable '([^']+)' Feature")
            match_disable_feature = disable_feature_regex.match(selected_option)
            if match_disable_feature:
                feature = match_disable_feature.group(1)
                config_key = convert_feature_to_config_key(feature)
                config_values[config_key] = False

                await ctx.edit_origin(content=f"The '{feature}' feature is now disabled.\n\n{generate_features_status()}", components=[])

kick_nicely_regex = re.compile(r"kick_nicely_(yes|no)_([\w.]+)_([0-9]+)_([\w.]+)")
@component_callback(kick_nicely_regex)
async def kick_nicely_callback(ctx: ComponentContext):
    match = kick_nicely_regex.match(ctx.custom_id)
    if match:
        chosen_option = match.group(1)
        username = match.group(2)
        display_name = match.group(4)
        member_id = match.group(3)

        match (chosen_option):
            case "yes":
                blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
                member = ctx.guild.get_member(member_id)
                
                await ctx.defer(edit_origin=True)
                await ctx.delete(ctx.message)

                try:
                    await member.send(kick_message) 
                    await blossomz_bot_channel.send(content=f"{display_name} ({username}) has been kicked using the 'kick_nicely' command. A private message has been sent to them.")
                except Exception as e:
                    print(e)
                    await blossomz_bot_channel.send(error_messages["04"])

                await ctx.guild.kick(member_id)
            
            case "no":
                await ctx.defer(edit_origin=True)
                await ctx.delete(ctx.message)

send_welcome_message_regex = re.compile(r"send_welcome_message_(yes|no)_([\w.]+)_([0-9]+)_([\w.]+)")
@component_callback(send_welcome_message_regex)
async def send_welcome_message_callback(ctx: ComponentContext):
    match = send_welcome_message_regex.match(ctx.custom_id)
    if match:
        chosen_option = match.group(1)
        username = match.group(2)
        display_name = match.group(4)
        member_id = match.group(3)

        match (chosen_option):
            case "yes":
                blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
                member = ctx.guild.get_member(member_id)
                
                try:
                    await member.send(welcome_message)  
                except Exception as e:
                    print(e)
                    await blossomz_bot_channel.send(error_messages["05"])

                await ctx.defer(edit_origin=True)
                await ctx.delete(ctx.message)
                await blossomz_bot_channel.send(content=f"A welcome message has been sent to {display_name} ({username}).")
            
            case "no":
                await ctx.defer(edit_origin=True)
                await ctx.delete(ctx.message)

# Slash Commands
@slash_command(name="configure", description="Shows the status of each BlossomzBot feature and allows for enabling/disabling them", scopes=SCOPES)
async def configure(ctx: SlashContext):
    if not ctx.member.has_role(config_values["leader_role"]) and not ctx.member.has_role(config_values["officer_role"]):
        await ctx.send("You do not have the permissions to use this command.", ephemeral=True)
    else:
        blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])

        await ctx.send("Loading...", ephemeral=True)
        await ctx.delete()
        await blossomz_bot_channel.send(content=generate_features_status(), components=generate_configure_select_component())


@slash_command(name="kick_nicely", description="Kicks a user from the Blossomz discord server and sends a private message to them.", scopes=SCOPES)
@slash_option(
    name="discord_user_id",
    description="You can get this by right clicking on the user and selecting 'Copy User ID'.",
    required=True,
    opt_type=OptionType.STRING
)
async def kick_nicely(ctx: SlashContext, discord_user_id: str):
    if not ctx.member.has_role(config_values["leader_role"]) and not ctx.member.has_role(config_values["officer_role"]):
        await ctx.send("You do not have the permissions to use this command.", ephemeral=True)
    else:
        blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
        member = ctx.guild.get_member(discord_user_id)
        
        await ctx.send("Loading...", ephemeral=True)
        await ctx.delete()

        components = create_kick_nicely_buttons(username = member.username, display_name = member.display_name, member_id = discord_user_id)
        action_rows = create_action_rows_horizontally(components)
        await blossomz_bot_channel.send(content=f"Hello <@{ctx.author_id}>.\nAre you sure you want to kick {member.display_name} ({member.username})?", components=action_rows, ephemeral=True)


@slash_command(name="send_welcome_message", description="Sends a private welcome message to the discord user.", scopes=SCOPES)
@slash_option(
    name="discord_user_id",
    description="You can get this by right clicking on the user and selecting 'Copy User ID'.",
    required=True,
    opt_type=OptionType.STRING
)
async def send_welcome_message(ctx: SlashContext, discord_user_id: str):
    if not ctx.member.has_role(config_values["leader_role"]) and not ctx.member.has_role(config_values["officer_role"]):
        await ctx.send("You do not have the permissions to use this command.", ephemeral=True)
    else:
        blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
        member = ctx.guild.get_member(discord_user_id)
        
        await ctx.send("Loading...", ephemeral=True)
        await ctx.delete()

        components = create_send_welcome_message_buttons(username = member.username, display_name = member.display_name, member_id = discord_user_id)
        action_rows = create_action_rows_horizontally(components)
        await blossomz_bot_channel.send(content=f"Hello <@{ctx.author_id}>.\nAre you sure you want to send a welcome message to {member.display_name} ({member.username})?", components=action_rows, ephemeral=True)


# Start Bot
bot.start()