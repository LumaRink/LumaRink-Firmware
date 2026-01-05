from fastapi import FastAPI
from pydantic import BaseModel
import requests
import time
import threading
from typing import Optional, Dict

# -----------------------------------------------------------------------------
# FastAPI application instance
# -----------------------------------------------------------------------------
app = FastAPI()

# -----------------------------------------------------------------------------
# Global state
# -----------------------------------------------------------------------------
# These arrays are refreshed periodically with live NHL game data
awayTeamScore = []
gameState = []
homeTeamName = []
homeTeamScore = []
awayTeamName = []

# Firmware / protocol versioning
latestVersion = 1

# Input timing values sent to the firmware when versions mismatch
DOUBLE_PRESS_INTERVAL = 500
DEBOUNCE_MS = 50

# -----------------------------------------------------------------------------
# Request model
# -----------------------------------------------------------------------------
# Incoming POST data from the device
class Message(BaseModel):
    message: str   # Team name requested by the device
    version: int   # Firmware version running on the device

# -----------------------------------------------------------------------------
# Basic test endpoint
# -----------------------------------------------------------------------------
@app.get("/nhl-data/")
async def read_root():
    return {"message": "Hello from FastAPI!"}

# -----------------------------------------------------------------------------
# Main API endpoint used by LumaRink devices
# -----------------------------------------------------------------------------
@app.post("/nhl-data/")
async def receive_string(data: Message):
    print(f"Received request for team: {data.message} with version {data.version}")

    # Detect firmware version mismatch
    if data.version != latestVersion:
        print(
            f"Version mismatch: device ({data.version}) != server ({latestVersion})"
        )

    # Search for the requested team in the cached game data
    for x, team in enumerate(homeTeamName):
        # Home team match
        if homeTeamName[x] == data.message:
            print(f"Returning home team data for {data.message}")

            response = {
                "team_name": homeTeamName[x],
                "score_game": homeTeamScore[x],
                "game_state": gameState[x],
                "new_url": "http://nhl-vps-9175.vpsmini.keepsec.cloud/nhl-data/",
                "latestVersion": latestVersion,
            }

            # Include timing values if firmware version is outdated
            if data.version != latestVersion:
                response.update({
                    "DOUBLE_PRESS_INTERVAL": DOUBLE_PRESS_INTERVAL,
                    "DEBOUNCE_MS": DEBOUNCE_MS,
                })

            return response

        # Away team match
        elif awayTeamName[x] == data.message:
            print(f"Returning away team data for {data.message}")

            response = {
                "team_name": awayTeamName[x],
                "score_game": awayTeamScore[x],
                "game_state": gameState[x],
                "new_url": "http://nhl-vps-9175.vpsmini.keepsec.cloud/nhl-data/",
                "latestVersion": latestVersion,
            }

            # Include timing values if firmware version is outdated
            if data.version != latestVersion:
                response.update({
                    "DOUBLE_PRESS_INTERVAL": DOUBLE_PRESS_INTERVAL,
                    "DEBOUNCE_MS": DEBOUNCE_MS,
                })

            return response

    # Team not found in current game list
    print(f"No match found for team: {data.message}")
    return {"error": "Team not found"}

# -----------------------------------------------------------------------------
# NHL API polling
# -----------------------------------------------------------------------------
# NHL public API endpoint
url = "https://api-web.nhle.com/v1/score/now"

def fetch_data():
    """
    Fetches live NHL game data and refreshes the cached team lists.
    This data is used to respond quickly to device requests without
    hitting the NHL API on every request.
    """
    global awayTeamScore, gameState, homeTeamName, homeTeamScore, awayTeamName

    try:
        response = requests.get(url)
        response.raise_for_status()
        nhlapi = response.json()

        # Clear previous game data before storing new values
        gameState.clear()
        homeTeamName.clear()
        homeTeamScore.clear()
        awayTeamName.clear()
        awayTeamScore.clear()

        # Parse and store game information
        for game in nhlapi["games"]:
            gameState.append(game["gameState"])
            homeTeamName.append(game["homeTeam"]["name"]["default"])
            homeTeamScore.append(game["homeTeam"].get("score", 0))
            awayTeamName.append(game["awayTeam"]["name"]["default"])
            awayTeamScore.append(game["awayTeam"].get("score", 0))

    except requests.RequestException as e:
        print(f"Error fetching NHL data: {e}")

def poll_data():
    """
    Continuously polls the NHL API at a fixed interval to keep
    cached game data up to date.
    """
    while True:
        fetch_data()
        time.sleep(10)

# -----------------------------------------------------------------------------
# Startup event
# -----------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    """
    Starts the background polling thread when the server launches.
    """
    thread = threading.Thread(target=poll_data)
    thread.daemon = True
    thread.start()