# LumaRink FastAPI Server Documentation

This document explains how the **FastAPI server** interacts with LumaRink firmware, particularly for **barebones PCB users**.

---

## Server Purpose

- Provides NHL game data to boards in real time.  
- Tracks game state, team names, and scores.  
- Supplies the **current firmware server URL** in case it changes.  
- Boards use `myVersion` **only to detect server URL changes**.  
- Debounce and double-press settings are no longer used.  

---

## Endpoint

### POST `/nhl-data/`

**Description:** Returns data for the requested NHL team.

**Payload sent by firmware:**

```json
{
  "message": "<team_name>",
  "version": <myVersion>
}
```

- `message`: NHL team name (must match a game today).  
- `version`: current firmware version (used only to track URL changes).

---

## Server Response

**1. Team playing today**

```json
{
  "team_name": "<team_name>",
  "score_game": <score>,
  "game_state": "<PRE|LIVE|CRIT|FUT|OFF>",
  "firmware_server_url": "<current_server_url>",
  "latestVersion": <latest_version>
}
```

**Fields:**

| Field | Meaning |
|-------|--------|
| `team_name` | Name of the requested NHL team |
| `score_game` | Current score of that team |
| `game_state` | One of `PRE`, `LIVE`, `CRIT`, `FUT`, `OFF` |
| `firmware_server_url` | Current URL of the FastAPI server |
| `latestVersion` | Current server version (used to track URL changes) |

**2. Team not playing today or invalid team name**

```json
{
  "error": "Team not found",
  "firmware_server_url": "<current_server_url>",
  "latestVersion": <latest_version>
}
```

---

## Game States

| State | Meaning |
|-------|---------|
| `PRE` | Game about to start |
| `LIVE` | Game in progress |
| `CRIT` | Game critical event (e.g., goal scored) |
| `FUT` | Future game scheduled today |
| `OFF` | Game finished or inactive |

**Notes:**

- Boards return `score_game = 0` for FUT or OFF states.  
- Teams not playing today may return `"Team not found"`.  

---

## Polling Intervals

- **Board → Server:** Every 10 seconds for active games (`PRE`, `LIVE`, `CRIT`).  
- **Server → NHL API:** Every 5 seconds, independently of board requests.  
  - Ensures the server always has up-to-date scores ready for any board, accounting for the NHL API refresh time.  

---

## Notes for Barebones Users

- The firmware automatically updates the server URL if it changes.  
- Only the `myVersion` field is used for detecting URL changes; no other settings (like debounce/double-press) are required.  
- Teams not playing today will return `"Team not found"`.  
- If the board does not see updates, ensure WiFi is connected and the server URL is correct in `settings.json`.  
- **Running your own server:** Barebones users can run the FastAPI server locally or on their own VPS.  
  - To do this, update the `url` field in `settings.json` to point to your server instance.

---

## Additional Information

- The server polls NHL data every 5 seconds.  
- Multiple boards can connect simultaneously without affecting server performance.  
- All JSON requests and responses follow the examples above.  