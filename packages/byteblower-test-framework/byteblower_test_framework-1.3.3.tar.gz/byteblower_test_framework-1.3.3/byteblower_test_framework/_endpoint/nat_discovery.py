"""Behavior module for IP address and UDP port resolution."""
import binascii
import logging
from datetime import datetime, timedelta
from ipaddress import IPv4Address, IPv6Address
from time import sleep
from typing import Dict, Optional, Sequence, Tuple, Union  # for type hinting

from byteblowerll.byteblower import (
    ByteBlowerAPIException,
    Capture,
    CapturedFrame,
    CaptureResultSnapshot,
    ConfigError,
    DeviceStatus,
)
from byteblowerll.byteblower import Frame as TxFrame  # for type hinting
from byteblowerll.byteblower import FrameMobile, Stream, StreamMobile
from scapy.layers.inet import IP, UDP, Ether
from scapy.layers.inet6 import IPv6
from scapy.packet import Raw

from ..constants import UDP_DYNAMIC_PORT_START
from ..exceptions import NatDiscoveryFailed
from .endpoint import Endpoint
from .helpers import build_layer2_5_headers
from .port import Port

_CACHE_KEY_FORMAT = '{}/{}'


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
class NatResolver(object):
    """IP address and UDP port resolver.

    Used by endpoint interfaces which require NAT/NAPT discovery.

    This resolver performs "*NAPT discovery mode*": Discovery of the actual
    *source* IP address (and UDP port) used by an endpoint when transmitting
    to a specific destination.

    This is particularly relevant for IPv4 NAPT and multihoming
    or IPv6 multihoming (`RFC 7157`_, *IPv6 Multihoming without
    Network Address Translation*).

    For IPv4 :class:`Port` and :class:`Endpoint`, the discovery supports
    *Traditional NAT* (`RFC 3022`_, *Traditional IP Network Address Translator*).
    *Traditional NAT* has two variants: `Basic NAT`_ and
    `Network Address Port Translation (NAPT)`_.

    .. _RFC 3022: https://datatracker.ietf.org/doc/html/rfc3022
    .. _Basic NAT: https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.1
    .. _Network Address Port Translation (NAPT): https://www.rfc-editor.org/rfc/rfc2663.html#section-4.1.2

    For IPv6 :class:`Port` and :class:`Endpoint`, the discovery can also
    support NPTv6 (`RFC 6296`_, *IPv6-to-IPv6 Network Prefix Translation*).

    .. _RFC 6296: https://datatracker.ietf.org/doc/html/rfc6296
    .. _RFC 7157: https://datatracker.ietf.org/doc/html/rfc7157

    .. versionadded:: 1.2.0
       Added support for ByteBlower Endpoint.
    """  # pylint: disable=line-too-long

    __slots__ = (
        '_local_port',
        '_cache',
        '_public_ip',
    )

    def __init__(self, local_port: Union[Port, Endpoint]) -> None:
        self._local_port = local_port
        self._cache: Dict[str, Tuple[str, int]] = {}
        self._public_ip: Optional[str] = None

    def resolve(
        self,
        remote_port: Port,
        remote_udp_port: int = UDP_DYNAMIC_PORT_START,
        local_udp_port: int = UDP_DYNAMIC_PORT_START
    ) -> Tuple[Union[IPv4Address, IPv6Address], int]:
        """
        Discover translated IP address and/or UDP port.

        Discovers whether the local IP address and/or UDP port are translated
        when communicating with the remote IP address / UDP port.

        This function will resolve the public IP address and port
        as seen by the `remote_port`.

        :param remote_port: The port on the NSI side.
        :type remote_port: Port
        :param remote_udp_port: The remote UDP port.
           Default is UDP_DYNAMIC_PORT_START.
        :type remote_udp_port: int
        :param local_udp_port: The local UDP port.
           Default is UDP_DYNAMIC_PORT_START.
        :type local_udp_port: int
        :return: A tuple containing the resolved IP address and port.
        :rtype: Tuple[str, int]
        :raises ByteBlowerAPIException: When configuration of
           public NAT/NAPT discovery failed.
        :raises NatDiscoveryFailed: When discovery of the public IP address
            and/or UDP port failed.

        .. note::
           - If the endpoint to be resolved is ByteBlower endpoint,
             this function discovers the IP address selected
             by the ByteBlower endpoint.
           - If address and/or port translation is done
             (for example NAT in IPv4), this function returns
             the public IP address.
        """
        remote_ip_address = remote_port.ip.compressed

        # Check if it is already in our cache
        _cache_key = _CACHE_KEY_FORMAT.format(
            remote_ip_address, remote_udp_port, local_udp_port
        )
        _cache_entry = self._cache.get(_cache_key)
        if _cache_entry:
            return _cache_entry

        if isinstance(self._local_port, Port):
            # Collect generic information:
            local_port_l3 = self._local_port.layer3

            local_ip_address = self._local_port.ip.compressed

            # Prepare stream configuration
            # Resolve destination MAC address
            mac: str
            try:
                mac = local_port_l3.Resolve(remote_ip_address)
            except ByteBlowerAPIException:
                logging.debug(
                    'Exception occurred while trying to resolve'
                    ' public IP address %s from NAT/NAPT port %r',
                    remote_ip_address,
                    self._local_port.name,
                    exc_info=True
                )
                mac = local_port_l3.Resolve(local_port_l3.GatewayGet())
            logging.debug(
                "NAT/NAPT PORT %r DEST MAC: %s", self._local_port.name, mac
            )

            # Build frame content
            # NOTE: Done in
            # byteblower_test_framework.logging.configure_logging():
            # logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

            scapy_layer2_5_headers = build_layer2_5_headers(self._local_port)

            payload = 'a' * (200)
            scapy_udp_payload = Raw(payload.encode('ascii', 'strict'))
            scapy_udp_header = UDP(dport=remote_udp_port, sport=local_udp_port)
            scapy_ip_header = IP(src=local_ip_address, dst=remote_ip_address)
            scapy_ethernet_header = Ether(src=self._local_port.mac, dst=mac)
            for scapy_layer2_5_header in scapy_layer2_5_headers:
                scapy_ethernet_header /= scapy_layer2_5_header
            scapy_frame = (
                scapy_ethernet_header / scapy_ip_header / scapy_udp_header /
                scapy_udp_payload
            )
            logging.debug(
                'NaptResolver for %r: Transmit Content: %s',
                self._local_port.name, scapy_frame.summary()
            )

            # Configure stream
            stream: Stream = self._local_port.bb_port.TxStreamAdd()
            stream.InterFrameGapSet(10 * 1000 * 1000)  # 10ms
            stream.NumberOfFramesSet(-1)

            # Add frame to the stream
            frame_content = bytearray(bytes(scapy_frame))
            # The ByteBlower API expects an 'str' as input
            # for the Frame::BytesSet(), we need to convert the bytearray.
            hexbytes = ''.join((format(b, '02x') for b in frame_content))

            tx_frame: TxFrame = stream.FrameAdd()
            tx_frame.BytesSet(hexbytes)

        elif isinstance(self._local_port, Endpoint):
            stream: StreamMobile = self._local_port.bb_endpoint.TxStreamAdd()
            stream.InterFrameGapSet(10 * 1000 * 1000)  # 10ms
            stream.NumberOfFramesSet(20)

            payload = 'a' * (200)

            scapy_udp_payload = Raw(payload.encode('ascii', 'strict'))

            payload_array = bytearray(bytes(scapy_udp_payload))

            hexbytes = ''.join((format(b, "02x") for b in payload_array))

            tx_frame: FrameMobile = stream.FrameAdd()
            tx_frame.PayloadSet(hexbytes)

            stream.DestinationAddressSet(remote_ip_address)
            stream.DestinationPortSet(remote_udp_port)
            stream.SourcePortSet(local_udp_port)

        # Create destination capture
        capture: Capture = remote_port.bb_port.RxCaptureBasicAdd()
        capture.FilterSet(
            f'dst host {remote_ip_address!s}'
            f' and udp dst port {remote_udp_port}'
        )

        # Start resolution process
        capture.Start()

        if isinstance(self._local_port, Endpoint):
            # For debugging
            try:
                self._local_port.bb_endpoint.Prepare()

                device_start_nanoseconds: int = (
                    self._local_port.bb_endpoint.Start()
                )
                device_start_timestamp = datetime.utcfromtimestamp(
                    device_start_nanoseconds / 1e9
                )
                current_timestamp = self._local_port.meeting_point.timestamp

                # Wait for the endpoint to start
                time_to_wait = device_start_timestamp - current_timestamp
                time_to_wait += timedelta(milliseconds=200)

                sleep(time_to_wait.total_seconds())

                # Wait until the Endpoint finished (should be 200ms)
                while True:
                    endpoint_status = self._local_port.status
                    if endpoint_status != DeviceStatus.Running:
                        break
                    sleep(0.1)

                # self._local_port.bb_endpoint.Stop()
            except ConfigError as error:
                print(error.getMessage())
                self._local_port.bb_endpoint.Lock(False)
                raise
            self._local_port.bb_endpoint.TxStreamRemove(stream)

        elif isinstance(self._local_port, Port):
            stream.Start()
            sleep(.2)

            # Stop stream (should have stopped by itself already)
            stream.Stop()
            # Remove the stream, no longer required
            self._local_port.bb_port.TxStreamRemove(stream)

        # stop capture
        capture.Stop()

        capture_result: CaptureResultSnapshot = capture.ResultGet()
        capture_frames: Sequence[CapturedFrame] = capture_result.FramesGet()
        if len(capture_frames) == 0:
            remote_port.bb_port.RxCaptureBasicRemove(capture)
            raise NatDiscoveryFailed(
                'NAT/NAPT discovery failed, no packets received on'
                f' public endpoint from endpoint {self._local_port.name!r}.'
            )

        result = None
        for capture_frame in capture_frames:
            captured_bytes = capture_frame.BytesGet()
            # logging.debug('Checking frame %s for public IPaddress.',
            #               captured_bytes)
            raw_bytes = binascii.unhexlify(captured_bytes)
            # get source ip and udp port from captured packet
            # Layer 2 decoding
            # -- decoding LENGTH/TYPE field
            ether = Ether(raw_bytes)
            logging.debug(
                'NaptResolver for %r: Received Content: %s',
                self._local_port.name, ether.summary()
            )
            # Check for IPv4
            if ether.haslayer(IP) and ether.haslayer(UDP):
                nat_public_ip: str = ether[IP].src
                nat_public_udp: int = ether[UDP].sport
                result = (IPv4Address(nat_public_ip), nat_public_udp)
                break
            # Check for IPv6
            if ether.haslayer(IPv6) and ether.haslayer(UDP):
                nat_public_ip: str = ether[IPv6].src
                nat_public_udp: int = ether[UDP].sport
                result = (IPv6Address(nat_public_ip), nat_public_udp)
                break

        # Cleanup the capture
        remote_port.bb_port.RxCaptureBasicRemove(capture)

        if result is None:
            raise NatDiscoveryFailed(
                'Could not resolve public NAT/NAPT information'
                f' for {self._local_port.name!r}'
            )

        # Cache the result
        self._public_ip = result[0].compressed
        self._cache[_cache_key] = result

        return result

    @property
    def public_ip(self) -> Optional[str]:
        """Return the public IP address resolved from last NAT discovery."""
        return self._public_ip
