"""Interactive guided mode for beginners."""
from rich.console import Console
from rich.prompt import Prompt, IntPrompt, Confirm
from wifitest.adapter import list_adapters, enable_monitor_mode
from wifitest.scanner import scan_networks
from wifitest.attacks import run_attack
from wifitest.logger import SessionLogger

console = Console()


def run_interactive():
    """Step-by-step guided workflow."""
    console.print("\n[bold cyan]=== WiFiTest Interactive Mode ===[/bold cyan]\n")

    # Step 1: Authorization
    console.print("[bold]Step 1: Authorization[/bold]")
    if not Confirm.ask("I confirm I am authorized to test the target network", default=False):
        console.print("[red]Authorization required. Exiting.[/red]")
        return

    # Step 2: Adapter selection
    console.print("\n[bold]Step 2: Select wireless adapter[/bold]")
    adapters = list_adapters()
    if not adapters:
        console.print("[red]No adapters found.[/red]")
        return
    for i, a in enumerate(adapters, 1):
        console.print(f"  {i}. {a['name']} ({a['phy']})")
    choice = IntPrompt.ask("Select adapter", default=1) - 1
    iface = adapters[choice]["name"]
    console.print(f"[green]Using {iface}[/green]")

    # Step 3: Scan
    console.print("\n[bold]Step 3: Scanning for networks...[/bold]")
    duration = IntPrompt.ask("Scan duration (seconds)", default=10)
    networks = scan_networks(iface, duration)
    if not networks:
        console.print("[yellow]No networks found.[/yellow]")
        return
    for i, n in enumerate(networks, 1):
        console.print(f"  {i:2d}. {n['ssid']:<30} ch={n['channel']} sig={n['signal']}dBm")

    # Step 4: Target selection
    console.print("\n[bold]Step 4: Select target[/bold]")
    target_idx = IntPrompt.ask("Target number", default=1) - 1
    target = networks[target_idx]
    if not Confirm.ask(f"Confirm target: {target['ssid']} (you have permission?)", default=False):
        console.print("[red]Aborted.[/red]")
        return

    # Step 5: Attack mode
    console.print("\n[bold]Step 5: Select attack mode[/bold]")
    modes = ["evil_twin", "karma", "known_beacons"]
    for i, m in enumerate(modes, 1):
        console.print(f"  {i}. {m}")
    mode_idx = IntPrompt.ask("Mode", default=1) - 1
    mode = modes[mode_idx]

    # Step 6: Scenario
    scenario = "none"
    if mode == "evil_twin":
        console.print("\n[bold]Optional captive portal scenario:[/bold]")
        scenarios = ["none", "router-update", "login"]
        for i, s in enumerate(scenarios, 1):
            console.print(f"  {i}. {s}")
        s_idx = IntPrompt.ask("Scenario", default=1) - 1
        scenario = scenarios[s_idx]

    # Step 7: Launch
    console.print(f"\n[bold red]Launching {mode} against '{target['ssid']}'...[/bold red]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")

    logger = SessionLogger()
    try:
        run_attack(mode, interface=iface, ssid=target["ssid"],
                   channel=target["channel"], scenario=scenario)
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopped by user.[/yellow]")
    finally:
        logger.close()
        console.print(f"[green]Session log: {logger.path}[/green]")
