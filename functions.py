import mysql.connector
from interactions import ActionRow, Button, ButtonStyle
from config import config_values

def query_database(sql_command, database_credentials, need_to_commit = False):
    try:
        conn = mysql.connector.connect(
        host=database_credentials["host"],
        user=database_credentials["user"],
        password=database_credentials["password"],
        database=database_credentials["database_name"]
        )
        cursor = conn.cursor() 
        cursor.execute(sql_command)

        if not need_to_commit:
            result = cursor.fetchall()
            return result
        else:
            conn.commit()
    except mysql.connector.Error as err:
        raise RuntimeError(f"Error executing SQL command: {err}")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_action_rows_horizontally(components):
    action_rows: list[ActionRow] = [ActionRow(*components)]

    return action_rows

def create_resolve_guest_buttons(username, display_name, joined_at, member_id):
    member_button = Button(
        style=ButtonStyle.SUCCESS,
        label="Member",
        custom_id=f"member_button_{username}_{display_name}_{joined_at}_{member_id}",
        disabled=False,
    )

    best_friend_button = Button(
        style=ButtonStyle.PRIMARY,
        label="Best Friend",
        custom_id=f"best_friend_button_{username}_{display_name}_{joined_at}_{member_id}",
        disabled=False,
    )

    friend_button = Button(
        style=ButtonStyle.DANGER,
        label="Friend",
        custom_id=f"friend_button_{username}_{display_name}_{joined_at}_{member_id}",
        disabled=False,
    )

    guest_button = Button(
        style=ButtonStyle.SECONDARY,
        label="Remain as Guest",
        custom_id=f"guest_button_{username}_{display_name}_{joined_at}_{member_id}",
        disabled=False,
    )

    return [member_button, best_friend_button, friend_button, guest_button]

def convert_feature_to_config_key(feature):
    config_key = "status_"

    for char in feature:
        if char == " ":
            config_key += "_"
        elif char.isupper():
            config_key += char.lower()
        else:
            config_key += char

    return config_key

def count_number_of_roles(member):
    roles = 0

    if member.has_role(config_values["member_role"]):
        roles += 1
    if member.has_role(config_values["best_friend_role"]):
        roles += 1
    if member.has_role(config_values["friend_role"]):
        roles += 1
    if member.has_role(config_values["guest_role"]):
        roles += 1

    return roles

def get_prev_or_new_role(member):
    prev_or_new_role = ""

    if member.has_role(config_values["member_role"]):
        prev_or_new_role = "Member"
    elif member.has_role(config_values["best_friend_role"]):
        prev_or_new_role = "Best Friend"
    elif member.has_role(config_values["friend_role"]):
        prev_or_new_role = "Friend"
    elif member.has_role(config_values["guest_role"]):
        prev_or_new_role = "Guest"

    return prev_or_new_role

def sift_out_prev_role(member_before, new_role):
    prev_role = ""

    if member_before.has_role(config_values["member_role"]) and new_role != "Member":
        prev_role = "Member"
    elif member_before.has_role(config_values["best_friend_role"]) and new_role != "Best Friend":
        prev_role = "Best Friend"
    elif member_before.has_role(config_values["friend_role"]) and new_role != "Friend":
        prev_role = "Friend"

    return prev_role
