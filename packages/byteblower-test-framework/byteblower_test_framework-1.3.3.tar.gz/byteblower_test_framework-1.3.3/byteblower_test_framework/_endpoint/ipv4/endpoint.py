"""ByteBlower IPv4 Endpoint interface module."""
from ipaddress import IPv4Address, IPv4Network  # for type hinting
from typing import TYPE_CHECKING, Optional  # for type hinting

from ..._host.meetingpoint import MeetingPoint  # for type hinting
from ...exceptions import FeatureNotSupported
from ..nat_endpoint import NatDiscoveryEndpoint

if TYPE_CHECKING:
    # NOTE: Used in documentation
    from ...exceptions import InvalidInput


class IPv4Endpoint(NatDiscoveryEndpoint):
    """ByteBlower Endpoint interface.

    This type of endpoint supports discovery of the actual *source* IP address
    (and UDP port) used by an Endpoint when transmitting to a specific
    destination. This is particularly important for IPv4 multihoming.

    The discovery also supports *Traditional NAT* (`RFC 3022`_,
    *Traditional IP Network Address Translator*). *Traditional NAT* has two
    variants: `Basic NAT`_ and `Network Address Port Translation (NAPT)`_.

    .. _RFC 3022: https://datatracker.ietf.org/doc/html/rfc3022
    .. _Basic NAT: https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.1
    .. _Network Address Port Translation (NAPT): https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.2

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """  # pylint: disable=line-too-long

    def __init__(
        self,
        meeting_point: MeetingPoint,
        uuid: str,
        name: Optional[str] = None,
        **kwargs
    ) -> None:
        """Initialize a ByteBlower IPv4 Endpoint.

        :param meeting_point: Meeting point this Endpoint is registered on
        :type meeting_point: MeetingPoint
        :param uuid: Unique identifier of the device to use
        :type uuid: str
        :param name: Friendly name for this endpoint, used for reporting,
           defaults to None (*auto-generated*)
        :type name: Optional[str], optional
        :param tags: List of tags to assign, defaults to None
        :type tags: Optional[Sequence[str]], optional
        :raises InvalidInput: when unsupported configuration is provided
        """
        super().__init__(meeting_point, uuid, name=name, **kwargs)

    @property
    def ip(self) -> IPv4Address:
        """Return the Endpoint host IP address."""
        # Returns a single IPv4 address instead of a list
        ipv4_address: str = self._network_info.IPv4Get()
        return IPv4Address(ipv4_address)

    @property
    def network(self) -> IPv4Network:
        """
        Return the network of the *preferred* IP address.

        .. note::
           Useful for reporting. Furthermore not used
           in traffic generation or analysis.
        """
        raise FeatureNotSupported('Endpoint IPv4 network address')

    @property
    def gateway(self) -> IPv4Address:
        """
        Return the default gateway.

        .. note::
           Useful for reporting. Furthermore not used
           in traffic generation or analysis.
        """
        raise FeatureNotSupported('Endpoint IPv4 network gateway')
