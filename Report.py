"""Report generation from session logs."""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict


def load_session(path: str) -> List[Dict]:
    """Load a JSONL session log."""
    events = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                events.append(json.loads(line))
    return events


def generate_report(session_path: str, fmt: str = "markdown",
                    output_path: str = "report.md") -> None:
    """Generate a report from a session log."""
    events = load_session(session_path)
    if fmt == "markdown":
        content = _render_markdown(events, session_path)
    elif fmt == "json":
        content = json.dumps(events, indent=2, default=str)
    else:
        content = _render_text(events)
    Path(output_path).write_text(content)


def _render_markdown(events: List[Dict], session_path: str) -> str:
    lines = [
        "# WiFiTest Security Assessment Report",
        "",
        f"**Generated:** {datetime.utcnow().isoformat()}",
        f"**Session Log:** {session_path}",
        "",
        "## Executive Summary",
        "",
        "This report summarizes findings from an authorized WiFi security test.",
        "",
        "## Session Timeline",
        "",
    ]
    for ev in events:
        ts = ev.get("timestamp", "")
        etype = ev.get("type", "unknown")
        desc = _describe_event(ev)
        lines.append(f"- **{ts}** [{etype}] {desc}")
    lines.append("")
    lines.append("## Recommendations")
    lines.append("")
    lines.append("- Review captive-portal detection on client devices.")
    lines.append("- Disable automatic connection to open networks.")
    lines.append("- Implement 802.1X/EAP for enterprise networks.")
    lines.append("- Educate users on Evil Twin risks.")
    lines.append("")
    return "\n".join(lines)


def _describe_event(ev: Dict) -> str:
    etype = ev.get("type", "")
    if etype == "attack_started":
        return f"Attack '{ev.get('mode')}' launched against SSID '{ev.get('ssid')}'"
    if etype == "client_connected":
        return f"Client {ev.get('client_mac')} connected"
    if etype == "authorization_confirmed":
        return f"Operator {ev.get('operator')} confirmed authorization"
    return str(ev)
