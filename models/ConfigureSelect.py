from interactions import StringSelectMenu
from config import config_values

def generate_configure_options():
    configure_options = [
        f"{'Disable' if config_values['status_managing_guests'] else 'Enable'} 'Managing Guests' Feature\n",
        f"{'Disable' if config_values['status_full_spreadsheet_update'] else 'Enable'} 'Full Spreadsheet Update' Feature\n",
        "Done"
        ]
    
    return configure_options

def generate_configure_select_component():
    configure_select_component = StringSelectMenu(
        generate_configure_options(),
        placeholder="What action would you like to take?",
        min_values=1,
        max_values=1,
        custom_id="configure_select"
        )
    
    return configure_select_component