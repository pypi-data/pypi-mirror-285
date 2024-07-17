"""Interface module for ByteBlower Endpoint requiring NAT/NAPT discovery."""
from ipaddress import IPv4Address, IPv6Address, ip_address  # for type hinting
from typing import Optional, Tuple, Union  # for type hinting

from .._host.meetingpoint import MeetingPoint
from ..constants import UDP_DYNAMIC_PORT_START
from .endpoint import Endpoint
from .nat_discovery import NatResolver
from .port import Port


# See also:
#
# IPv4
# - "RFC 3022, section 2.2 - Overview op NAPT"
#   https://datatracker.ietf.org/doc/html/rfc3022#section-2.2
# - "RFC 2663, section 4.1 - Traditional NAT (or) Outbound NAT"
#   https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1
# - https://en.wikipedia.org/wiki/Network_address_translation#One-to-many_NAT
#
# IPv6
# - "IPv6 Multihoming without Network Address Translation"
#   https://datatracker.ietf.org/doc/html/rfc7157
# - "IPv6-to-IPv6 Network Prefix Translation" (NPTv6)
#   https://datatracker.ietf.org/doc/html/rfc6296
# - "IPv6-to-IPv6 Network Prefix Translation" (NPTv6)
#   https://en.wikipedia.org/wiki/IPv6-to-IPv6_Network_Prefix_Translation
#
# - "Local Network Protection for IPv6" (LNP)
#   https://datatracker.ietf.org/doc/html/rfc4864
#
class NatDiscoveryEndpoint(Endpoint):
    """ByteBlower Endpoint interface requiring NAT/NAPT discovery.

    This type of endpoint supports discovery of the actual *source* IP address
    (and UDP port) used by an Endpoint when transmitting to a specific
    destination.

    This is particularly important for IPv4 multihoming or IPv6 multihoming
    (`RFC 7157`_, *IPv6 Multihoming without Network Address Translation*).

    For IPv4, the discovery also supports *Traditional NAT* (`RFC 3022`_,
    *Traditional IP Network Address Translator*). *Traditional NAT* has two
    variants: `Basic NAT`_ and `Network Address Port Translation (NAPT)`_.

    .. _RFC 3022: https://datatracker.ietf.org/doc/html/rfc3022
    .. _Basic NAT: https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.1
    .. _Network Address Port Translation (NAPT): https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.2

    For IPv6, the discovery can also support NPTv6 (`RFC 6296`_,
    *IPv6-to-IPv6 Network Prefix Translation*).

    .. _RFC 6296: https://datatracker.ietf.org/doc/html/rfc6296
    .. _RFC 7157: https://datatracker.ietf.org/doc/html/rfc7157

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        meeting_point: MeetingPoint,
        uuid: str,
        name: Optional[str] = None,
        **kwargs,
    ) -> None:
        super().__init__(meeting_point, uuid, name=name, **kwargs)
        self._nat_resolver = NatResolver(self)

    @property
    def require_nat_discovery(self) -> bool:
        """
        Return whether this endpoint requires NAT/NAPT discovery.

        This is typically required when this endpoint is located
        behind a NAT/NAPT gateway or you are testing on a
        `carrier-grade NAT`_ (CGN/CGNAT, `RFC 6888`_) network.

        .. _carrier-grade NAT: https://en.wikipedia.org/wiki/Carrier-grade_NAT
        .. _RFC 6888: https://datatracker.ietf.org/doc/html/rfc6888
        """
        return True

    def discover_nat(
        self,
        remote_port: Port,
        remote_udp_port: int = UDP_DYNAMIC_PORT_START,
        local_udp_port: int = UDP_DYNAMIC_PORT_START,
    ) -> Tuple[Union[IPv4Address, IPv6Address], int]:
        """
        Resolve the IP address (and/or UDP port) as seen by `remote_port`.

        This will resolve either the IP address of the endpoint
        or the public IP address of the (IPv4 NAT/NAPT) gateway when
        the endpoint is using IPv4 and is located behind a NAT/NAPT
        gateway.

        .. note::
           UDP ports (``remote_udp_port`` and ``local_udp_port``) can be
           left to the default if you are only interested in the public IP.
        """
        return self._nat_resolver.resolve(
            remote_port,
            remote_udp_port=remote_udp_port,
            local_udp_port=local_udp_port
        )

    @property
    def public_ip(self) -> Union[IPv4Address, IPv6Address]:
        """Return the public IP address resolved from last NAT discovery."""
        # TODO - Return ip when public_ip is not (yet) resolved?
        if self._nat_resolver.public_ip:
            return ip_address(self._nat_resolver.public_ip)
        # TODO - Discover NAT when not yet done?
        #      * For example when only performing TCP tests
        #        (NAT is not resolved then via the NatResolver)
        return self.ip
