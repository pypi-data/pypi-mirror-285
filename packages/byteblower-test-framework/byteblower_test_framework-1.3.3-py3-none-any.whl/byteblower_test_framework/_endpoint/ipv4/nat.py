"""ByteBlower IPv4 Port interfaces supporting NAT/NAPT discovery."""
import logging
from ipaddress import IPv4Address
from typing import Optional, Sequence, Tuple  # for type hinting

from ..._host.server import Server  # for type hinting
from ...constants import UDP_DYNAMIC_PORT_START
from ..nat_discovery import NatResolver
from .port import IPv4Port


# See also:
#
# - "RFC 3022, section 2.2 - Overview of NAPT"
#   https://datatracker.ietf.org/doc/html/rfc3022#section-2.2
# - "RFC 2663, section 4.1 - Traditional NAT (or) Outbound NAT"
#   https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1
# - https://en.wikipedia.org/wiki/Network_address_translation#One-to-many_NAT
#
class NatDiscoveryIPv4Port(IPv4Port):
    """ByteBlower Port interface for IPv4 which requires NAT/NAPT discovery.

    This type of endpoint supports discovery of *Traditional NAT* (`RFC 3022`_,
    *Traditional IP Network Address Translator*). *Traditional NAT* has two
    variants: `Basic NAT`_ and `Network Address Port Translation (NAPT)`_.

    .. _RFC 3022: https://datatracker.ietf.org/doc/html/rfc3022
    .. _Basic NAT: https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.1
    .. _Network Address Port Translation (NAPT): https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.2

    .. versionchanged:: 1.2.0
       Improved naming for NAT/NAPT discovery related interfaces.
    """  # pylint: disable=line-too-long

    __slots__ = ('_nat_resolver',)

    def __init__(
        self,
        server: Server,
        interface: str = None,
        mac: Optional[str] = None,
        ipv4: Optional[str] = None,
        netmask: Optional[str] = None,
        gateway: Optional[str] = None,
        name: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        **kwargs
    ) -> None:
        super().__init__(
            server,
            interface=interface,
            mac=mac,
            ipv4=ipv4,
            netmask=netmask,
            gateway=gateway,
            name=name,
            tags=tags,
            **kwargs
        )
        self._nat_resolver = NatResolver(self)

    @property
    def require_nat_discovery(self) -> bool:
        return True

    def discover_nat(
        self,
        remote_port: IPv4Port,
        remote_udp_port: int = UDP_DYNAMIC_PORT_START,
        local_udp_port: int = UDP_DYNAMIC_PORT_START
    ) -> Tuple[IPv4Address, int]:
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
            local_udp_port=local_udp_port,
        )

    @property
    def public_ip(self) -> IPv4Address:
        """Return the public IP address resolved from last NAT discovery."""
        # TODO - Return ip when public_ip is not (yet) resolved?
        if self._nat_resolver.public_ip:
            return IPv4Address(self._nat_resolver.public_ip)
        # TODO - Discover NAT when not yet done?
        #      * For example when only performing TCP tests
        #        (NAT is not resolved then via the NatResolver)
        return self.ip


# NOTE: Deprecated ``NattedPort`` in v1.2.0,
# TODO: Remove ``NattedPort`` in v1.4.0
class NattedPort(NatDiscoveryIPv4Port):
    """ByteBlower Port interface for IPv4 which requires NAT/NAPT discovery.

    .. deprecated:: 1.2.0
       Use :class:`NatDiscoveryIPv4Port` instead. Will be removed in v1.4.0

    :meta private:
    """

    def __init__(self, server: Server, **kwargs) -> None:
        logging.warning(
            'DEPRECATED: NattedPort is replaced by NatDiscoveryIPv4Port.'
            ' It will be removed in the next release.'
            ' Please update your script accordingly.'
        )
        super().__init__(server, **kwargs)
