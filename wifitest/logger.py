"""Structured JSON logging for audit trails."""
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional


class SessionLogger:
    """Append-only JSON-lines logger for security testing sessions."""

    def __init__(self, log_dir: str = "./logs", session_id: Optional[str] = None):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.session_id = session_id or datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"session_{self.session_id}.jsonl"
        self._write({"type": "session_start", "session_id": self.session_id,
                     "timestamp": self._now()})

    def _now(self) -> str:
        return datetime.now(timezone.utc).isoformat()

    def event(self, event_type: str, **kwargs: Any) -> None:
        """Log an event. kwargs are stored as structured data."""
        record = {
            "type": event_type,
            "session_id": self.session_id,
            "timestamp": self._now(),
            **kwargs,
        }
        # SECURITY: Never log passwords or sensitive credentials
        sanitized = {k: v for k, v in record.items()
                     if k.lower() not in ("password", "passwd", "secret", "token")}
        self._write(sanitized)

    def _write(self, record: Dict) -> None:
        with open(self.log_file, "a") as f:
            f.write(json.dumps(record, default=str) + "\n")

    def close(self) -> None:
        self._write({"type": "session_end", "session_id": self.session_id,
                     "timestamp": self._now()})

    @property
    def path(self) -> Path:
        return self.log_file
