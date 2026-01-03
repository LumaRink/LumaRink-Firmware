import ujson
import os

def load_settings():
    """
    Load settings from 'settings.json'.

    Returns:
        dict: A dictionary of settings.
              If the file is missing or invalid, returns default settings.
    """
    try:
        with open('settings.json', 'r') as f:
            # Load JSON settings from file
            return ujson.load(f)
    except (OSError, ValueError):
        # If the file doesn't exist or contains invalid JSON, return defaults
        print("Error loading settings, using defaults.")
        return {
            'colour': 0,                   # Default color index
            'colour_routine': 0,           # Default LED routine index
            'url': "http://192.168.2.101:8000/nhl-data/",  # Default API endpoint
            'brightness': 1,               # Default LED brightness (0-1 scale)
            'nhl_api': False,              # Enable NHL API usage (False = disabled)
            'DEBOUNCE_MS': 50,             # Button debounce in milliseconds
            'DOUBLE_PRESS_INTERVAL': 500,  # Double-press detection interval (ms)
            'MAX_COLOUR': 3,               # Maximum selectable color index
            'myVersion': 1,                # Firmware/software version
            'NUM_PIXELS': 114,             # Total number of LEDs on the strip
            'SKATE_PIXELS': 12,            # Number of LEDs in the skate section
            'WORD': 'SENS',                # Default word displayed on the sign
            'MYTEAM': 'Senators'           # Team identifier
        }

def save_settings(settings):
    """
    Save the provided settings dictionary to 'settings.json'.

    Args:
        settings (dict): Dictionary containing settings to save.
    """
    with open('settings.json', 'w') as f:
        # Serialize the dictionary as JSON and write to file
        ujson.dump(settings, f)