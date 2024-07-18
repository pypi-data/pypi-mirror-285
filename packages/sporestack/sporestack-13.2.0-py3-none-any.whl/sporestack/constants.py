from enum import Enum


class Provider(str, Enum):
    DUMMY = "dummy"
    """Dummy hosting. No actual server."""
    DIGITALOCEAN = "digitalocean"
    """DigitalOcean"""
    VULTR = "vultr"
    """Vultr"""


class Currency(str, Enum):
    xmr = "xmr"
    """Monero"""
    btc = "btc"
    """Bitcoin"""
    bch = "bch"
    """Bitcoin Cash"""


class ServerDeletedBy(str, Enum):
    EXPIRATION = "expiration"
    """The server was deleted automatically for being expired."""
    MANUAL = "manual"
    """The server was deleted before its expiration via the API."""
    SPORESTACK = "sporestack"
    """The server was deleted by SporeStack, likely due to an AUP violation."""


class TokenMessageSender(str, Enum):
    USER = "User"
    SPORESTACK = "SporeStack"
