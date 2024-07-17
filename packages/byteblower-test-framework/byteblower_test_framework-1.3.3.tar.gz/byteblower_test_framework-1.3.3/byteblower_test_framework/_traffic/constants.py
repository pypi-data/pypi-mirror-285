"""Constants related to traffic generation."""
from enum import Enum

# Ethernet frame constants

ETHERNET_HEADER_LENGTH: int = 14  # [Bytes]
ETHERNET_FCS_LENGTH: int = 4  # [Bytes]
ETHERNET_PREAMBLE_LENGTH: int = 7  # [Bytes]
ETHERNET_SFD_LENGTH: int = 1  # Start Frame Delimiter [Bytes]
ETHERNET_PAUSE_LENGTH: int = 12  # [Bytes]
ETHERNET_PHYSICAL_OVERHEAD: int = (  # [Bytes]
    ETHERNET_PREAMBLE_LENGTH + ETHERNET_SFD_LENGTH + ETHERNET_PAUSE_LENGTH
)
assert ETHERNET_PHYSICAL_OVERHEAD == 20, "Unexpected invalid calculation"

# Ethernet frame Layer 2.5 constants

VLAN_HEADER_LENGTH: int = 4  # [Bytes]

VLAN_S_TAG = 0x88a8
VLAN_C_TAG = 0x8100

# IPv4 frame constants

IPV4_HEADER_LENGTH: int = 20

# IPv6 frame constants
IPV6_HEADER_LENGTH: int = 40

# UDP frame constants

UDP_HEADER_LENGTH: int = 8  # [Bytes]

# IP/UDP frame constants

IPV4_FULL_HEADER_LENGTH: int = (
    ETHERNET_HEADER_LENGTH +  # noqa: W504
    IPV4_HEADER_LENGTH + UDP_HEADER_LENGTH
)
assert IPV4_FULL_HEADER_LENGTH == 42, 'Incorrect IPv4 full header length'

IPV6_FULL_HEADER_LENGTH = (
    ETHERNET_HEADER_LENGTH +  # noqa: W504
    IPV6_HEADER_LENGTH + UDP_HEADER_LENGTH
)
assert IPV6_FULL_HEADER_LENGTH == 62, 'Incorrect IPv6 full header length'


class HttpMethod(Enum):
    """HTTP method used for HTTP (client) sessions."""

    AUTO = 'Automatic'
    GET = 'GET'
    PUT = 'PUT'


class TCPCongestionAvoidanceAlgorithm(Enum):
    """
    TCP Congestion Avoidance Algorithm.

    .. versionchanged:: 1.2.0
       Fixed for Python upper case naming convention.
    """

    NONE = 'None'
    NEW_RENO = 'new-reno'
    NEW_RENO_WITH_CUBIC = 'new-reno-with-cubic'
    SACK = 'sack'
    SACK_WITH_CUBIC = 'sack-with-cubic'
