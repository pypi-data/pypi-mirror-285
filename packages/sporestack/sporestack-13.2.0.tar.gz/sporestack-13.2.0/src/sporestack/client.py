from dataclasses import dataclass, field
from typing import List, Union

from . import api
from .api_client import APIClient
from .constants import Currency, Provider
from .models import Flavor, Invoice, OperatingSystem, Region, TokenInfo
from .utils import random_token


@dataclass
class Server:
    machine_id: str
    api_client: APIClient = field(default_factory=APIClient)

    def info(self) -> api.ServerInfo.Response:
        """Returns information about the server."""
        return self.api_client.server_info(self.machine_id)

    @property
    def flavor(self) -> Flavor:
        """Returns information about the server's flavor."""
        info = self.info()
        for flavor in self.api_client.flavors(Provider(info.provider)):
            if flavor.slug == info.flavor_slug:
                return flavor
        # This **should** never happen...
        raise ValueError("Could not map flavor! Contact support!")

    @property
    def region(self) -> Region:
        """Returns information about the server's region."""
        info = self.info()
        for region in self.api_client.regions(Provider(info.provider)):
            if region.provider != info.provider:
                continue
        # This **should** never happen...
        raise ValueError("Could not map region! Contact support!")

    @property
    def operating_system(self) -> OperatingSystem:
        """Returns information about the server's operating_system."""
        info = self.info()
        for operating_system in self.api_client.operating_systems(
            Provider(info.provider)
        ):
            if operating_system.slug == info.operating_system:
                return operating_system
        # This **should** never happen...
        raise ValueError("Could not map operating_system! Contact support!")

    def rebuild(self) -> None:
        """Delete all data on the server and reinstall it."""
        self.api_client.server_rebuild(self.machine_id)

    def forget(self) -> None:
        """Forget about the server so it doesn't show up when listing servers."""
        self.api_client.server_forget(self.machine_id)

    def delete(self) -> None:
        """Delete the server."""
        self.api_client.server_delete(self.machine_id)

    def start(self) -> None:
        """Powers on the server."""
        self.api_client.server_start(self.machine_id)

    def stop(self) -> None:
        """Powers off the server."""
        self.api_client.server_stop(self.machine_id)

    def autorenew_enable(self) -> None:
        """Enables autorenew on the server."""
        self.api_client.server_update(self.machine_id, autorenew=True)

    def autorenew_disable(self) -> None:
        """Disables autorenew on the server."""
        self.api_client.server_update(self.machine_id, autorenew=False)

    def update(
        self, hostname: Union[str, None] = None, autorenew: Union[bool, None] = None
    ) -> None:
        """Update details about a server."""
        self.api_client.server_update(
            self.machine_id, hostname=hostname, autorenew=autorenew
        )

    def topup(self, days: int) -> None:
        """
        Renew the server for the amount of days specified, from the token that
        launched the server.
        """
        self.api_client.server_topup(machine_id=self.machine_id, days=days)


@dataclass
class Token:
    token: str = field(default_factory=random_token)
    api_client: APIClient = field(default_factory=APIClient)
    ssh_key: Union[str, None] = None
    """SSH public key for launching new servers with."""

    def add(self, dollars: int, currency: Currency) -> Invoice:
        """Fund the token."""
        response = self.api_client.token_add(
            token=self.token,
            dollars=dollars,
            currency=currency,
        )
        return response.invoice

    def balance(self) -> int:
        """Returns the token's balance in cents."""
        return self.api_client.token_balance(token=self.token).cents

    def info(self) -> TokenInfo:
        """Returns information about a token."""
        return self.api_client.token_info(token=self.token)

    def invoice(self, invoice: str) -> Invoice:
        """Returns the specified token's invoice."""
        return self.api_client.token_invoice(token=self.token, invoice=invoice)

    def invoices(self) -> List[Invoice]:
        """Returns invoices for adding balance to the token."""
        return self.api_client.token_invoices(token=self.token)

    def messages(self) -> List[api.TokenMessage]:
        """Returns support messages for/from the token."""
        return self.api_client.token_get_messages(token=self.token)

    def send_message(self, message: str) -> None:
        """Returns support messages for/from the token."""
        self.api_client.token_send_message(token=self.token, message=message)

    def servers(self, show_forgotten: bool = False) -> List[Server]:
        server_classes: List[Server] = []
        for server in self.api_client.servers_launched_from_token(
            self.token, include_forgotten=show_forgotten
        ).servers:
            server_classes.append(
                Server(machine_id=server.machine_id, api_client=self.api_client)
            )
        return server_classes

    def launch_server(
        self,
        flavor: str,
        operating_system: str,
        days: Union[int, None] = None,
        autorenew: bool = False,
        provider: Provider = Provider.DIGITALOCEAN,
        ssh_key: Union[str, None] = None,
        region: Union[str, None] = None,
        hostname: str = "",
        user_data: Union[str, None] = None,
    ) -> Server:
        if ssh_key is None:
            if self.ssh_key is not None:
                ssh_key = self.ssh_key
            else:
                raise ValueError("ssh_key must be set in Client() or launch_server().")
        server_launch_response = self.api_client.server_launch(
            autorenew=autorenew,
            days=days,
            token=self.token,
            provider=provider,
            region=region,
            flavor=flavor,
            operating_system=operating_system,
            ssh_key=ssh_key,
            hostname=hostname,
            user_data=user_data,
        )
        return Server(
            machine_id=server_launch_response.machine_id,
            api_client=self.api_client,
        )


@dataclass
class Client:
    client_token: str = ""
    """Token to manage/pay for servers with."""
    api_client: APIClient = field(default_factory=APIClient)
    """Your own API Client, perhaps if you want to connect through Tor."""
    ssh_key: Union[str, None] = None
    """SSH public key for launching new servers with."""

    def flavors(self, provider: Union[Provider, None] = None) -> List[Flavor]:
        """Returns available flavors (server sizes)."""
        return self.api_client.flavors(provider)

    def operating_systems(
        self, provider: Union[Provider, None] = None
    ) -> List[OperatingSystem]:
        """Returns available operating systems."""
        return self.api_client.operating_systems(provider)

    def regions(self, provider: Union[Provider, None] = None) -> List[Region]:
        """Returns regions that servers can be launched in."""
        return self.api_client.regions(provider)

    def server_quote(
        self, days: int, flavor: str, provider: Provider = Provider.DIGITALOCEAN
    ) -> api.ServerQuote.Response:
        """Get a quote for how much a server will cost."""
        return self.api_client.server_quote(days=days, flavor=flavor, provider=provider)

    def changelog(self) -> str:
        """Read the API changeog."""
        return self.api_client.changelog()

    @property
    def token(self) -> Token:
        """Returns a Token object with the api_client and token specified."""
        return Token(
            token=self.client_token, api_client=self.api_client, ssh_key=self.ssh_key
        )
