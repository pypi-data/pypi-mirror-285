"""ByteBlower traffic endpoint interfaces."""
from ._endpoint.endpoint import Endpoint  # for user convenience type hinting
from ._endpoint.ipv4.endpoint import IPv4Endpoint

# NOTE: Deprecated ``NattedPort`` in v1.2.0,
# kept export for backward-compatibility
# TODO: Remove ``NattedPort`` in v1.4.0
from ._endpoint.ipv4.nat import NattedPort  # pylint: disable=unused-import
from ._endpoint.ipv4.nat import NatDiscoveryIPv4Port
from ._endpoint.ipv4.port import IPv4Port
from ._endpoint.ipv6.endpoint import IPv6Endpoint
from ._endpoint.ipv6.port import IPv6Port
from ._endpoint.nat_endpoint import NatDiscoveryEndpoint  # for documentation
from ._endpoint.port import Port  # for user convenience type hinting
from ._endpoint.port import (  # pylint: disable=unused-import; for user convenience
    VlanConfig,
)

# Export the user interfaces.
#
# Outcomes:
# * Limits import on `from byteblower_test_framework.endpoint import *`
# * Exposes the interfaces in the (Sphinx) documentation
#
# NOTE
#   Port is only useful for type hinting, but we export it so that we
#   are sure that it is included in the Sphinx documentation properly.
#
__all__ = (
    # ByteBlowerPort base interface:
    Port.__name__,  # Include it for Sphinx documentation
    # ByteBlowerPort interfaces:
    IPv4Port.__name__,
    NatDiscoveryIPv4Port.__name__,
    IPv6Port.__name__,
    # ByteBlower Endpoint interfaces:
    Endpoint.__name__,  # Include it for Sphinx documentation
    NatDiscoveryEndpoint.__name__,  # Include it for Sphinx documentation
    IPv4Endpoint.__name__,
    IPv6Endpoint.__name__,
)
