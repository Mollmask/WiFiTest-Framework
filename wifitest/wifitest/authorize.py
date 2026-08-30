"""Authorization gates - ensures tester has explicit permission."""
import sys
from rich.console import Console
from rich.prompt import Confirm

console = Console()

AUTHORIZATION_TEXT = """
Before proceeding, you MUST confirm ALL of the following:

  1. You own the network(s) being tested, OR
  2. You have explicit WRITTEN permission from the network owner, OR
  3. This is a controlled lab environment you operate.

  4. You will NOT use this tool against any network without authorization.
  5. You understand that unauthorized access is illegal in most jurisdictions.
  6. All findings will be used only for defensive security improvement.
"""


def require_authorization() -> bool:
    """Prompt the user to confirm authorization. Returns True if confirmed."""
    console.print(AUTHORIZATION_TEXT, style="bold yellow")
    try:
        return Confirm.ask("[bold red]Do you confirm you are authorized to perform this test?[/bold red]",
                           default=False)
    except (EOFError, KeyboardInterrupt):
        return False


def log_authorization(logger, target_ssid: str, operator: str) -> None:
    """Record authorization confirmation in the session log."""
    logger.event("authorization_confirmed", operator=operator, target_ssid=target_ssid)
