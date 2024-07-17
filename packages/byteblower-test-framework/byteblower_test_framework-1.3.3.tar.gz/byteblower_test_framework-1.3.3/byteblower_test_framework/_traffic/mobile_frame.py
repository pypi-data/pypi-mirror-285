"""Mobile frame module."""
import logging
from abc import ABC
from typing import TYPE_CHECKING, Optional, Union  # for type hinting

from byteblowerll.byteblower import FrameMobile as TxFrame
from byteblowerll.byteblower import FrameTagTx  # for type hinting
from byteblowerll.byteblower import StreamMobile as TxStream

from .._endpoint.endpoint import Endpoint
from .._endpoint.ipv4.endpoint import IPv4Endpoint
from .._endpoint.ipv6.endpoint import IPv6Endpoint
from .._endpoint.port import Port
from ..constants import DEFAULT_FRAME_LENGTH, UDP_DYNAMIC_PORT_START
from ..exceptions import FeatureNotSupported
from .constants import IPV4_FULL_HEADER_LENGTH, IPV6_FULL_HEADER_LENGTH
from .helpers import get_ip_traffic_class

if TYPE_CHECKING:
    # NOTE: Import because referenced in docstrings:
    from ..constants import DEFAULT_IP_DSCP, DEFAULT_IP_ECN
    from ..exceptions import ConflictingInput, InvalidInput


class MobileFrame(ABC):
    """Mobile Frame Interface.

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """

    _slots__ = (
        '_length',
        '_udp_src',
        '_udp_dest',
        '_ip_traffic_class',
        '_latency_tag',
        '_frame',
    )

    def __init__(
        self,
        length: Optional[int] = None,
        udp_src: Optional[int] = None,
        udp_dest: Optional[int] = None,
        ip_dscp: Optional[int] = None,
        ip_ecn: Optional[int] = None,
        ip_traffic_class: Optional[int] = None,
        latency_tag: bool = False
    ) -> None:
        """Create the mobile frame for the wireless endpoint.

        :param length: Frame length. This is the layer 2 (Ethernet)
           frame length *excluding* Ethernet FCS and *excluding* VLAN tags,
           defaults to :const:`DEFAULT_FRAME_LENGTH`
        :type length: int, optional
        :param udp_src: UDP source port, defaults to
           :const:`UDP_DYNAMIC_PORT_START`
        :type udp_src: int, optional
        :param udp_dest: UDP destination port, defaults to
           :const:`UDP_DYNAMIC_PORT_START`
        :type udp_dest: int, optional
        :param ip_dscp: IP Differentiated Services Code Point (DSCP),
            mutual exclusive with ``ip_traffic_class``,
            defaults to :const:`DEFAULT_IP_DSCP`
        :type ip_dscp: Optional[int], optional
        :param ip_ecn: IP Explicit Congestion Notification (ECN),
            mutual exclusive with ``ip_traffic_class``,
            defaults to :const:`DEFAULT_IP_ECN`
        :type ip_ecn: Optional[int], optional
        :param ip_traffic_class: The IP traffic class value is used to
           specify the exact value of either the *IPv4 ToS field* or the
           *IPv6 Traffic Class field*,
           mutual exclusive with ``ip_dscp`` and ``ip_ecn``,
           defaults to field value composed from ``ip_dscp`` and ``ip_ecn``.
        :type ip_traffic_class: Optional[int], optional
        :param latency_tag: Enable latency tag generation in the Frame,
           defaults to ``False``
        :type latency_tag: bool, optional
        :raises InvalidInput: When invalid configuration values are given.
        :raises ConflictingInput: When invalid combination of configuration
           parameters is given
        """
        if length is None:
            length = DEFAULT_FRAME_LENGTH

        if udp_src is None:
            udp_src = UDP_DYNAMIC_PORT_START

        if udp_dest is None:
            udp_dest = UDP_DYNAMIC_PORT_START

        self._length = length
        self._udp_src = udp_src
        self._udp_dest = udp_dest
        self._latency_tag = latency_tag
        self._frame: TxFrame = None

        self._ip_traffic_class = get_ip_traffic_class(
            "IP Traffic Class",
            ip_traffic_class=ip_traffic_class,
            ip_dscp=ip_dscp,
            ip_ecn=ip_ecn,
        )

    def build_frame_content(
        self, source_port: Port, destination_port: Union[Port, Endpoint]
    ):
        """Obtain needed information to build the mobile frame.

        .. warning::
           Internal use only. Use with care.

        :meta private:
        """
        if isinstance(source_port, IPv4Endpoint):
            payload = self._build_payload(IPV4_FULL_HEADER_LENGTH)
        elif isinstance(source_port, IPv6Endpoint):
            payload = self._build_payload(IPV6_FULL_HEADER_LENGTH)
        else:
            raise FeatureNotSupported(
                'Unsupported source endpoint'
                f' type: {type(source_port).__name__!r}'
            )

        return payload, destination_port.ip.compressed

    def _build_payload(self, header_length: int) -> str:
        return 'a' * (self._length - header_length)

    def add(self, frame_content: str, stream: TxStream):
        """Add the created frame to the stream.

        .. warning::
           Internal use only. Use with care.

        :meta private:
        """
        payload, destination_ip = frame_content

        payload_bytes = payload.encode('ascii', 'strict')

        hexbytes = ''.join((format(b, "02x") for b in payload_bytes))

        self._frame: TxFrame = stream.FrameAdd()
        self._frame.PayloadSet(hexbytes)

        if self._latency_tag:
            # Enable latency for this frame.
            # The frame frame contents will be altered
            # so it contains a timestamp.
            frame_tag: FrameTagTx = self._frame.FrameTagTimeGet()
            frame_tag.Enable(True)

        stream.DestinationAddressSet(destination_ip)
        stream.DestinationPortSet(self._udp_dest)
        stream.SourcePortSet(self._udp_src)
        stream.TypeOfServiceSet(self._ip_traffic_class)

    def release(self, stream: TxStream) -> None:
        """
        Release this frame resources used on the ByteBlower system.

        .. note::
           The resources related to the stream itself is not released.
        """
        try:
            bb_frame = self._frame
            del self._frame
        except AttributeError:
            logging.warning('MobileFrame: Already destroyed?', exc_info=True)
        else:
            if bb_frame is not None:
                # NOTE: Not really required when we destroy the stream
                #       afterwards
                stream.FrameDestroy(bb_frame)

    @property
    def length(self) -> int:
        """Ethernet length without FCS and without VLAN tags."""
        return self._length

    @property
    def udp_src(self):
        """UDP source port."""
        return self._udp_src

    @property
    def udp_dest(self):
        """UDP destination port."""
        return self._udp_dest
