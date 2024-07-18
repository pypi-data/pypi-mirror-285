"""
maix.network.wifi module
"""
from __future__ import annotations
import maix._maix.err
__all__ = ['AP_Info', 'Wifi', 'list_devices']
class AP_Info:
    bssid: str
    channel: int
    frequency: int
    rssi: int
    security: str
    ssid: list[int]
    def ssid_str(self) -> str:
        """
        WiFi AP info ssid_str
        """
class Wifi:
    def __init__(self, iface: str = 'wlan0') -> None:
        ...
    def connect(self, ssid: str, password: str, wait: bool = True, timeout: int = 60) -> maix._maix.err.Err:
        """
        Connect to WiFi AP.
        
        Args:
          - ssid: SSID of AP
          - password: password of AP, if no password, leave it empty.
          - wait: wait for got IP or failed or timeout.
          - timeout: connect timeout internal, unit second.
        
        
        Returns: If success, return err.Err.ERR_NONE, else means failed.
        """
    def disconnect(self) -> maix._maix.err.Err:
        """
        Disconnect from WiFi AP.
        
        Returns: If success, return err.Err.ERR_NONE, else means failed.
        """
    def get_gateway(self) -> str:
        """
        Get current WiFi ip
        
        Returns: ip, string type, if network not connected, will return empty string.
        """
    def get_ip(self) -> str:
        """
        Get current WiFi ip
        
        Returns: ip, string type, if network not connected, will return empty string.
        """
    def get_mac(self) -> str:
        """
        Get current WiFi MAC address
        
        Returns: ip, string type.
        """
    def get_scan_result(self) -> list[AP_Info]:
        """
        Get WiFi scan AP info.
        
        Returns: wifi.AP_Info list.
        """
    def get_ssid(self, from_cache: bool = True) -> str:
        """
        Get current WiFi SSID
        
        Args:
          - from_cache: if true, will not read config from file, direct use ssid in cache.
        attention, first time call this method will auto matically read config from file, and if call connect method will set cache.
        
        
        Returns: SSID, string type.
        """
    def is_connected(self) -> bool:
        """
        See if WiFi is connected to AP.
        
        Returns: If connected return true, else false.
        """
    def start_scan(self) -> maix._maix.err.Err:
        """
        WiFi start scan AP info around in background.
        
        Returns: If success, return err.Err.ERR_NONE, else means failed.
        """
    def stop_scan(self) -> None:
        """
        Stop WiFi scan AP info.
        """
def list_devices() -> list[str]:
    """
    List WiFi interfaces
    
    Returns: WiFi interface list, string type
    """
