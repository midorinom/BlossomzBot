from datetime import datetime

def generate_payload_create_in_holding_area(display_name, discord_username, previous_role, new_role, joined_at, member_id ):
    payload_create_in_holding_area = {
        "Display Name": display_name,
        "Discord Username": discord_username,
        "Previous Role": previous_role,
        "New Role": new_role,
        "Date Joined": str(joined_at.date().strftime("%d %B %Y")),
        "Member ID": str(member_id)
        }
    
    return payload_create_in_holding_area
