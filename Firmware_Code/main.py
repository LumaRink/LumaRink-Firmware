import ujson
from machine import Pin, Timer
import time
import neopixel
import requests as urequests
import uasyncio as asyncio
from wifi_manager import WifiManager
from settings_manager import load_settings, save_settings
from routines import (
    update_brightness,
    flashing_routine,
    fill_routine,
    fade_routine,
    skate_routine,
    skate_rng_routine,
    goal_routine,
    reset_brightness,
    wifi_connected_routine,
    wifi_connecting_routine
)
from wifi_functions import setup_wifi, reset_wifi
from api_nhl import team_info_update
import globals
from letters import letters_5x5

# ---------------- Settings ----------------
settings = load_settings()
colour = settings['colour']
colour_routine = settings['colour_routine']
brightness = settings['brightness']
MAX_COLOUR = settings['MAX_COLOUR']
num_pixels = settings['NUM_PIXELS']
skate_pixels = settings['SKATE_PIXELS']
word = settings['WORD']
myTeam = settings['MYTEAM']
url = settings['url']
myVersion = settings.get('myVersion', 1)

# ---------------- Button config ----------------
BUTTON_PINS = [7, 8, 9]  # 7=brightness/reset, 8=colour, 9=colour routine
DEBOUNCE_MS = settings.get('DEBOUNCE_MS', 50)
LONG_PRESS_MS = 5000

buttons = [Pin(pin, Pin.IN, Pin.PULL_UP) for pin in BUTTON_PINS]

# ---------------- NeoPixel setup ----------------
pin_np = Pin(6, Pin.OUT)
np = neopixel.NeoPixel(pin_np, num_pixels)

# ---------------- Globals ----------------
lettersx4 = 0
colour_idx = 1
colour_idx_skate = -1
colour_idx_letters = -1
colour_b = False
colour_b_skate = False
colour_b_letters = False
fade = brightness
restart_flag = asyncio.Event()
wm = None

# ---------------- Load Colors ----------------
def load_colors(filename='colors.txt'):
    """
    Load RGB color definitions from a text file.

    Returns:
        dict: Mapping of color names to (R, G, B) tuples.
    """
    loaded_colors = {}
    with open(filename, 'r') as f:
        for line in f:
            name, values = line.strip().split(':')
            loaded_colors[name] = list(map(int, values.split(',')))
    return loaded_colors

loaded_colors = load_colors()

# Color palettes for different routines
iModeColours = [
    [loaded_colors.get("OFF"), loaded_colors.get("WHITE"), loaded_colors.get("RED"), loaded_colors.get("BLUE"), loaded_colors.get("WHITE")] + [(-1,-1,-1)]*4,
    [loaded_colors.get("OFF"), loaded_colors.get("WHITE"), loaded_colors.get("RED"), loaded_colors.get("ORANGE"),
     loaded_colors.get("YELLOW"), loaded_colors.get("GREEN"), loaded_colors.get("BLUE"), loaded_colors.get("VIOLET"), (-1,-1,-1)],
    [loaded_colors.get("OFF"), loaded_colors.get("WHITE"), loaded_colors.get("LBLUE"), loaded_colors.get("PINK"),
     loaded_colors.get("WHITE")] + [(-1,-1,-1)]*4
]

# ---------------- Reset Routine Variables ----------------
def reset_routine_vars():
    """
    Reset internal routine variables and clear LEDs.
    """
    global colour_idx, colour_b, fade
    global colour_idx_skate, colour_b_skate
    global colour_idx_letters, colour_b_letters

    # Reset routine indexes and flags
    colour_idx = 1
    colour_b = False
    fade = brightness
    colour_idx_skate = -1
    colour_b_skate = False
    colour_idx_letters = -1
    colour_b_letters = False

    # Clear all LEDs
    for i in range(num_pixels):
        np[i] = (0, 0, 0)
    np.write()

# ---------------- Button Actions ----------------
def toggle_brightness():
    """
    Cycle brightness levels and save to settings.
    """
    global brightness
    if brightness <= 0.02745:
        brightness = 0.60
    else:
        brightness /= 2
    update_brightness(np, brightness)
    settings['brightness'] = brightness
    save_settings(settings)

def toggle_colour():
    """
    Cycle main color and optionally trigger routine reset.
    """
    global colour
    colour = (colour + 1) % MAX_COLOUR
    settings['colour'] = colour
    save_settings(settings)
    if colour_routine in [2, 3]:
        return
    restart_flag.set()  # Reset routines on next loop

def toggle_colour_routine():
    """
    Cycle color routines and optionally trigger routine reset.
    """
    global colour_routine
    colour_routine = (colour_routine + 1) % 5
    settings['colour_routine'] = colour_routine
    save_settings(settings)
    if colour_routine == 3:
        return
    restart_flag.set()  # Reset routines on next loop

# ---------------- Button Watcher ----------------
async def watch_button(pin, idx):
    """
    Async task to watch a button and handle short/long presses.

    Args:
        pin (Pin): GPIO pin object.
        idx (int): Button index.
    """
    global wm
    while True:
        while pin.value():  # wait for button press
            await asyncio.sleep_ms(10)
        press_time = time.ticks_ms()
        long_press_handled = False

        while not pin.value():
            # Handle long press for button 0 (reset WiFi)
            if idx == 0 and time.ticks_diff(time.ticks_ms(), press_time) >= LONG_PRESS_MS:
                print("Long press detected on pin 7, resetting WiFi...")
                wm_new, success = await reset_wifi(wm, ap_name=myTeam, ap_password=myTeam)
                if success:
                    wm = wm_new
                    print("WiFi reset complete.")
                long_press_handled = True
                while not pin.value():
                    await asyncio.sleep_ms(10)
                break
            await asyncio.sleep_ms(10)

        # Handle short press actions
        if not long_press_handled:
            if idx == 0:
                toggle_brightness()
            elif idx == 1:
                toggle_colour()
            elif idx == 2:
                toggle_colour_routine()

        await asyncio.sleep_ms(100)

# ---------------- NeoPixel Routines ----------------
async def run_color_routines():
    """
    Run selected NeoPixel color routine.
    """
    global colour_idx, colour_b, fade, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters, restart_flag

    # Reset routine variables if flagged
    if restart_flag.is_set():
        reset_routine_vars()
        restart_flag.clear()

    colours = iModeColours[colour]

    # Select routine based on colour_routine
    if colour_routine == 0:
        colour_idx = await flashing_routine(np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
                                            colours, colour_idx, brightness)
    elif colour_routine == 1:
        colour_idx, colour_idx_letters, colour_b_letters = await fill_routine(
            np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
            colours, colour_idx, colour_idx_letters, colour_b_letters, brightness)
    elif colour_routine == 2:
        colour_idx, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters = await skate_routine(
            np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
            colours, colour_idx, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters, brightness)
    elif colour_routine == 3:
        colour_idx, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters = await skate_rng_routine(
            np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
            colours, colour_idx, colour_idx_skate, colour_b_skate, colour_idx_letters, colour_b_letters, brightness)
    elif colour_routine == 4:
        colour_idx, colour_b, fade = await fade_routine(
            np, num_pixels, skate_pixels, lettersx4, letters_5x5, word,
            colours, colour_idx, colour_b, brightness, fade)

# ---------------- Main Loop ----------------
async def main():
    """
    Main async event loop to manage WiFi, button watchers, NHL API updates, and LED routines.
    """
    global wm
    nhl_task = None

    # Initial WiFi connecting animation
    await wifi_connecting_routine(np, num_pixels, skate_pixels, iModeColours[0], brightness)

    # Setup WiFi
    wm, success = await setup_wifi(ap_name="LumaRink", ap_password="LumaRink")
    if not success:
        print("Initial WiFi setup failed, portal should be running.")

    # Start async button watchers
    for i, b in enumerate(buttons):
        asyncio.create_task(watch_button(b, i))

    wifi_connected_ran = False

    while True:
        try:
            # Run WiFi-connected routine once
            if wm.is_connected() and not wifi_connected_ran:
                await wifi_connected_routine(np, num_pixels, skate_pixels, iModeColours[colour], brightness)
                wifi_connected_ran = True

            # Start NHL API polling if WiFi connected
            if nhl_task is None and wifi_connected_ran and wm.is_connected():
                print("Starting NHL API updates")
                nhl_task = asyncio.create_task(team_info_update(url, myTeam, myVersion))

            # Run goal animation if score increased
            if globals.teamscore > globals.previous_score and globals.first_nhl_scores >= 2:
                await goal_routine(np, num_pixels, iModeColours[0], brightness)
            globals.previous_score = globals.teamscore

            # Run selected color routines
            await run_color_routines()

        except Exception as e:
            print(f"[Main] Loop error: {e}")
        await asyncio.sleep(0)

# ---------------- Start ----------------
try:
    asyncio.run(main())
except KeyboardInterrupt:
    print("Program stopped.")
except Exception as e:
    print(f"Unexpected error: {e}")