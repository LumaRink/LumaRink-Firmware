# WiFi Setup for LumaRink Firmware

This guide explains how to connect your LumaRink 5x5 LED board to your WiFi network so it can access optional features like live NHL score updates.

## Requirements
- A computer, phone, or tablet with WiFi  
- The ESP32 board running LumaRink firmware  

## Steps to Connect to WiFi

1. **Power on the ESP32 board** via USB.  

2. **Look for the LumaRink access point** on your WiFi device.  
   - The network name (SSID) will be `LumaRink`.  
   - The password is also `LumaRink`.  
   - **If the access point does not appear**, press and hold the **brightness button** on the board for 5 seconds or longer.  
     This will force the device to reboot into Access Point mode.  

3. **Connect your device** (phone, tablet, or computer) to this WiFi network.  

4. **Open a web browser** and go to the following address:
 - http://192.168.4.1
>  This is the ESP32’s built-in configuration page where you can enter your local WiFi credentials.

5. **Follow the on-screen instructions** to enter your local WiFi network name (SSID) and password.  

6. **Save the settings** and allow the board to reconnect to your WiFi.  

7. **Verify the connection**:  
   - The LED matrix may display a confirmation pattern once connected.  
   - Optional features, such as live NHL score updates, will now be active.

## Notes
- This setup only needs to be done **once** unless you change WiFi networks.  
- Make sure your WiFi credentials are correct — the board will not connect if the SSID or password is incorrect.  
- If the board does not connect, it may be out of range of your WiFi network — move it closer to your router and try again.
