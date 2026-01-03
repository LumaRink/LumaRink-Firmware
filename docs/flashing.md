# Flashing LumaRink Firmware

This guide shows how to copy the LumaRink firmware to your ESP32 board in case you need to recover or update it.

## Requirements
- A computer with a USB port  
- USB-C cable to connect to the ESP32  
- MicroPython IDE such as **Thonny** or **Arduino Labs for MicroPython**  
- USB drivers installed for the ESP32 (required for your computer to detect the board)

## Steps to Flash the Firmware

1. **Ensure USB drivers are installed** for the ESP32 so your computer can detect the board.  
2. **Connect the ESP32 board** to your computer using the USB-C cable.  
3. **Open your MicroPython IDE** (Thonny or Arduino Labs).  
4. **Locate the ESP32 device** in your IDE.  
   - Make sure it is recognized as a connected board.  
   - Verify or select the correct COM port for your ESP32 if your IDE asks.  
5. **Copy the firmware files**:  
   - Open the `Firmware_Code` folder.  
   - Copy all `.py` and `.txt` files from `Firmware_Code` directly into the ESP32 using the IDE.  
6. **Run the firmware**:  
   - **Thonny:** Make sure `main.py` is selected and click **Run Current Script**.  
   - **Arduino Labs for MicroPython:** Simply click **Run** — no file selection is needed.  
7. **Verify the board is running**:  
   - The LED matrix should display the default routine automatically.

## Notes
- LumaRink boards are **pre-flashed**, so this is only necessary if you need to recover or update the firmware.  
- Make sure not to delete any files required by the board when copying.  
- For WiFi setup or optional NHL features, see `docs/wifi-setup.md`.