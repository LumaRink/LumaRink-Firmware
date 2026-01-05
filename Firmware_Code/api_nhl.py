import machine
import urequests
import uasyncio as asyncio
from settings_manager import save_settings, load_settings
import globals


async def team_info(url, myTeam, myVersion):
    """
    Fetch team information from the server.

    Args:
        url (str): Server endpoint URL.
        myTeam (str): Team name.
        myVersion (int): Firmware version (informational only).

    Returns:
        tuple: (game_state, team_score), defaults to ("OFF", 0) on errors.
    """
    try:
        # -----------------------------
        # Prepare payload
        # -----------------------------
        payload = {"message": myTeam, "version": myVersion}

        # -----------------------------
        # Send POST request to server
        # -----------------------------
        response = urequests.post(url, json=payload)
        print(f"[team_info] Response status: {response.status_code}")

        if response.status_code != 200:
            print("[team_info] Error: Failed to fetch team info from server.")
            return "OFF", 0

        # -----------------------------
        # Parse JSON response
        # -----------------------------
        try:
            data = response.json()
            print(f"[team_info] Fetched data: {data}")
        except ValueError:
            print("[team_info] Error: Failed to parse JSON response.")
            return "OFF", 0

        if 'error' in data:
            print(f"[team_info] Server error: {data['error']}")
            return "OFF", 0

        # -----------------------------
        # Extract relevant fields
        # -----------------------------
        if isinstance(data, dict):
            team_name = data.get("team_name", "Unknown")
            globals.teamscore = data.get("score_game", 0)
            game_state = data.get("game_state", "OFF")
            latestVersion = data.get("latestVersion", myVersion)
            firmware_server_url = data.get("firmware_server_url", url)

            print(f"[team_info] Team: {team_name}, Score: {globals.teamscore}, Game State: {game_state}")

            # -----------------------------
            # Update server URL if changed
            # -----------------------------
            if firmware_server_url != url:
                print(f"[team_info] Updating server URL to {firmware_server_url}")
                url = firmware_server_url
                settings = load_settings()
                settings['url'] = url
                save_settings(settings)
                print("[team_info] URL updated successfully!")

            # -----------------------------
            # Version info update (no debounce/double-press)
            # -----------------------------
            if latestVersion != myVersion:
                settings = load_settings()
                settings['myVersion'] = latestVersion
                save_settings(settings)
                print(f"[team_info] Firmware version updated to {latestVersion}")
                # Optional: trigger reset if needed
                # machine.reset()

            # -----------------------------
            # Determine return based on game state
            # -----------------------------
            if game_state in ["PRE", "LIVE", "CRIT", "FUT"]:
                return game_state, globals.teamscore
            else:
                return "OFF", 0

        else:
            print("[team_info] Error: Invalid data format from server.")
            return "OFF", 0

    except Exception as e:
        print(f"[team_info] Exception fetching team info: {e}")
        return "OFF", 0


async def team_info_update(url, myTeam, myVersion):
    """
    Continuously fetch and update team info at intervals based on game state.

    Args:
        url (str): Server endpoint URL.
        myTeam (str): Team name.
        myVersion (int): Firmware version.
    """
    while True:
        gamestate, score = await team_info(url, myTeam, myVersion)

        # -----------------------------
        # Track first NHL score fetches
        # -----------------------------
        if globals.first_nhl_scores <= 1:
            globals.first_nhl_scores += 1
            print(f"[team_info_update] First NHL fetch count: {globals.first_nhl_scores}")

        print(f"[team_info_update] Game state: {gamestate}, Score: {score}")

        # -----------------------------
        # Adjust polling interval based on game state
        # -----------------------------
        if gamestate in ["PRE", "LIVE", "CRIT"]:
            sleep_sec = 10        # Active game: frequent updates
        elif gamestate == "FUT":
            sleep_sec = 600       # Future game: periodic polling
        else:
            sleep_sec = 1800      # OFF or error: conserve bandwidth and power

        await asyncio.sleep(sleep_sec)