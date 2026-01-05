# LumaRink Firmware Settings (`settings.json`)

This document explains all configurable variables in the LumaRink firmware’s `settings.json` file.  
Barebones users can edit these to customize their board’s display, team, colors, and server connection.

---

## Example `settings.json`

```json
{
  "SKATE_PIXELS": 12,
  "NUM_PIXELS": 114,
  "WORD": "HABS",
  "MYTEAM": "Senators",
  "colour": 0,
  "colour_routine": 1,
  "brightness": 0.15,
  "myVersion": 1,
  "MAX_COLOUR": 3,
  "url": "http://nhl-vps-9175.vpsmini.keepsec.cloud/nhl-data/"
}
```
---

## Board Layout / LED Counts

### 4-Letter Boards

| Variable           | Type      | Default                                                | Description                                                                                         |
|--------------------|-----------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `SKATE_PIXELS`     | int       | 12                                                     | Number of LEDs used for the “skate” section. Must match your physical build for proper animations.  |
| `NUM_PIXELS`       | int       | 112                                                    | Total number of LEDs including the skate section.                                                   |

### 5-Letter Boards

| Variable           | Type      | Default                                                | Description                                                                                         |
|--------------------|-----------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `SKATE_PIXELS`     | int       | 14                                                     | Number of LEDs used for the “skate” section.                                                        |
| `NUM_PIXELS`       | int       | 139                                                    | Total number of LEDs including the skate section.                                                   |

### 6-Letter Boards

| Variable           | Type      | Default                                                | Description                                                                                         |
|--------------------|-----------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `SKATE_PIXELS`     | int       | 16                                                     | Number of LEDs used for the “skate” section.                                                        |
| `NUM_PIXELS`       | int       | 166                                                    | Total number of LEDs including the skate section.                                                   |

## Display / Visuals & Team

| Variable           | Type      | Default                                                | Description                                                                                         |
|--------------------|-----------|--------------------------------------------------------|-----------------------------------------------------------------------------------------------------|
| `WORD`             | string    | "SENS"                                                 | 4–6 letters displayed on the board. Adjust according to your board size.                            |
| `MYTEAM`           | string    | "Senators"                                             | NHL team name for live score updates. Must match the NHL API.                                       |
| `colour`           | int       | 0                                                      | Colour mode; 0 = team colours, other numbers cycle modes. See firmware docs.                        |
| `colour_routine`   | int       | 1                                                      | Colour routine; see firmware docs for options.                                                      |
| `brightness`       | float     | 0.15                                                   | LED brightness (0.0 = off, 1.0 = maximum).                                                          |
| `MAX_COLOUR`       | int       | 3                                                      | Maximum number of selectable colour modes.                                                          |
| `myVersion`        | int       | 1                                                      | Tracks server URL changes. Barebones users usually leave as 1.                                      |
| `url`              | string    | `http://nhl-vps-9175.vpsmini.keepsec.cloud/nhl-data/`  | FastAPI server URL. Barebones users can run their own VPS or local server and update this field.    |

---

## Notes for Barebones Users

- All variables can be edited safely, but ensure the types match (integer, float, string).  
- `MYTEAM` must match a team that has a game scheduled today, otherwise the server may return `"Team not found"`.  
- `WORD` can be 4–6 letters. For 5 or 6 letters, adjust `NUM_PIXELS` proportionally if using a custom LED board.  
- `url` can point to a personal FastAPI server if running locally or on a VPS. Update the firmware `myVersion` only if necessary to trigger URL changes.  
- Changes to this file take effect **after restarting the board**.

---

## Recommended Usage

1. Update `MYTEAM` to your preferred NHL team.  
2. Adjust `WORD` to match the letters you want displayed.  
3. Set `SKATE_PIXELS` and `NUM_PIXELS` according to your board build.  
4. Optional: adjust `colour`, `colour_routine`, and `brightness` to your preference.  
5. Ensure `url` points to the active FastAPI server.  

---

## Related Documentation

- For flashing the firmware, see [`flashing.md`](docs/flashing.md).  
- For WiFi setup, see [`wifi-setup.md`](docs/wifi-setup.md).  
- For server details and JSON interactions, see [`Server.md`](docs/Server.md).  