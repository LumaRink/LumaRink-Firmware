from wifi_manager import WifiManager
import uasyncio as asyncio
from machine import reset

async def setup_wifi(ap_name="WiFiManager", ap_password="wifimanager"):
    """
    Set up WiFi connection. If already connected, returns the manager.
    Otherwise, starts a captive portal in AP mode.

    Args:
        ap_name (str): SSID for the AP if portal mode is needed.
        ap_password (str): Password for the AP if portal mode is needed.

    Returns:
        tuple: (WifiManager instance, bool)
               Bool is True if WiFi is connected, False if portal started.
    """
    wm = WifiManager(ap_ssid=ap_name, ap_password=ap_password)
    print(f"[WiFiFunctions] Setting up WiFi AP: {ap_name}")

    # Attempt to connect to known WiFi credentials
    wm.connect()
    if wm.is_connected():
        print("[WiFiFunctions] Already connected to WiFi")
        print(f"[WiFiFunctions] Network config: {wm.get_address()}")
        return wm, True

    # If not connected, start AP portal for configuration
    print("[WiFiFunctions] Starting captive portal (AP mode)...")
    asyncio.create_task(wm.web_server())  # Run portal asynchronously
    return wm, False

async def reset_wifi(wm, ap_name="WiFiManager", ap_password="wifimanager"):
    """
    Reset stored WiFi credentials and relaunch AP portal.

    Args:
        wm (WifiManager): Current WifiManager instance.
        ap_name (str): SSID for the AP if portal mode is needed.
        ap_password (str): Password for the AP if portal mode is needed.

    Returns:
        tuple: (WifiManager instance, bool)
               Bool is True if WiFi is connected, False if portal started.
    """
    print("[WiFiFunctions] Resetting WiFi credentials...")

    if wm:
        try:
            wm.disconnect()          # Disconnect from current network
            wm.delete_credentials()  # Remove stored WiFi credentials
            reset()                  # Restart the board to apply changes
        except Exception as e:
            print(f"[WiFiFunctions] Error during reset: {e}")

    print("[WiFiFunctions] WiFi credentials reset. Relaunching AP portal...")
    return await setup_wifi(ap_name=ap_name, ap_password=ap_password)