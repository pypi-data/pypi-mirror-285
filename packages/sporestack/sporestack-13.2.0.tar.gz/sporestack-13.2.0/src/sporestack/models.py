"""SporeStack API supplemental models"""

# Try not to import this file from the CLI directly as it will slow interactivity.

import sys
from typing import Union

if sys.version_info >= (3, 9):  # pragma: nocover
    from typing import Annotated
else:  # pragma: nocover
    from typing_extensions import Annotated

# Re-export Currency
from pydantic import BaseModel, Field

from .constants import Currency


class Flavor(BaseModel):
    # Unique string to identify the flavor that's sort of human readable.
    slug: str
    # Number of vCPU cores the server is given.
    cores: int
    # Memory in Megabytes
    memory: int
    # Disk in Gigabytes
    disk: int
    # USD cents per day
    price: int
    # IPv4 connectivity: "/32"
    ipv4: str
    # IPv6 connectivity: "/128"
    ipv6: str
    """Gigabytes of bandwidth per day."""
    bandwidth_per_month: float
    """Gigabytes of bandwidth per month."""
    provider: str
    """Provider that the flavor is available on."""


class OperatingSystem(BaseModel):
    name: str
    """Human readable string to identify the operating system."""
    slug: str
    """Unique string to identify the operating system."""
    provider: str
    """Provider that the operating system is available on."""


class TokenInfo(BaseModel):
    balance_cents: int
    balance_usd: str
    burn_rate_cents: int
    burn_rate_usd: str
    days_remaining: int
    servers: int
    autorenew_servers: int
    suspended_servers: int


class Region(BaseModel):
    # Unique string to identify the region that's sort of human readable.
    slug: str
    # Actually human readable string describing the region.
    name: str
    provider: str
    """Provider that the region is available on."""


class Invoice(BaseModel):
    id: str
    payment_uri: Annotated[
        str, Field(description="Cryptocurrency URI for the payment.")
    ]
    cryptocurrency: Annotated[
        Currency,
        Field(description="Cryptocurrency that will be used to pay this invoice."),
    ]
    amount: Annotated[
        int,
        Field(
            description="Amount of cents to add to the token if this invoice is paid."
        ),
    ]
    fiat_per_coin: Annotated[
        str,
        Field(
            description="Stringified float of the price when this was made.",
            example="100.00",
        ),
    ]
    created: Annotated[
        int, Field(description="Timestamp of when this invoice was created.")
    ]
    expires: Annotated[
        int, Field(description="Timestamp of when this invoice will expire.")
    ]
    paid: Annotated[
        int, Field(description="Timestamp of when this invoice was paid. 0 if unpaid.")
    ]
    txid: Annotated[
        Union[str, None],
        Field(
            description="TXID of the transaction for this payment, if it was paid.",
            min_length=64,
            max_length=64,
            pattern="^[a-f0-9]+$",
        ),
    ]
    expired: Annotated[
        bool,
        Field(
            description=(
                "Whether or not the invoice has expired (only applicable if "
                "unpaid, or payment not yet confirmed."
            ),
        ),
    ]


class ServerUpdateRequest(BaseModel):
    hostname: Annotated[
        Union[str, None],
        Field(
            min_length=0,
            max_length=128,
            title="Hostname",
            description="Hostname to refer to your server by.",
            example="web-1",
            pattern="(^$|^[a-zA-Z0-9-_. ]+$)",
        ),
    ] = None
    autorenew: Annotated[
        Union[bool, None],
        Field(
            title="Autorenew",
            description=(
                "Automatically renew the server from the token, "
                "keeping it at 1 week expiration."
            ),
            example=True,
        ),
    ] = None
