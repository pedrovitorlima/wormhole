import wifi
import ssl

import socketpool
import constants

class WifiManager:
    def connect(self):
        print("Trying to connect to:", constants.WIFI_SSID)
        wifi.radio.connect(ssid=constants.WIFI_SSID, password=constants.WIFI_PASSWORD)
        print("Connected!", wifi.radio.ipv4_address)
        return socketpool.SocketPool(wifi.radio), ssl.create_default_context()
        
