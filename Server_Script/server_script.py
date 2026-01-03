import machine
import urequests
import uasyncio as asyncio
from settings_manager import save_settings, load_settings
import globals

async def team_info(url, myTeam, myVersion):
    """
    Fetch team information from the server and handle updates.

    Args:
        url (str): Server endpoint URL.
        myTeam (str): Identifier for the team.
        myVersion (int): Current version of the software.

    Returns:
        tuple: (game_state, team_score)
               Defaults to ("OFF", 0) on errors.
    """
    try:
        payload = {"message": myTeam, "version": myVersion}
        response = urequests.post(url, json=payload)
        print(f"Response status: {response.status_code}")

        if response.status_code != 200:
            print("Error: Failed to fetch team info from server.")
            return "OFF", 0

        try:
            data = response.json()
            print(f"Fetched data: {data}")
        except ValueError:
            print("Error: Failed to parse JSON response.")
            return "OFF", 0

        if 'error' in data:
            print(f"Error: {data['error']}")
            return "OFF", 0

        if isinstance(data, dict):
            team_name = data.get("team_name", "Unknown")
            globals.teamscore = data.get("score_game", 0)
            game_state = data.get("game_state", "OFF")
            latestVersion = data.get("latestVersion", 1)
            new_url = data.get("new_url", None)

            print(f"Team: {team_name}, Score: {globals.teamscore}, Game State: {game_state}")

            if new_url and new_url != url:
                print(f"Updating URL to {new_url}")
                url = new_url
                settings = load_settings()
                settings['url'] = url
                save_settings(settings)
                print("URL updated successfully!")

            if latestVersion != myVersion:
                settings = load_settings()
                settings['myVersion'] = latestVersion
                if data.get("DOUBLE_PRESS_INTERVAL") is not None:
                    settings['DOUBLE_PRESS_INTERVAL'] = data.get("DOUBLE_PRESS_INTERVAL")
                if data.get("DEBOUNCE_MS") is not None:
                    settings['DEBOUNCE_MS'] = data.get("DEBOUNCE_MS")
                save_settings(settings)
                machine.reset()

            if game_state in ["PRE", "LIVE", "CRIT"]:
                return game_state, globals.teamscore
            else:
                return "OFF", 0
        else:
            print("Error: Invalid data format from server.")
            return "OFF", 0

    except Exception as e:
        print(f"Error fetching team info: {e}")
        return "OFF", 0

async def team_info_update(url, myTeam, myVersion):
    """
    Continuously fetch and update team info at intervals based on game state.

    Args:
        url (str): Server endpoint URL.
        myTeam (str): Identifier for the team.
        myVersion (int): Current version of the software.
    """
    while True:
        gamestate, score = await team_info(url, myTeam, myVersion)

        if globals.first_nhl_scores <= 1:
            globals.first_nhl_scores += 1
            print(globals.first_nhl_scores)

        print(f"Game state: {gamestate}, Score: {score}")

        if gamestate in ["PRE", "LIVE", "CRIT"]:
            sleep_sec = 10
        elif gamestate == "FUT":
            sleep_sec = 600
        else:
            sleep_sec = 1800

        await asyncio.sleep(sleep_sec)
