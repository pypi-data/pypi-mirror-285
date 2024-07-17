"""IPv4 Frame interface module."""
import logging
from typing import TYPE_CHECKING, Optional, Union  # for type hinting

# XXX - Causes circular import with scapy 2.4.5 on macOS Monterey:
# Similar to https://github.com/secdev/scapy/issues/3246
# from scapy.layers.inet import IP, UDP
# from scapy.layers.l2 import Ether
from scapy.all import IP, UDP, Ether  # pylint: disable=no-name-in-module
from scapy.packet import Raw

from ..._endpoint.endpoint import Endpoint
from ..._endpoint.ipv4.port import IPv4Port  # for type hinting
from ..constants import IPV4_FULL_HEADER_LENGTH
from ..frame import Frame
from ..helpers import get_ip_traffic_class

if TYPE_CHECKING:
    # NOTE: Import because referenced in docstrings:
    from ...constants import (
        DEFAULT_FRAME_LENGTH,
        DEFAULT_IP_DSCP,
        DEFAULT_IP_ECN,
        UDP_DYNAMIC_PORT_START,
    )
    from ...exceptions import ConflictingInput, InvalidInput


class IPv4Frame(Frame):
    """Frame interface for IPv4."""

    __slots__ = ('_ip_tos',)

    def __init__(
        self,
        length: Optional[int] = None,
        udp_src: Optional[int] = None,
        udp_dest: Optional[int] = None,
        ip_dscp: Optional[int] = None,
        ip_ecn: Optional[int] = None,
        ipv4_tos: Optional[int] = None,
        latency_tag: bool = False
    ) -> None:
        """Create the interface to an IPv4 frame.

        :param length: Frame length. This is the layer 2 (Ethernet) frame length
           *excluding* Ethernet FCS and *excluding* VLAN tags,
           defaults to :const:`DEFAULT_FRAME_LENGTH`
        :type length: Optional[int], optional
        :param udp_src: UDP source port, defaults to
           :const:`UDP_DYNAMIC_PORT_START`
        :type udp_src: Optional[int], optional
        :param udp_dest: UDP destination port, defaults to
           :const:`UDP_DYNAMIC_PORT_START`
        :type udp_dest: Optional[int], optional
        :param ip_dscp: IP Differentiated Services Code Point (DSCP),
           mutual exclusive with ``ipv4_tos``,
           defaults to :const:`DEFAULT_IP_DSCP`
        :type ip_dscp: Optional[int], optional
        :param ip_ecn: IP Explicit Congestion Notification (ECN),
           mutual exclusive with ``ipv4_tos``,
           defaults to :const:`DEFAULT_IP_ECN`
        :type ip_ecn: Optional[int], optional
        :param ipv4_tos: Exact IPv4 ToS field value,
           mutual exclusive with ``ip_dscp`` and ``ip_ecn``,
           defaults to field value composed from ``ip_dscp`` and ``ip_ecn``.
        :type ipv4_tos: Optional[int], optional
        :param latency_tag: Enable latency tag generation in the Frame,
           defaults to ``False``
        :type latency_tag: bool, optional
        :raises InvalidInput: When invalid configuration values are given.
        :raises ConflictingInput: When invalid combination of configuration
           parameters is given
        """
        super().__init__(
            IPV4_FULL_HEADER_LENGTH, length, udp_src, udp_dest, latency_tag
        )

        self._ip_tos = get_ip_traffic_class(
            "IPv4 ToS",
            ip_traffic_class=ipv4_tos,
            ip_dscp=ip_dscp,
            ip_ecn=ip_ecn,
        )

    def build_frame_content(
        self, source_port: IPv4Port, destination_port: Union[IPv4Port,
                                                             Endpoint]
    ) -> Ether:
        """Obtain needed information to build the frame.

        .. warning::
           Internal use only. Use with care.

        .. versionadded:: 1.2.0
           Added for ByteBlower Endpoint support.

        :meta private:
        """
        udp_dest = self._udp_dest
        udp_src = self._udp_src

        ip_src = source_port.ip
        ipv4_tos = self._ip_tos

        napt_info = destination_port.discover_nat(
            source_port,
            remote_udp_port=self._udp_src,
            local_udp_port=self._udp_dest
        )
        logging.debug('NAT/NAPT discovery result: %r', napt_info)
        ip_dest, udp_dest = napt_info

        mac_src = source_port.mac
        mac_dst = source_port.layer3.Resolve(ip_dest.compressed)

        scapy_layer2_5_headers = self._build_layer2_5_headers(source_port)

        payload = self._build_payload(IPV4_FULL_HEADER_LENGTH)

        scapy_udp_payload = Raw(payload.encode('ascii', 'strict'))
        scapy_udp_header = UDP(dport=udp_dest, sport=udp_src)
        scapy_ip_header = IP(src=ip_src, dst=ip_dest, tos=ipv4_tos)
        scapy_ethernet_header = Ether(src=mac_src, dst=mac_dst)
        for scapy_layer2_5_header in scapy_layer2_5_headers:
            scapy_ethernet_header /= scapy_layer2_5_header
        scapy_frame = (
            scapy_ethernet_header / scapy_ip_header / scapy_udp_header /
            scapy_udp_payload
        )

        return scapy_frame
