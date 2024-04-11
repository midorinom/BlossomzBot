from interactions import ActionRow, Button, ButtonStyle


def create_action_rows_horizontally(components):
    action_rows: list[ActionRow] = [ActionRow(*components)]

    return action_rows

def create_resolve_guest_buttons(username, display_name, member_id):
    member_button = Button(
        style=ButtonStyle.SUCCESS,
        label="Member",
        custom_id=f"member_button_{username}_{display_name}_{member_id}",
        disabled=False,
    )

    best_friend_button = Button(
        style=ButtonStyle.PRIMARY,
        label="Best Friend",
        custom_id=f"best_friend_button_{username}_{display_name}_{member_id}",
        disabled=False,
    )

    friend_button = Button(
        style=ButtonStyle.DANGER,
        label="Friend",
        custom_id=f"friend_button_{username}_{display_name}_{member_id}",
        disabled=False,
    )

    guest_button = Button(
        style=ButtonStyle.SECONDARY,
        label="Remain as Guest",
        custom_id=f"guest_button_{username}_{display_name}_{member_id}",
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