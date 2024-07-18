"""
SporeStack CLI: `sporestack`
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import TYPE_CHECKING, Optional, Union

import typer

from .constants import Currency, Provider

if sys.version_info >= (3, 9):  # pragma: nocover
    from typing import Annotated
else:  # pragma: nocover
    from typing_extensions import Annotated

if TYPE_CHECKING:
    from . import api
    from .api_client import APIClient
    from .models import Invoice


HELP = """
SporeStack Python CLI

Optional environment variables:
SPORESTACK_ENDPOINT
*or*
SPORESTACK_USE_TOR_ENDPOINT

TOR_PROXY (defaults to socks5://127.0.0.1:9050 which is fine for most)
"""

_home = os.getenv("HOME", None)
assert _home is not None, "Unable to detect $HOME environment variable?"
HOME = Path(_home)

SPORESTACK_DIR = Path(os.getenv("SPORESTACK_DIR", HOME / ".sporestack"))

# Try to protect files in ~/.sporestack
os.umask(0o0077)

cli = typer.Typer(help=HELP)

HOME = Path(_home)

token_cli = typer.Typer(help="Commands to interact with SporeStack tokens.")
cli.add_typer(token_cli, name="token")
server_cli = typer.Typer(help="Commands to interact with SporeStack servers.")
cli.add_typer(server_cli, name="server")

log = logging.getLogger(__name__)
_log_level = os.getenv("LOG_LEVEL", "warning").upper()
_numeric_log_level = getattr(logging, _log_level, None)
if _numeric_log_level is None:
    raise ValueError(f"LOG_LEVEL: {_log_level} is invalid. Aborting!")
assert isinstance(_numeric_log_level, int)
logging.basicConfig(level=_numeric_log_level)

DEFAULT_TOKEN = "primary"
DEFAULT_FLAVOR = "vps-1vcpu-1gb"
# Users may have a different key file, but this is the most common.
DEFAULT_SSH_KEY_FILE = HOME / ".ssh" / "id_rsa.pub"
DEFAULT_TOKEN_SSH_KEY_PRIVATE = Path("id_ed25519")
DEFAULT_TOKEN_SSH_KEY_PUBLIC = DEFAULT_TOKEN_SSH_KEY_PRIVATE.with_suffix(".pub")

# On disk format
TOKEN_VERSION = 1

WAITING_PAYMENT_TO_PROCESS = "Waiting for payment to process..."


def get_api_endpoint() -> str:
    from .api_client import CLEARNET_ENDPOINT, TOR_ENDPOINT

    api_endpoint = os.getenv("SPORESTACK_ENDPOINT", CLEARNET_ENDPOINT)
    if os.getenv("SPORESTACK_USE_TOR_ENDPOINT", None) is not None:
        api_endpoint = TOR_ENDPOINT
    return api_endpoint


def get_api_client() -> "APIClient":
    from .api_client import APIClient

    return APIClient(api_endpoint=get_api_endpoint())


def invoice_qr(invoice: "Invoice") -> None:
    import segno

    qr = segno.make(invoice.payment_uri)
    qr.terminal()


def normalize_ssh_key_file(ssh_key_file: Union[Path, None], token: str) -> Path:
    if ssh_key_file is None:
        token_specific_path = ssh_key_path(token)
        token_specific_key = token_specific_path / DEFAULT_TOKEN_SSH_KEY_PUBLIC
        if token_specific_key.exists():
            ssh_key_file = token_specific_key
        elif DEFAULT_SSH_KEY_FILE.exists():
            ssh_key_file = DEFAULT_SSH_KEY_FILE

    if ssh_key_file is None:
        typer.echo(
            "No SSH key specified with --ssh-key-file, nor was "
            f"{token_specific_key} or {DEFAULT_SSH_KEY_FILE} found.",
            err=True,
        )
        typer.echo("You can generate a SSH key with `ssh-key-gen`", err=True)
        raise typer.Exit(code=1)

    return ssh_key_file


@server_cli.command()
def launch(
    operating_system: Annotated[
        str,
        typer.Option(
            help=(
                "Example: debian-12 (Run `sporestack server operating-systems` for "
                "more options.)"
            ),
            show_default=False,
        ),
    ],
    provider: Annotated[
        Provider,
        typer.Option(help="Which provider to launch the server with."),
    ] = Provider.DIGITALOCEAN,
    region: Annotated[
        Optional[str],
        typer.Option(
            help=(
                "Leave unset for random region selection. Or run `sporestack server "
                "regions` for options."
            ),
            show_default=False,
        ),
    ] = None,
    flavor: Annotated[
        str, typer.Option(help="Run `sporestack server flavors` to see more options.")
    ] = DEFAULT_FLAVOR,
    autorenew: bool = typer.Option(
        False, help="Automatically renew server. (--days 7) recommended if using this."
    ),
    days: Annotated[
        Union[int, None],
        typer.Option(
            min=1,
            max=90,
            help=(
                "Initially fund the server to run for this many days. Use "
                "--autorenew if you don't want it to expire."
            ),
            show_default=False,
        ),
    ] = None,
    hostname: Annotated[
        str,
        typer.Option(
            help=(
                "Give the server a hostname to help remember what it's for. "
                "(Note: This is visible to us.)"
            )
        ),
    ] = "",
    ssh_key_file: Annotated[
        Union[Path, None],
        typer.Option(
            help=(
                "SSH key that the new server will allow to login as root. Defaults "
                "to the token-specific SSH key, or ~/.ssh/id_rsa.pub if the former "
                "was not found."
            ),
            show_default=False,
        ),
    ] = None,
    user_data_file: Annotated[
        Union[Path, None],
        typer.Option(
            help=("Path to load Cloud Init user data from."),
            show_default=False,
        ),
    ] = None,
    token: Annotated[
        str, typer.Option(help="Which token to launch the server with.")
    ] = DEFAULT_TOKEN,
    quote: bool = typer.Option(True, help="Require manual price confirmation."),
    wait: bool = typer.Option(
        True, help="Wait for server to be assigned an IP address."
    ),
) -> None:
    """Launch a server on SporeStack."""
    typer.echo(f"Launching server with token {token}...", err=True)
    _token = load_token(token)

    ssh_key_file = normalize_ssh_key_file(ssh_key_file=ssh_key_file, token=token)
    typer.echo(f"Using SSH key: {ssh_key_file}")

    from .client import Client

    client = Client(
        api_client=get_api_client(),
        client_token=_token,
        ssh_key=ssh_key_file.read_text(),
    )

    if quote:
        if days is None:
            raise ValueError("Can't give a quote unless --days is set!")
        quote_response = client.server_quote(
            days=days, flavor=flavor, provider=provider
        )

        msg = f"Is {quote_response.usd} for {days} day(s) of {flavor} okay?"
        typer.echo(msg, err=True)
        input("[Press ctrl+c to cancel, or enter to accept.]")

    if autorenew:
        typer.echo(
            "Server will be automatically renewed (from this token) to one week of expiration.",  # noqa: E501
            err=True,
        )
        typer.echo(
            "If using this feature, watch your token balance and server expiration closely!",  # noqa: E501
            err=True,
        )

    user_data = None
    if user_data_file is not None:
        user_data = user_data_file.read_text()

    server = client.token.launch_server(
        days=days,
        flavor=flavor,
        operating_system=operating_system,
        provider=provider,
        region=region,
        hostname=hostname,
        autorenew=autorenew,
        user_data=user_data,
    )

    if wait:
        tries = 60
        while tries > 0:
            response = server.info()
            if response.deleted_at > 0:
                typer.echo(
                    "Server creation failed, was deleted while waiting.", err=True
                )
                raise typer.Exit(code=1)
            if response.ipv4 != "":
                break
            typer.echo("Waiting for server to build...", err=True)
            tries = tries + 1
            # Waiting for server to spin up.
            time.sleep(10)

        if response.ipv4 == "":
            typer.echo("Server creation failed, tries exceeded.", err=True)
            raise typer.Exit(code=1)
        else:
            print_machine_info(response)

    if not wait:
        print_machine_info(server.info())
        return

    typer.echo("Consider adding the following to ~/.ssh/config...")

    config = (
        "\nHost {host}\n"
        "\tHostname {hostname}\n"
        f"\tIdentityFile {str(ssh_key_file).strip('.pub')}\n"
        "\tUser root\n"
        "\t # Remove this comment if you wish to connect via Tor. "
        "ProxyCommand nc -x localhost:9050 %h %p\n"
    )

    typer.echo("If you wish to connect with IPv4:")
    typer.echo(
        config.format(
            host=hostname if hostname != "" else response.ipv4, hostname=response.ipv4
        )
    )

    typer.echo("Or if you wish to connect with IPv6:")
    typer.echo(
        config.format(
            host=hostname if hostname != "" else response.ipv6, hostname=response.ipv6
        )
    )

    msg = (
        "If you've done that, you should be able to run `ssh {host}` "
        "to connect to the server."
    )
    if hostname != "":
        typer.echo(msg.format(host=hostname))
    else:
        typer.echo(msg.format(host=f"({response.ipv4} or {response.ipv6})"))


@server_cli.command()
def topup(
    hostname: str = "",
    machine_id: str = "",
    days: int = typer.Option(...),
    token: str = DEFAULT_TOKEN,
) -> None:
    """Extend an existing SporeStack server's lifetime."""

    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())

    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)

    _token = load_token(token)

    api_client.server_topup(machine_id=machine_id, days=days)

    typer.echo(f"Server topped up for {days} day(s)")


def token_path() -> Path:
    token_dir = SPORESTACK_DIR / "tokens"

    # Make it, if it doesn't exist already.
    token_dir.mkdir(exist_ok=True, parents=True)

    return token_dir


def ssh_key_path(token: str) -> Path:
    ssh_key_dir = SPORESTACK_DIR / "sshkey" / token

    # Make it, if it doesn't exist already.
    ssh_key_dir.mkdir(exist_ok=True, parents=True)

    return ssh_key_dir


def epoch_to_human(epoch: int) -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S %z", time.localtime(epoch))


def print_machine_info(info: "api.ServerInfo.Response") -> None:
    from rich.console import Console
    from rich.panel import Panel

    console = Console(width=None if sys.stdout.isatty() else 10**9)

    output = ""

    output = ""
    if info.ipv6 != "":
        output += f"IPv6: {info.ipv6}\n"
    else:
        output += "IPv6: (Not yet assigned)\n"
    if info.ipv4 != "":
        output += f"IPv4: {info.ipv4}\n"
    else:
        output += "IPv4: (Not yet assigned)\n"
    output += f"Provider: {info.provider}\n"
    output += f"Region: {info.region}\n"
    output += f"Flavor: {info.flavor_slug}\n"
    output += f"Token (keep this secret!): {info.token}\n"
    if info.deleted_at != 0:
        output += f"Server deleted at: {epoch_to_human(info.deleted_at)}\n"
        if info.deleted_by is not None:
            output += f"Server deleted by: {info.deleted_by.value}\n"
        if info.forgotten_at is not None:
            output += f"Server forgotten at: {info.forgotten_at}\n"
    else:
        msg = f"Running: {info.running}\n"
        if info.suspended_at is not None:
            msg = (
                "Running: Server is powered off because it is [bold]suspended[/bold].\n"
            )
        output += msg
        time_to_live = info.expiration - int(time.time())
        hours = time_to_live // 3600
        output += f"Server will be deleted in {hours} hours.\n"
        output += f"Expiration: {epoch_to_human(info.expiration)}\n"
        output += f"Autorenew: {info.autorenew}"

    title = f"Machine ID: [italic]{info.machine_id}[/italic] "
    if info.hostname != "":
        title += f"[bold]({info.hostname})[/bold]"
    else:
        title += "(No hostname set)"

    if info.deleted_at == 0:
        if info.autorenew:
            subtitle = "Server is set to automatically renew. Watch your token balance!"
        else:
            _expiration = epoch_to_human(info.expiration)
            subtitle = f"Server will expire: [italic]{_expiration}[/italic]"
    else:
        subtitle = "Server was [italic]deleted[/italic]."

    panel = Panel(output, title=title, subtitle=subtitle)

    console.print(panel)


@server_cli.command(name="list")
def server_list(
    token: str = DEFAULT_TOKEN,
    show_forgotten: Annotated[
        bool, typer.Option(help="Show deleted and forgotten servers.")
    ] = False,
    show_deleted: Annotated[bool, typer.Option(help="Show deleted servers.")] = True,
) -> None:
    """Lists a token's servers."""
    _token = load_token(token)

    from rich.console import Console
    from rich.table import Table

    from .api_client import APIClient

    console = Console(width=None if sys.stdout.isatty() else 10**9)

    table = Table(
        title=f"Servers for {token} ({_token})",
        show_header=True,
        header_style="bold magenta",
        caption=(
            "For more details on a server, run "
            "`sporestack server info --machine-id (machine id)`"
        ),
    )

    api_client = APIClient(api_endpoint=get_api_endpoint())

    server_infos = api_client.servers_launched_from_token(
        token=_token, include_forgotten=show_forgotten, include_deleted=show_deleted
    ).servers

    printed_machine_ids = []

    table.add_column("Machine ID [bold](Secret!)[/bold]", style="dim")
    table.add_column("Hostname")
    table.add_column("IPv4")
    table.add_column("IPv6")
    table.add_column("Expires At")
    table.add_column("Autorenew")

    for info in server_infos:
        typer.echo()

        expiration = epoch_to_human(info.expiration)
        if info.deleted_at:
            expiration = f"[bold]Deleted[/bold] at {epoch_to_human(info.deleted_at)}"

        table.add_row(
            info.machine_id,
            info.hostname,
            info.ipv4,
            info.ipv6,
            expiration,
            str(info.autorenew),
        )

        if info.suspended_at is not None:
            typer.echo(
                f"Warning: {info.machine_id} was suspended at {info.suspended_at}!",
                err=True,
            )

        printed_machine_ids.append(info.machine_id)

    console.print(table)
    typer.echo()


def _get_machine_id(machine_id: str, hostname: str, token: str) -> str:
    usage = "--hostname *OR* --machine-id must be set."

    if machine_id != "" and hostname != "":
        typer.echo(usage, err=True)
        raise typer.Exit(code=2)

    if machine_id != "":
        return machine_id

    if hostname == "":
        typer.echo(usage, err=True)
        raise typer.Exit(code=2)

    _token = load_token(token)

    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())

    candidates = api_client.servers_launched_from_token(
        token=_token, include_forgotten=False, hostname=hostname
    ).servers

    if len(candidates) == 1:
        return candidates[0].machine_id

    remaining_candidates = []
    for candidate in candidates:
        if candidate.deleted_at == 0:
            remaining_candidates.append(candidate)

    if len(remaining_candidates) == 1:
        return remaining_candidates[0].machine_id
    elif len(remaining_candidates) > 1:
        typer.echo(
            "Too many servers match that hostname. Please use --machine-id, instead.",
            err=True,
        )
        raise typer.Exit(code=1)

    typer.echo(
        f"Could not find any servers matching the hostname: {hostname}", err=True
    )
    raise typer.Exit(code=1)


@server_cli.command(name="info")
def server_info(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """Show information about the server."""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    print_machine_info(api_client.server_info(machine_id=machine_id))


@server_cli.command(name="json")
def server_info_json(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """Info on the server, in JSON format."""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    typer.echo(api_client.server_info(machine_id=machine_id).json())


@server_cli.command()
def start(hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN) -> None:
    """Boots the VM."""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.server_start(machine_id=machine_id)
    typer.echo(f"{hostname} started.")


@server_cli.command()
def stop(hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN) -> None:
    """Power off the server. (Not a graceful shutdown)"""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.server_stop(machine_id=machine_id)
    typer.echo(f"{hostname} stopped.")


@server_cli.command()
def autorenew_enable(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """Enable autorenew on a server."""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.autorenew_enable(machine_id=machine_id)
    typer.echo("Autorenew enabled.")


@server_cli.command()
def autorenew_disable(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """
    Disable autorenew on a server.
    """
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.autorenew_disable(machine_id=machine_id)
    typer.echo("Autorenew disabled.")


@server_cli.command()
def delete(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """Delete the server before its expiration."""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.server_delete(machine_id=machine_id)
    typer.echo(f"{machine_id} was destroyed.")


@server_cli.command()
def forget(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """Forget about a deleted server so that it doesn't show up in server list."""
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.server_forget(machine_id=machine_id)
    typer.echo(f"{machine_id} was forgotten.")


@server_cli.command()
def update_hostname(
    machine_id: str,
    hostname: Annotated[str, typer.Option()],
) -> None:
    """Update a server's hostname, given its machine ID."""
    from .client import Server

    server = Server(machine_id=machine_id, api_client=get_api_client())

    current_hostname = server.info().hostname
    server.update(hostname=hostname)
    if current_hostname == "":
        typer.echo(f"{machine_id}'s hostname was set to {hostname}.")
    else:
        typer.echo(
            f"{machine_id}'s hostname was updated from {current_hostname} to "
            f"{hostname}."
        )


@server_cli.command()
def rebuild(
    hostname: str = "", machine_id: str = "", token: str = DEFAULT_TOKEN
) -> None:
    """
    Rebuilds the VM with the operating system and SSH key given at launch time.

    Will take a couple minutes to complete after the request is made.
    """
    machine_id = _get_machine_id(machine_id=machine_id, hostname=hostname, token=token)
    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    api_client.server_rebuild(machine_id=machine_id)
    typer.echo(f"{hostname} rebuilding.")


@server_cli.command()
def flavors(provider: Union[Provider, None] = None) -> None:
    """Shows available flavors."""
    from rich.console import Console
    from rich.table import Table

    from ._cli_utils import cents_to_usd, gb_string, mb_string, tb_string
    from .api_client import APIClient

    console = Console(width=None if sys.stdout.isatty() else 10**9)

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Flavor Slug (--flavor)")
    table.add_column("Provider (--provider)")
    table.add_column("vCPU Cores")
    table.add_column("Memory")
    table.add_column("Disk")
    table.add_column("Bandwidth (per month)")
    table.add_column("Price per day")
    table.add_column("Price per month (30 days)")

    api_client = APIClient(api_endpoint=get_api_endpoint())
    flavors = api_client.flavors(provider)
    for flavor in flavors:
        price_per_30_days = flavor.price * 30
        table.add_row(
            flavor.slug,
            flavor.provider,
            str(flavor.cores),
            mb_string(flavor.memory),
            gb_string(flavor.disk),
            tb_string(flavor.bandwidth_per_month),
            f"[green]{cents_to_usd(flavor.price)}[/green]",
            f"[green]{cents_to_usd(price_per_30_days)}[/green]",
        )

    console.print(table)


@server_cli.command()
def operating_systems(provider: Union[Provider, None] = None) -> None:
    """Show available operating systems."""
    from rich.console import Console
    from rich.table import Table

    from .api_client import APIClient

    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    api_client = APIClient(api_endpoint=get_api_endpoint())
    table.add_column("Operating System (--operating-system)")
    table.add_column("Provider (--provider)")
    for _os in api_client.operating_systems(provider):
        table.add_row(_os.slug, _os.provider)

    console.print(table)


@server_cli.command()
def regions(provider: Union[Provider, None] = None) -> None:
    """Shows regions that servers can be launched in."""
    from rich.console import Console
    from rich.table import Table

    from .api_client import APIClient

    console = Console()

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Region Slug (--region)")
    table.add_column("Provider (--provider)")
    table.add_column("Region Name")

    api_client = APIClient(api_endpoint=get_api_endpoint())
    for region in api_client.regions(provider):
        table.add_row(region.slug, region.provider, region.name)

    console.print(table)


def load_token(token: str) -> str:
    token_file = token_path().joinpath(f"{token}.json")
    if not token_file.exists():
        msg = f"Token '{token}' ({token_file}) does not exist. Create it with:\n"
        msg += f"sporestack token create {token} --dollars 20 --currency xmr\n"
        msg += "(Can do more than $20, or a different currency, like btc.)\n"
        msg += (
            "With the token credited, you can launch servers, renew existing ones, etc."
        )
        typer.echo(msg, err=True)
        raise typer.Exit(code=1)

    token_data = json.loads(token_file.read_text())
    assert token_data["version"] == 1
    assert isinstance(token_data["key"], str)
    return token_data["key"]


def save_token(token: str, key: str) -> None:
    token_file = token_path().joinpath(f"{token}.json")
    if token_file.exists():
        msg = f"Token '{token}' already exists in {token_file}. Aborting!"
        typer.echo(msg, err=True)
        raise typer.Exit(code=1)

    token_data = {"version": TOKEN_VERSION, "name": token, "key": key}
    token_file.write_text(json.dumps(token_data))


@token_cli.command(name="create")
def token_create(
    dollars: Annotated[
        int,
        typer.Option(help="How many dollars to add to the token.", show_default=False),
    ],
    currency: Annotated[
        Currency,
        typer.Option(help="Which cryptocurrency to pay with.", show_default=False),
    ],
    token: Annotated[str, typer.Argument()] = DEFAULT_TOKEN,
    wait: Annotated[
        bool, typer.Option(help="Wait for the payment to be confirmed.")
    ] = True,
    qr: Annotated[
        bool, typer.Option(help="Show a QR code for the payment URI.")
    ] = True,
) -> None:
    """Enables a new token."""
    from . import utils

    if Path(SPORESTACK_DIR / "tokens" / f"{token}.json").exists():
        typer.echo("Token already created! Did you mean to `topup`?", err=True)
        raise typer.Exit(1)

    _token = utils.random_token()
    typer.echo(f"Generated key {_token} for use with token {token}", err=True)

    save_token(token, _token)
    token_add(
        token=_token,
        dollars=dollars,
        currency=currency,
        wait=wait,
        token_name=token,
        qr=qr,
    )
    typer.echo(f"{token}'s key is {_token}.")
    typer.echo("Save it, don't share it, and don't lose it!")
    typer.echo()
    typer.echo("Optional: Make a SSH key just for this token.")
    token_ssh_key_path = ssh_key_path(token) / DEFAULT_TOKEN_SSH_KEY_PRIVATE
    typer.echo(f'Run: ssh-keygen -C "" -t ed25519 -f "{token_ssh_key_path}"')
    typer.echo(
        "If you do this, servers launched from that token will default to use "
        "that key and you won't have to pass --ssh-key-file every time you "
        "launch a server!"
    )


@token_cli.command(name="import")
def token_import(
    name: str = typer.Argument(DEFAULT_TOKEN),
    key: str = typer.Option(...),
) -> None:
    """Imports a token under the given name."""
    save_token(name, key)


def token_add(
    token: str, dollars: int, currency: Currency, wait: bool, token_name: str, qr: bool
) -> None:
    from httpx import HTTPError

    from .api_client import APIClient
    from .client import Client
    from .exceptions import SporeStackServerError

    api_client = APIClient(api_endpoint=get_api_endpoint())
    client = Client(api_client=api_client, client_token=token)

    invoice = client.token.add(dollars, currency=currency)

    if qr:
        invoice_qr(invoice)
        typer.echo()
        typer.echo(
            "Resize your terminal and try again if QR code above is not readable."
        )
        typer.echo()
    invoice_panel(invoice, token=token, token_name=token_name)
    typer.echo("Pay *exactly* the specified amount. No more, no less.")

    if not wait:
        typer.echo("--no-wait: Not waiting for payment to be confirmed.", err=True)
        typer.echo(
            (
                f"Check status with: sporestack token invoice {token_name} "
                f"--invoice-id {invoice.id}"
            ),
            err=True,
        )
        return

    typer.echo("Press ctrl+c to abort.")

    while invoice.expired is False or invoice.paid is False:
        try:
            invoice = client.token.invoice(invoice=invoice.id)
        except (SporeStackServerError, HTTPError):
            typer.echo("Received 500 HTTP status, will try again.", err=True)
            continue
        if invoice.paid:
            typer.echo(
                f"Added ${dollars} to {token_name} ({token}) with TXID {invoice.txid}"
            )
            return
        typer.echo(WAITING_PAYMENT_TO_PROCESS, err=True)
        time.sleep(60)

    if invoice.expired:
        raise ValueError("Invoice has expired.")


@token_cli.command(name="topup")
def token_topup(
    currency: Annotated[
        Currency,
        typer.Option(help="Which cryptocurrency to pay with.", show_default=False),
    ],
    dollars: Annotated[
        int,
        typer.Option(help="How many dollars to add to the token.", show_default=False),
    ],
    token: Annotated[str, typer.Argument()] = DEFAULT_TOKEN,
    wait: Annotated[
        bool, typer.Option(help="Wait for the payment to be confirmed.")
    ] = True,
    qr: Annotated[
        bool, typer.Option(help="Show a QR code for the payment URI.")
    ] = True,
) -> None:
    """Adds balance to an existing token."""
    real_token = load_token(token)
    token_add(
        token=real_token,
        dollars=dollars,
        currency=currency,
        wait=wait,
        token_name=token,
        qr=qr,
    )


@token_cli.command()
def balance(token: str = typer.Argument(DEFAULT_TOKEN)) -> None:
    """Shows a token's balance."""
    _token = load_token(token)

    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())

    typer.echo(api_client.token_info(token=_token).balance_usd)


@token_cli.command(name="info")
def token_info(token: Annotated[str, typer.Argument()] = DEFAULT_TOKEN) -> None:
    """
    Show information about a token, including balance.

    Burn Rate is calculated per day of servers set to autorenew.

    Days Remaining is for servers set to autorenew, given the remaining balance.
    """
    _token = load_token(token)

    from rich import print

    from .api_client import APIClient
    from .client import Client

    api_client = APIClient(api_endpoint=get_api_endpoint())
    client = Client(api_client=api_client, client_token=_token)

    info = client.token.info()
    print(f"[bold]Token Information for {token} ({_token})[/bold]")
    print(f"Balance: [green]{info.balance_usd}")
    print(f"Total Servers (not deleted): {info.servers}")
    print(f"Servers set to autorenew: {info.autorenew_servers}")
    print(f"Suspended servers: {info.suspended_servers}")
    print(
        f"Burn Rate: [red]{info.burn_rate_usd}[/red] "
        "(per day of servers set to autorenew)"
    )
    print(
        f"Days Remaining: {info.days_remaining} "
        "(for servers set to autorenew, given the remaining balance)"
    )


@token_cli.command()
def servers(token: Annotated[str, typer.Argument()] = DEFAULT_TOKEN) -> None:
    """Deprecated: Use sporestack server list --token TOKEN instead!"""
    _token = load_token(token)

    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())

    typer.echo(api_client.servers_launched_from_token(token=_token))


@token_cli.command(name="list")
def token_list() -> None:
    """List tokens."""
    from rich.console import Console
    from rich.table import Table

    console = Console(width=None if sys.stdout.isatty() else 10**9)

    token_dir = token_path()
    table = Table(
        show_header=True,
        header_style="bold magenta",
        caption=f"These tokens are stored in {token_dir}",
    )
    table.add_column("Name")
    table.add_column("Token (this is a globally unique [bold]secret[/bold])")

    for token_file in token_dir.glob("*.json"):
        token = token_file.stem
        key = load_token(token)
        table.add_row(token, key)

    console.print(table)


@token_cli.command(name="invoices")
def token_invoices(token: Annotated[str, typer.Argument()] = DEFAULT_TOKEN) -> None:
    """List invoices."""
    _token = load_token(token)

    from rich.console import Console
    from rich.table import Table

    from ._cli_utils import cents_to_usd
    from .api_client import APIClient
    from .client import Client

    api_client = APIClient(api_endpoint=get_api_endpoint())
    client = Client(api_client=api_client, client_token=_token)

    console = Console(width=None if sys.stdout.isatty() else 10**9)

    table = Table(
        title=f"Invoices for {token} ({_token})",
        show_header=True,
        header_style="bold magenta",
    )
    table.add_column("ID")
    table.add_column("Amount")
    table.add_column("Created At")
    table.add_column("Paid At")
    table.add_column("URI")
    table.add_column("TXID")

    for invoice in client.token.invoices():
        if invoice.paid:
            paid = epoch_to_human(invoice.paid)
        else:
            if invoice.expired:
                paid = "[bold]Expired[/bold]"
            else:
                paid = f"Unpaid. Expires: {epoch_to_human(invoice.expires)}"
        table.add_row(
            str(invoice.id),
            cents_to_usd(invoice.amount),
            epoch_to_human(invoice.created),
            paid,
            invoice.payment_uri,
            invoice.txid,
        )

    console.print(table)


def invoice_panel(invoice: "Invoice", token: str, token_name: str) -> None:
    from rich import print
    from rich.panel import Panel

    if invoice.paid != 0:
        subtitle = f"[bold]Paid[/bold] with TXID: {invoice.txid}"
    elif invoice.expired:
        subtitle = "[bold]Expired[/bold]"
    else:
        subtitle = f"Unpaid. Expires: {epoch_to_human(invoice.expires)}"

    content = (
        f"Invoice created: {epoch_to_human(invoice.created)}\n"
        f"Payment URI: [link={invoice.payment_uri}]{invoice.payment_uri}[/link]\n"
        f"Cryptocurrency: {invoice.cryptocurrency.value.upper()}\n"
        f"Cryptocurrency rate: [green]${invoice.fiat_per_coin}[/green]\n"
        f"Dollars to add to token: [green]${invoice.amount // 100}[/green]"
    )
    panel = Panel(
        content,
        title=(
            f"SporeStack Invoice ID [italic]{invoice.id}[/italic] "
            f"for token [bold]{token_name}[/bold] ([italic]{token}[/italic])"
        ),
        subtitle=subtitle,
    )

    print(panel)


@token_cli.command(name="invoice")
def token_invoice(
    token: Annotated[str, typer.Argument()] = DEFAULT_TOKEN,
    invoice_id: str = typer.Option(help="Invoice's ID."),
    qr: bool = typer.Option(False, help="Show a QR code for the payment URI."),
) -> None:
    """Show a particular invoice."""
    _token = load_token(token)

    from .api_client import APIClient
    from .client import Client

    api_client = APIClient(api_endpoint=get_api_endpoint())
    client = Client(api_client=api_client, client_token=_token)

    invoice = client.token.invoice(invoice_id)
    if qr:
        invoice_qr(invoice)
        typer.echo()
    invoice_panel(invoice, token=_token, token_name=token)


@token_cli.command()
def messages(token: str = typer.Argument(DEFAULT_TOKEN)) -> None:
    """Show support messages."""
    token = load_token(token)

    from .api_client import APIClient
    from .client import Client

    api_client = APIClient(api_endpoint=get_api_endpoint())
    client = Client(api_client=api_client, client_token=token)

    for message in client.token.messages():
        typer.echo()
        typer.echo(message.message)
        typer.echo()
        typer.echo(f"Sent at {message.sent_at}, by {message.sender.value}")


@token_cli.command()
def send_message(
    token: str = typer.Argument(DEFAULT_TOKEN), message: str = typer.Option(...)
) -> None:
    """Send a support message."""
    token = load_token(token)

    from .api_client import APIClient
    from .client import Client

    api_client = APIClient(api_endpoint=get_api_endpoint())
    client = Client(api_client=api_client, client_token=token)

    client.token.send_message(message)


@cli.command()
def version() -> None:
    """Returns the installed version."""
    from . import __version__

    typer.echo(__version__)


@cli.command()
def api_changelog() -> None:
    """Shows the API changelog."""
    from rich.console import Console
    from rich.markdown import Markdown

    from .api_client import APIClient

    api_client = APIClient(api_endpoint=get_api_endpoint())
    console = Console()
    console.print(Markdown(api_client.changelog()))


# TODO
# @cli.command()
# def cli_changelog() -> None:
#     """Shows the Python library/CLI changelog."""


@cli.command()
def api_endpoint() -> None:
    """
    Prints the selected API endpoint: Env var: SPORESTACK_ENDPOINT,
    or, SPORESTACK_USE_TOR_ENDPOINT=1
    """
    from . import api_client

    endpoint = get_api_endpoint()
    if ".onion" in endpoint:
        typer.echo(f"{endpoint} using {api_client._get_tor_proxy()}")
        return
    else:
        typer.echo(endpoint)
        return


if __name__ == "__main__":
    cli()
