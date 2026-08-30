"""Wireless adapter detection and capability checks."""
import subprocess
import re
from typing import List, Dict, Optional


def _run(cmd: List[str], timeout: int = 5) -> str:
    """Run a shell command and return stdout."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def list_adapters() -> List[Dict[str, str]]:
    """Detect wireless adapters and their capabilities.

    Returns a list of dicts with keys: name, phy, monitor, injection.
    """
    adapters = []
    iw_output = _run(["iw", "dev"])
    # Parse "Interface wlan0" lines
    for match in re.finditer(r"Interface\s+(\S+)", iw_output):
        iface = match.group(1)
        phy_output = _run(["iw", "dev", iface, "info"])
        phy = ""
        for line in phy_output.splitlines():
            if line.strip().startswith("wiphy"):
                phy = line.strip().split()[-1]
                break
        adapters.append({
            "name": iface,
            "phy": phy,
            "monitor": _supports_monitor(iface),
            "injection": _supports_injection(iface),
        })
    return adapters


def _supports_monitor(iface: str) -> bool:
    """Check if interface supports monitor mode."""
    out = _run(["iw", "dev", iface, "info"])
    return "type monitor" in out.lower() or "monitor" in out.lower()


def _supports_injection(iface: str) -> bool:
    """Heuristic: assume injection if iw list shows the phy supports it."""
    out = _run(["iw", "list"])
    return "TX frame injection" in out


def enable_monitor_mode(iface: str, mon_name: Optional[str] = None) -> str:
    """Enable monitor mode on an interface. Returns the monitor interface name."""
    mon_name = mon_name or f"{iface}mon"
    _run(["iw", "dev", iface, "interface", "add", mon_name, "type", "monitor"])
    _run(["ip", "link", "set", mon_name, "up"])
    return mon_name


def disable_monitor_mode(mon_iface: str) -> None:
    """Remove a monitor-mode interface."""
    _run(["iw", "dev", mon_iface, "del"])
