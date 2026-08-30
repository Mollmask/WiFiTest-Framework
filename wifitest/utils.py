"""Shared utilities."""
import subprocess
import os
from typing import Optional


def require_root() -> bool:
    """Check if running as root."""
    return os.geteuid() == 0


def run_cmd(cmd: list, timeout: int = 10) -> tuple:
    """Run a command, return (stdout, stderr, returncode)."""
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        return "", "timeout", -1
    except FileNotFoundError:
        return "", f"command not found: {cmd[0]}", -1


def validate_ssid(ssid: str) -> bool:
    """Basic SSID validation."""
    if not ssid or len(ssid) > 32:
        return False
    return True


def sanitize_for_log(value: str) -> str:
    """Remove potentially sensitive content from log values."""
    sensitive = ["password", "passwd", "secret", "token", "key"]
    lower = value.lower()
    for s in sensitive:
        if s in lower:
            return "***REDACTED***"
    return value
