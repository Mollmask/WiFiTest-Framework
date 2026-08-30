"""Main CLI entry point for WiFiTest."""
import sys
import click
from rich.console import Console
from wifitest import __version__, WARNING_BANNER
from wifitest.authorize import require_authorization
from wifitest.adapter import list_adapters
from wifitest.scanner import scan_networks
from wifitest.attacks import run_attack
from wifitest.reporter import generate_report

console = Console()


@click.group()
@click.option("--yes", "-y", is_flag=True, help="Skip authorization prompt (use with caution).")
@click.pass_context
def main(ctx, yes):
    """WiFiTest - Authorized WiFi security testing framework."""
    console.print(WARNING_BANNER, style="bold red")
    if not yes:
        if not require_authorization():
            console.print("[red]Authorization declined. Exiting.[/red]")
            sys.exit(1)
    ctx.ensure_object(dict)


@main.command()
def version():
    """Show version information."""
    console.print(f"WiFiTest {__version__}")


@main.command()
def adapters():
    """List available wireless adapters."""
    adapter_list = list_adapters()
    if not adapter_list:
        console.print("[yellow]No wireless adapters found.[/yellow]")
        return
    console.print(f"\n[bold green]Found {len(adapter_list)} adapter(s):[/bold green]\n")
    for idx, adapter in enumerate(adapter_list, 1):
        console.print(f"  [cyan]{idx}.[/cyan] {adapter['name']} "
                      f"([dim]{adapter['phy']}[/dim]) "
                      f"monitor={adapter.get('monitor', False)} "
                      f"inject={adapter.get('injection', False)}")


@main.command()
@click.option("--interface", "-i", required=True, help="Wireless interface to scan with.")
@click.option("--duration", "-d", default=10, type=int, help="Scan duration in seconds.")
def scan(interface, duration):
    """Scan for nearby wireless networks."""
    console.print(f"\n[bold]Scanning with {interface} for {duration}s...[/bold]\n")
    networks = scan_networks(interface, duration)
    if not networks:
        console.print("[yellow]No networks detected.[/yellow]")
        return
    console.print(f"\n[bold green]Found {len(networks)} network(s):[/bold green]\n")
    for idx, net in enumerate(networks, 1):
        enc = net.get("encryption", "OPEN")
        console.print(f"  [cyan]{idx:2d}.[/cyan] [bold]{net['ssid']:<30}[/bold] "
                      f"ch={net['channel']:<3} sig={net['signal']:>4}dBm "
                      f"enc={enc}")


@main.command()
@click.option("--interface", "-i", required=True, help="Wireless interface.")
@click.option("--ssid", "-s", required=True, help="Target SSID to clone.")
@click.option("--channel", "-c", default=6, type=int, help="Channel for rogue AP.")
@click.option("--scenario", type=click.Choice(["router-update", "login", "none"]),
              default="none", help="Captive portal scenario.")
def evil_twin(interface, ssid, channel, scenario):
    """Launch an Evil Twin attack against a target SSID."""
    console.print(f"\n[bold red]Launching Evil Twin:[/bold red] SSID='{ssid}' ch={channel}")
    run_attack("evil_twin", interface=interface, ssid=ssid,
               channel=channel, scenario=scenario)


@main.command()
@click.option("--interface", "-i", required=True, help="Wireless interface.")
def karma(interface):
    """Launch KARMA attack (respond to all probe requests)."""
    console.print(f"\n[bold red]Launching KARMA mode on {interface}[/bold red]")
    run_attack("karma", interface=interface)


@main.command()
@click.option("--interface", "-i", required=True, help="Wireless interface.")
@click.option("--list", "beacon_list", type=click.Path(exists=True),
              help="File with custom SSID list (one per line).")
def known_beacons(interface, beacon_list):
    """Broadcast known/common SSIDs to test client auto-connect."""
    console.print(f"\n[bold red]Launching Known Beacons on {interface}[/bold red]")
    run_attack("known_beacons", interface=interface, beacon_list=beacon_list)


@main.command()
@click.option("--session", required=True, type=click.Path(exists=True),
              help="Session log JSON file.")
@click.option("--format", "fmt", type=click.Choice(["markdown", "json", "text"]),
              default="markdown", help="Output format.")
@click.option("--output", "-o", default="report.md", help="Output file path.")
def report(session, fmt, output):
    """Generate a report from a session log."""
    generate_report(session, fmt, output)
    console.print(f"[green]Report written to {output}[/green]")


@main.command()
def interactive():
    """Step-by-step interactive guided mode for beginners."""
    from wifitest.interactive import run_interactive
    run_interactive()


if __name__ == "__main__":
    main()
