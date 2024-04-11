from config import config_values

def generate_features_status():
    features_status = (
        f"-- Status of BlossomzBot Features --\n"
        f"Managing Guests : {'Enabled' if config_values['status_managing_guests'] else 'Disabled'}\n"
    )

    return features_status
