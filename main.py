from os import getenv
from dotenv import load_dotenv
from interactions import Client, Intents, listen, ComponentContext, component_callback, slash_command, SlashContext
from interactions.api.events import CommandError, MemberUpdate
from config import config_values
from functions import create_resolve_guest_buttons, create_action_rows_horizontally, convert_feature_to_config_key
from components.select.ConfigureSelect import generate_configure_select_component
from components.content.FeaturesStatus import generate_features_status
import traceback
import re


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

    # Resolve Guest Role
    if config_values["status_managing_guests"] and after.has_role(config_values["guest_role"]):
        content = f"{event.after.display_name} has the Guest role. Which role do you want to change it to?"
        components = create_resolve_guest_buttons(username = event.after.username, display_name = event.after.display_name, member_id = event.after.id)
        action_rows = create_action_rows_horizontally(components)

        await managing_guests_channel.send(content=content, components=action_rows)


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
                await member.remove_role(config_values["guest_role"])

                # Checking for extra roles
                if member.has_role(config_values["friend_role"]):
                    await member.remove_role(config_values["friend_role"])
                if member.has_role(config_values["best_friend_role"]):
                    await member.remove_role(config_values["best_friend_role"])   

                await member.add_role(config_values["member_role"]) 
                await ctx.edit_origin(content=f"{name} now has the Member role. The Guest role was removed.", components=[])

            case "best_friend":
                member = ctx.guild.get_member(member_id)
                await member.remove_role(config_values["guest_role"])

                # Checking for extra roles
                if member.has_role(config_values["member_role"]):
                    await member.remove_role(config_values["member_role"])
                if member.has_role(config_values["friend_role"]):
                    await member.remove_role(config_values["friend_role"])   

                await member.add_role(config_values["best_friend_role"]) 
                await ctx.edit_origin(content=f"{name} now has the Best Friend role. The Guest role was removed.", components=[])

            case "friend":
                member = ctx.guild.get_member(member_id)
                await member.remove_role(config_values["guest_role"])

                # Checking for extra roles
                if member.has_role(config_values["member_role"]):
                    await member.remove_role(config_values["member_role"])
                if member.has_role(config_values["best_friend_role"]):
                    await member.remove_role(config_values["best_friend_role"])   

                await member.add_role(config_values["friend_role"]) 
                await ctx.edit_origin(content=f"{name} now has the Friend role. The Guest role was removed.", components=[])

            case "guest":
                member = ctx.guild.get_member(member_id)

                # Checking for extra roles
                if member.has_role(config_values["member_role"]):
                    await member.remove_role(config_values["member_role"])
                if member.has_role(config_values["best_friend_role"]):
                    await member.remove_role(config_values["best_friend_role"])
                if member.has_role(config_values["friend_role"]):
                    await member.remove_role(config_values["friend_role"])    

                await ctx.edit_origin(content=f"{name} will continue having the Guest role.", components=[])

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


# Slash Commands
@slash_command(name="configure", description="Shows the status of each BlossomzBot feature and allows for enabling/disabling them", scopes=SCOPES)
async def configure(ctx: SlashContext):
    if not ctx.member.has_role(config_values["leader_role"]) and not ctx.member.has_role(config_values["officer_role"]):
        await ctx.send("You do not have permission to use this command.", ephemeral=True)
    else:
        blossomz_bot_channel = ctx.guild.get_channel(config_values["blossomz_bot_channel_id"])
        
        await ctx.send("Loading...", ephemeral=True)
        await ctx.delete()
        await blossomz_bot_channel.send(content=generate_features_status(), components=generate_configure_select_component())
    

# Start Bot
bot.start()