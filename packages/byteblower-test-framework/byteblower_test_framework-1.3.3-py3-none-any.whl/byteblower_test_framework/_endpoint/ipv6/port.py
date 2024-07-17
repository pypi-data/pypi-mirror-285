"""ByteBlower Port IPv6 interface module."""
import logging
from ipaddress import IPv6Address, IPv6Interface, IPv6Network
from typing import Optional, Sequence  # for type hinting

from byteblowerll.byteblower import (  # for type hinting
    DHCPv6Protocol,
    DomainError,
    IPv6Configuration,
)

from ..._host.server import Server  # for type hinting
from ..port import Port, VlanConfig


class IPv6Port(Port):
    """ByteBlower Port interface for IPv6."""

    __slots__ = (
        '_dhcp_failed',
        '_slaac_failed',
        '_ipv6',
    )

    def __init__(
        self,
        server: Server,
        interface: str = None,
        name: Optional[str] = None,
        mac: Optional[str] = None,
        vlans: Optional[Sequence[VlanConfig]] = None,
        ipv6: Optional[str] = None,
        tags: Optional[Sequence[str]] = None,
        **kwargs
    ) -> None:
        super().__init__(
            server,
            interface=interface,
            name=name,
            mac=mac,
            vlans=vlans,
            tags=tags,
            **kwargs
        )
        self._dhcp_failed = False
        self._slaac_failed = False

        # Sanity checks
        if ipv6 is None:
            ipv6 = 'dhcp'
        elif ipv6.lower() not in ('dhcp', 'slaac'):
            raise ValueError(
                'Currently, only DHCPv6 or SLAAC is supported on IPv6 ports.'
            )
        self._ipv6 = ipv6.lower()
        self._configure()

    def _configure_l3(self) -> IPv6Configuration:
        # If we don't have a mac address yet, generate one automatically
        self._configure_l2()
        # Layer 2.5 configuration MUST be done after L2 and before L3
        self._configure_l2_5()
        port_l3: IPv6Configuration = self._bb_port.Layer3IPv6Set()
        if self._ipv6 == 'dhcp':
            try:
                # Perform DHCP
                port_l3_dhcp: DHCPv6Protocol = port_l3.ProtocolDhcpGet()
                port_l3_dhcp.Perform()
            except DomainError as error:
                logging.exception(
                    'DHCP failed for %s on %s! Error message: %s', self._name,
                    self._interface, error.getMessage()
                )
                self._dhcp_failed = True
            logging.debug('DHCPv6 succeeded: \n%s', port_l3.DescriptionGet())
        elif self._ipv6 == 'slaac':
            try:
                # Perform Stateless AutoConfiguration
                port_l3.StatelessAutoconfiguration()
            except DomainError as error:
                logging.exception(
                    'SLAAC failed for %s on %s! Error message: %s', self._name,
                    self._interface, error.getMessage()
                )
                self._slaac_failed = True
        else:
            logging.warning(
                '%s: Unexpected IPv6 configuration method: %r', self._name,
                self._ipv6
            )

        return port_l3

    @property
    def failed(self) -> bool:
        return self._dhcp_failed or self._slaac_failed

    @property
    def ip(self) -> IPv6Address:
        # Return first available DHCPv6 or SLAAC address
        if self._ipv6 == 'dhcp':
            ipv6_addresses = self.layer3.IpDhcpGet()
        elif self._ipv6 == 'slaac':
            ipv6_addresses = self.layer3.IpStatelessGet()
        else:
            logging.warning(
                " %s: Manual IPv6 addressing is not yet available,"
                "returning link local address", self._name
            )
            ipv6_addresses = []

        for ipv6_address in ipv6_addresses:
            ipv6_if = IPv6Interface(ipv6_address)
            return ipv6_if.ip
        # If none found, return the link local IPv6 address
        return IPv6Address(self.layer3.IpLinkLocalGet())

    @property
    def network(self) -> IPv6Network:
        if self._ipv6 == 'dhcp':
            ipv6_addresses = self.layer3.IpDhcpGet()
        elif self._ipv6 == 'slaac':
            ipv6_addresses = self.layer3.IpStatelessGet()
        else:
            logging.warning(
                "%s: Manual IPv6 addressing is not yet available,"
                "returning netmask of link local address", self._name
            )
            ipv6_addresses = []
        for ipv6_address in ipv6_addresses:
            ipv6_if = IPv6Interface(ipv6_address)
            return ipv6_if.network
        return IPv6Network((self.layer3.IpLinkLocalGet(), 64), strict=False)

    @property
    def gateway(self) -> IPv6Address:
        return IPv6Address(self.layer3.GatewayGet())

    @property
    def layer3(self) -> IPv6Configuration:
        """
        IPv6 configuration of the ByteBlower Lower Layer API.

        .. note::
           Subject to change in dual stack implementations.
        """
        return super().layer3
