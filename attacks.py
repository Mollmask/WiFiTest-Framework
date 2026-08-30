"""Attack mode dispatcher."""
from wifitest.attacks.evil_twin import run_evil_twin
from wifitest.attacks.karma import run_karma
from wifitest.attacks.known_beacons import run_known_beacons
from wifitest.logger import SessionLogger


_ATTACKS = {
    "evil_twin": run_evil_twin,
    "karma": run_karma,
    "known_beacons": run_known_beacons,
}


def run_attack(mode: str, **kwargs) -> None:
    """Dispatch to the appropriate attack module."""
    if mode not in _ATTACKS:
        raise ValueError(f"Unknown attack mode: {mode}. Choose from {list(_ATTACKS)}")
    logger = SessionLogger()
    logger.event("attack_started", mode=mode, **{k: v for k, v in kwargs.items()
                                                  if k != "beacon_list"})
    try:
        _ATTACKS[mode](logger=logger, **kwargs)
    except KeyboardInterrupt:
        logger.event("attack_stopped", mode=mode, reason="user_interrupt")
    finally:
        logger.close()
