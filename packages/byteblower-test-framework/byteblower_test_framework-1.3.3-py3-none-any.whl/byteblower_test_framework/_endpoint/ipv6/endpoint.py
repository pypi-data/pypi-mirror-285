"""ByteBlower IPv6 Endpoint interface module."""
from ipaddress import (  # for type hinting
    IPv6Address,
    IPv6Interface,
    IPv6Network,
)
from typing import (  # for type hinting
    TYPE_CHECKING,
    Iterable,
    Optional,
    Sequence,
)

from byteblowerll.byteblower import NetworkInterface

from ..._host.meetingpoint import MeetingPoint  # for type hinting
from ...exceptions import AddressSelectionFailed, FeatureNotSupported
from ..nat_endpoint import NatDiscoveryEndpoint

if TYPE_CHECKING:
    # NOTE: Used in documentation
    from ...exceptions import InvalidInput


class IPv6Endpoint(NatDiscoveryEndpoint):
    """ByteBlower Endpoint interface for IPv6.

    This type of endpoint supports discovery of the actual *source* IP address
    (and UDP port) used by an Endpoint when transmitting to a specific
    destination.

    This is particularly important for IPv6 multihoming (`RFC 7157`_,
    *IPv6 Multihoming without Network Address Translation*).

    The discovery can also support NPTv6 (`RFC 6296`_,
    *IPv6-to-IPv6 Network Prefix Translation*).

    .. _RFC 6296: https://datatracker.ietf.org/doc/html/rfc6296
    .. _RFC 7157: https://datatracker.ietf.org/doc/html/rfc7157

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """

    def __init__(
        self,
        meeting_point: MeetingPoint,
        uuid: str,
        name: Optional[str] = None,
        network_interface: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize ByteBlower IPv6 Endpoint.

        :param meeting_point: Meeting point this Endpoint is registered on
        :type meeting_point: MeetingPoint
        :param uuid: Unique identifier of the device to use
        :type uuid: str
        :param name: Friendly name for this endpoint, used for reporting,
           defaults to None (*auto-generated*)
        :type name: Optional[str], optional
        :param network_interface: Name of the network interface used
           by the endpoint for traffic generation and analysis,
           defaults to None (*first interface found with IPv6 address*).

           .. note::
              Mostly relevant for reporting and frame blasting flows.
              When multiple network interfaces are available on the
              Endpoint and automatic selection is not (always) correct.

        :type network_interface: Optional[str]
        :param tags: List of tags to assign, defaults to None
        :type tags: Optional[Sequence[str]], optional
        :raises InvalidInput: when unsupported configuration is provided
        """
        super().__init__(meeting_point, uuid, name=name, **kwargs)
        self._network_interface = network_interface

    @property
    def ip(self) -> IPv6Address:
        """Return the Endpoint host IP address."""
        self._network_info.Refresh()
        for address in self._global_addresses:
            return address.ip
        for address in self._link_local_addresses:
            return address.ip
        raise AddressSelectionFailed(
            f'No valid IPv6 address found for {self._network_interface}'
        )

    @property
    def network(self) -> IPv6Network:
        """
        Return the network of the *preferred* IP address.

        .. note::
           Useful for reporting. Furthermore not used
           in traffic generation or analysis.
        """
        raise FeatureNotSupported('Endpoint IPv6 network address')

    @property
    def gateway(self) -> IPv6Address:
        """
        Return the default gateway.

        .. note::
           Useful for reporting. Furthermore not used
           in traffic generation or analysis.
        """
        raise FeatureNotSupported('Endpoint IPv6 network gateway')

    @property
    def _global_addresses(self) -> Iterable[IPv6Interface]:
        """
        Return all available global IPv6 addresses.

        Searches for the traffic interface on the endpoint.

        :return: list if IPv6 global addresses
        :rtype: Iterable[IPv6Interface]
        """
        network_interface_list: Sequence[NetworkInterface] = (
            self._network_info.InterfaceGet()
        )
        for network_interface in network_interface_list:
            if (self._network_interface is None
                    or network_interface.NameGet() == self._network_interface):
                yield from (
                    IPv6Interface(address)
                    for address in network_interface.IPv6GlobalGet()
                )

    @property
    def _link_local_addresses(self) -> Iterable[IPv6Interface]:
        """
        Return all available link-local IPv6 addresses.

        Searches for the traffic interface on the endpoint.

        :return: list if IPv6 link-local addresses
        :rtype: Iterable[IPv6Interface]
        """
        network_interface_list: Sequence[NetworkInterface] = (
            self._network_info.InterfaceGet()
        )
        for network_interface in network_interface_list:
            if (self._network_interface is None
                    or network_interface.NameGet() == self._network_interface):
                yield from (
                    IPv6Interface(address)
                    for address in network_interface.IPv6LinkLocalGet()
                )
