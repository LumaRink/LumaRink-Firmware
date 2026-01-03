import network
import socket
import re
import time
import os
import uasyncio as asyncio

class WifiManager:
    """
    WiFi Manager for MicroPython devices.
    Handles:
      - Station mode connections (STA_IF)
      - Access Point (AP_IF) for captive portal setup
      - Credential storage/retrieval
    """

    def __init__(self, ap_ssid='WiFiManager', ap_password='wifimanager'):
        """
        Initialize WifiManager with AP credentials and internal state.
        """
        self.ap_ssid = ap_ssid
        self.ap_password = ap_password
        self.ap_authmode = 3               # WPA2
        self.wifi_credentials = 'wifi.dat'

        # Station interface for connecting to existing WiFi
        self.wlan_sta = network.WLAN(network.STA_IF)
        self.wlan_sta.active(True)

        # Access Point interface for captive portal
        self.wlan_ap = network.WLAN(network.AP_IF)
        self.wlan_ap.active(False)

    # ---------------- WiFi Connection Methods ----------------
    def connect(self):
        """
        Attempt to connect to stored WiFi credentials.
        Loads saved SSID/password pairs and tries them in order.
        """
        if self.wlan_sta.isconnected():
            print("[WiFiManager] Already connected.")
            return

        profiles = self.read_credentials()
        print(f"[WiFiManager] Loaded profiles: {profiles}")

        for ssid, password in profiles.items():
            if self.wifi_connect(ssid, password):
                return
        print("[WiFiManager] No working credentials found.")

    def disconnect(self):
        """
        Disconnect from current WiFi network if connected.
        """
        if self.wlan_sta.isconnected():
            self.wlan_sta.disconnect()

    def is_connected(self):
        """
        Returns True if currently connected to a WiFi network.
        """
        return self.wlan_sta.isconnected()

    def get_address(self):
        """
        Returns IP configuration tuple: (IP, subnet, gateway, DNS)
        """
        return self.wlan_sta.ifconfig()

    # ---------------- Credential Storage ----------------
    def write_credentials(self, ssid, password):
        """
        Save a WiFi SSID/password pair to the local file.
        """
        try:
            profiles = self.read_credentials()
            profiles[ssid] = password
            with open(self.wifi_credentials, 'w') as file:
                for s, p in profiles.items():
                    file.write(f'{s};{p}\n')
            print(f"[WiFiManager] Credentials saved for {ssid}.")
        except Exception as e:
            print(f"[WiFiManager] Failed to write credentials: {e}")

    def read_credentials(self):
        """
        Read saved WiFi credentials from file.
        Returns a dictionary {ssid: password}.
        """
        try:
            with open(self.wifi_credentials) as file:
                return dict(line.strip().split(';') for line in file if ';' in line)
        except OSError:
            return {}

    def delete_credentials(self):
        """
        Delete stored WiFi credentials file.
        """
        try:
            os.remove(self.wifi_credentials)
            print("[WiFiManager] WiFi credentials deleted.")
        except OSError:
            print("[WiFiManager] No WiFi credentials file found.")

    # ---------------- Connection Helper ----------------
    def wifi_connect(self, ssid, password):
        """
        Attempt to connect to a specific SSID with password.
        Returns True if successful.
        """
        print(f"[WiFiManager] Trying to connect to: {ssid}")
        self.wlan_sta.connect(ssid, password)
        for _ in range(50):  # Retry for ~5 seconds
            if self.wlan_sta.isconnected():
                ip = self.wlan_sta.ifconfig()[0]
                print(f"[WiFiManager] Connected to {ssid}. IP: {ip}")
                return True
            time.sleep_ms(100)
        print(f"[WiFiManager] Connection to {ssid} failed.")
        self.wlan_sta.disconnect()
        return False

    # ---------------- Captive Portal ----------------
    async def web_server(self):
        """
        Start a captive portal for WiFi configuration.
        Runs asynchronously using uasyncio.
        """
        self.wlan_ap.active(False)
        await asyncio.sleep_ms(100)
        self.wlan_ap.active(True)
        self.wlan_ap.config(essid=self.ap_ssid, password=self.ap_password, authmode=self.ap_authmode)

        server_socket = socket.socket()
        server_socket.setblocking(False)
        try:
            server_socket.bind(('', 80))
            server_socket.listen(1)
            print(f"[WiFiManager] Captive portal started at 192.168.4.1")

            while not self.wlan_sta.isconnected():
                try:
                    conn, addr = server_socket.accept()
                except OSError:
                    await asyncio.sleep(0.1)
                    continue

                try:
                    conn.settimeout(2.0)
                    request = conn.recv(1024).decode()
                    networks = [net[0].decode() for net in self.wlan_sta.scan()]
                    if request and 'POST /' in request:
                        self.handle_configure(conn, request, networks)
                    else:
                        conn.send(self.get_html(ssids=networks))
                except Exception as e:
                    print("[WiFiManager] Socket error:", e)
                finally:
                    conn.close()

                await asyncio.sleep(0)

        finally:
            try:
                server_socket.close()
            except Exception:
                pass
            self.wlan_ap.active(False)
            await asyncio.sleep_ms(100)
            print("[WiFiManager] Captive portal closed")

    def handle_configure(self, conn, request, networks):
        """
        Handle POST request from captive portal.
        Extracts SSID/password and attempts connection.
        """
        match = re.search('ssid=([^&]*)&password=(.*)', request)
        if match:
            ssid = match.group(1).replace('%3F', '?').replace('%21', '!')
            password = match.group(2).replace('%3F', '?').replace('%21', '!')
            success = self.wifi_connect(ssid, password)
            if success:
                self.write_credentials(ssid, password)
            conn.send(self.get_html(success=success, ssids=networks))
        else:
            conn.send(self.get_html(success=False, ssids=networks))

    def get_html(self, success=None, ssids=None):
        """
        Generate HTML for captive portal page.
        Shows form for SSID/password or connection status.
        """
        html = [
            "<html><head><title>WiFi Manager</title>",
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">",
            "<style>body{font-family:Arial,sans-serif;margin:0;padding:20px}h1{color:#333}"
            "form{max-width:300px}label{display:block;margin-top:10px}input,select{width:100%;padding:5px;margin-top:5px}"
            "input[type=\"submit\"]{background-color:#4CAF50;color:white;border:none;padding:10px;cursor:pointer}</style>",
            "</head><body><h1>WiFi Manager</h1>"
        ]

        if success is None:
            html.append("<form action=\"/\" method=\"post\">")
            html.append("<label for=\"ssid\">SSID:</label>")
            if ssids:
                html.append("<select id=\"ssid\" name=\"ssid\">")
                for ssid in ssids:
                    html.append(f"<option value=\"{ssid}\">{ssid}</option>")
                html.append("</select>")
            else:
                html.append("<input type=\"text\" id=\"ssid\" name=\"ssid\" required>")
            html.extend([
                "<label for=\"password\">Password:</label>",
                "<input type=\"password\" id=\"password\" name=\"password\" required>",
                "<input type=\"submit\" value=\"Connect\"></form>"
            ])
        elif success:
            html.append("<p>Successfully connected to WiFi.</p>")
        else:
            html.append("<p>Failed to connect. Please try again.</p>")

        html.append("</body></html>")
        return ''.join(html)