# LumaRink 5x5 LED Board Firmware

This repository contains the firmware and full documentation for the **LumaRink 5x5 LED boards**, including both barebones PCBs and full assembled kits.

---

## Overview

- Displays names, hockey team logos, and patterns on a 5x5 LED matrix.
- Connects to WiFi for live NHL score updates (unique goal routine).
- Supports multiple colour modes, routines, and brightness control.
- Open source firmware, fully documented for recovery or customization.

---

## Powering On & WiFi Connection

- When powered, most of the skate will light up, indicating the board is attempting to connect to WiFi.  
- This may take a few seconds.  
- If the connection is successful, the LEDs will flash **three times**, enabling NHL updates.  

### Setting Up WiFi

1. If the device is **not already connected** to WiFi, it will broadcast an access point named:  
- SSID: LumaRink
- Password: LumaRink

2. Connect to this access point using a phone, tablet, or computer.  
3. Open a web browser and navigate to:  
- http://192.168.4.1

4. Follow the on-screen instructions to enter your local WiFi network’s **SSID and password**.  
5. The board will attempt to connect to your local network automatically.  
6. **If the device does not appear as an access point**, hold down the **Brightness / WiFi Reset button** for 5 seconds or longer to force the board into AP mode.

---

## Button Functions

The back of the PCB is silk-screened to indicate each button’s function.

### Brightness Control
- Single press the **Brightness Button** to lower brightness by half.  
- Once it reaches minimum, it resets to maximum.

### WiFi Reset
- Hold the **Brightness / WiFi Reset Button** for 5+ seconds to clear WiFi settings and force AP mode.  
- Follow the WiFi setup steps above to reconnect.

### Colour Modes
- Single press the **Colours Button** to cycle modes:  
- Team colours  
- LGBTQ2+  
- Trans  
- Custom (if requested/configured)

### Colour Routines
- Pressing the **Colour Button** repeatedly cycles through routines:  
1. **Flashing** – Flashes on/off, cycling through the selected colour mode.  
2. **Fill** – Fills from button to top, then empties downward.  
3. **Skate** – Fills left-to-right and empties right-to-left; cycles colours per pass. The button ‘skate’ fills/empties white on its own.  
4. **RNG Skate** – Similar to Skate, but each LED cycles colours independently.  
5. **Fade** – Fades from maximum brightness to off and back, cycling colours.

---

## NHL Updates

- When connected to WiFi, the board runs a **unique goal routine** whenever the selected team scores.  
- Ensure the board is within WiFi range for this feature.

---

## Barebones PCB vs Full Assembled Kit

### Barebones PCB
- Requires manual assembly: includes the PCB with all the electronics soldered onto it, requires a custom shell.  
- Includes the firmware files in `Firmware_Code/` flashed to the board.  
- Follow the WiFi connection process above.  
- Once assembled and powered, usage is identical to the full kit.

### Full Assembled Kit
- Already assembled with 3D-printed shell and LEDs.  
- Plug in USB power and follow WiFi setup if needed.  
- Use buttons for brightness, colours, and routines as described above.

---

## Flashing the Firmware

- Use **Thonny** or **Arduino Labs for MicroPython** to copy `.py` and `.txt` files directly onto the ESP32.  
- Ensure USB drivers for the ESP32 are installed.  
- Refer to `Firmware_Code/` for all main files.
- Refer to `docs/flashin.md` for instructions on how to flash the firmware.

---

## License

This firmware is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.