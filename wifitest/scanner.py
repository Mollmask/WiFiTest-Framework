"""Network scanning via airodump-ng or iw scan."""
import subprocess
import re
import time
import tempfile
import os
from typing import List, Dict


def scan_networks(interface: str, duration: int = 10) -> List[Dict]:
    """Scan for nearby networks. Returns list of network dicts."""
    # Try airodump-ng first (more detailed), fall back to iw
    try:
        return _scan_airodump(interface, duration)
    except FileNotFoundError:
        return _scan_iw(interface)


def _scan_airodump(interface: str, duration: int) -> List[Dict]:
    """Use airodump-ng to scan."""
    with tempfile.TemporaryDirectory() as tmpdir:
        prefix = os.path.join(tmpdir, "scan")
        proc = subprocess.Popen(
            ["airodump-ng", "-w", prefix, "--output-format", "csv", interface],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        time.sleep(duration)
        proc.terminate()
        proc.wait(timeout=5)
        csv_file = f"{prefix}-01.csv"
        if not os.path.exists(csv_file):
            return []
        return _parse_airodump_csv(csv_file)


def _parse_airodump_csv(path: str) -> List[Dict]:
    """Parse airodump-ng CSV output."""
    networks = []
    with open(path, "r", errors="ignore") as f:
        in_ap_section = False
        for line in f:
            line = line.strip()
            if line.startswith("BSSID"):
                in_ap_section = True
                continue
            if not in_ap_section:
                continue
            if line.startswith("Station"):
                break
            parts = [p.strip() for p in line.split(",")]
            if len(parts) < 14:
                continue
            ssid = parts[13] if len(parts) > 13 else "<hidden>"
            networks.append({
                "bssid": parts[0],
                "ssid": ssid if ssid else "<hidden>",
                "channel": int(parts[3]) if parts[3].strip() else 0,
                "signal": int(parts[8]) if parts[8].strip() else -100,
                "encryption": parts[5] if len(parts) > 5 else "UNKNOWN",
            })
    return networks


def _scan_iw(interface: str) -> List[Dict]:
    """Fallback: use iw scan."""
    try:
        out = subprocess.run(["iw", "dev", interface, "scan"],
                             capture_output=True, text=True, timeout=15)
        return _parse_iw_scan(out.stdout)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def _parse_iw_scan(output: str) -> List[Dict]:
    """Parse iw scan output."""
    networks = []
    current = {}
    for line in output.splitlines():
        line = line.strip()
        if line.startswith("BSS"):
            if current and current.get("ssid"):
                networks.append(current)
            current = {"bssid": line.split()[1]}
        elif line.startswith("SSID:"):
            current["ssid"] = line.split(":", 1)[1].strip()
        elif line.startswith("freq:"):
            freq = int(line.split(":")[1].strip())
            current["channel"] = _freq_to_channel(freq)
        elif line.startswith("signal:"):
            sig = line.split(":")[1].strip().replace("dBm", "").strip()
            current["signal"] = int(sig)
    if current and current.get("ssid"):
        networks.append(current)
    return networks


def _freq_to_channel(freq: int) -> int:
    """Convert frequency in MHz to channel number."""
    if freq == 2484:
        return 14
    if freq < 2484:
        return (freq - 2407) // 5
    return (freq - 5000) // 5
