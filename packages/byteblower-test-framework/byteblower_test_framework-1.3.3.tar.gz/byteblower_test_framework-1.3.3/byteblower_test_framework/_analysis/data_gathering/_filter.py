"""Filter builders for different receiving endpoints."""
import logging
from ipaddress import IPv4Address, IPv6Address  # for type hinting
from typing import Sequence, Tuple, Union  # for type hinting

from byteblowerll.byteblower import VLANTag  # for type hinting

from ..._endpoint.endpoint import Endpoint
from ..._endpoint.ipv4.port import IPv4Port
from ..._endpoint.ipv6.port import IPv6Port
from ..._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting

# Type aliases
PortFilterContent = str
EndpointFilterContent = Tuple[Union[IPv4Address, IPv6Address], int, int]


class _GenericFilterBuilder(object):  # pylint: disable=too-few-public-methods

    __slots__ = ()

    @staticmethod
    def _vlan_id(flow: FrameBlastingFlow) -> Sequence[int]:
        destination_port = flow.destination
        layer2_5 = destination_port.layer2_5
        for l2_5 in layer2_5:
            if not isinstance(l2_5, VLANTag):
                logging.warning(
                    'Flow Analyser %r:'
                    ' Unsupported Layer 2.5 configuration: %r', flow.name,
                    type(l2_5)
                )
            yield l2_5.IDGet()

    @staticmethod
    def _build_layer2_5_filter(flow: FrameBlastingFlow) -> str:
        # Quick filter without VLAN ID:
        # l2_5_filter = 'vlan and ' * len(destination_port.layer2_5)
        l2_5_filter = ' and '.join(
            (
                f'vlan {vlan_id}'
                for vlan_id in _GenericFilterBuilder._vlan_id(flow)
            )
        )
        if l2_5_filter:
            return l2_5_filter + ' and '
        return l2_5_filter

    @staticmethod
    def build_bpf_filter(
        flow: FrameBlastingFlow, src_udp: int, dest_udp: int
    ) -> PortFilterContent:
        source_port = flow.source
        destination_port = flow.destination
        l2_5_filter = _GenericFilterBuilder._build_layer2_5_filter(flow)
        dest_ip = destination_port.ip.compressed
        # Source IP and UDP might be private
        logging.debug(
            'Discover NAT/NAPT: %r (%r) -> %r (%r)', source_port.name, src_udp,
            destination_port.name, dest_udp
        )
        napt_info = source_port.discover_nat(
            destination_port, remote_udp_port=dest_udp, local_udp_port=src_udp
        )
        logging.debug('NAT/NAPT discovery result: %r', napt_info)
        # Publicly visible source IP address and UDP port
        src_ip, src_udp = napt_info
        src_ip = src_ip.compressed
        if isinstance(source_port, (IPv6Port, Endpoint)) and isinstance(
                destination_port, IPv6Port):
            return f'{l2_5_filter}ip6 dst {dest_ip} and ip6 src {src_ip}' \
                f' and udp dst port {dest_udp} and udp src port {src_udp}'
        if isinstance(source_port, (IPv4Port, Endpoint)) and isinstance(
                destination_port, IPv4Port):
            return f'{l2_5_filter}ip dst {dest_ip} and ip src {src_ip}' \
                f' and udp dst port {dest_udp} and udp src port {src_udp}'
        raise ValueError(
            'FrameLossAnalyser: Cannot create BPF filter'
            f' for Flow {flow.name}: Unsupported Port type:'
            f' source: {source_port.name} > {type(source_port)} |'
            f' destination: {destination_port.name} > {type(destination_port)}'
        )


class FrameFilterBuilder(object):  # pylint: disable=too-few-public-methods

    __slots__ = ()

    @staticmethod
    def build_bpf_filter(flow: FrameBlastingFlow) -> PortFilterContent:
        src_dest_udp_set = {
            (source_frame.udp_src, source_frame.udp_dest)
            for source_frame in flow._frame_list
        }
        # TODO - Support for multiple UDP src/dest combinations
        #        with multiple frames
        if len(src_dest_udp_set) < 1:
            logging.warning(
                'Frame loss analyser: Flow %r: No frames configured?'
                ' Cannot analyze this Flow.', flow.name
            )
            src_dest_udp_set = set((0, 0))
        elif len(src_dest_udp_set) > 1:
            logging.warning(
                'Frame loss analyser: Flow %r: Multiple UDP source/destination'
                ' port combinations is not yet supported.'
                ' You may expect reported loss.', flow.name
            )
        src_dest_udp = next(iter(src_dest_udp_set))
        return _GenericFilterBuilder.build_bpf_filter(
            flow, src_dest_udp[0], src_dest_udp[1]
        )


class EndpointFilterBuilder(object):  # pylint: disable=too-few-public-methods

    __slots__ = ()

    @staticmethod
    def build(flow: FrameBlastingFlow) -> EndpointFilterContent:
        src_dest_udp_set = {
            (source_frame.udp_src, source_frame.udp_dest)
            for source_frame in flow.frame_list
        }
        # TODO - Support for multiple UDP src/dest combinations
        #        with multiple frames
        if len(src_dest_udp_set) < 1:
            logging.warning(
                'Endpoint filter: Flow %r: No frames configured?'
                ' Cannot analyze this Flow.', flow.name
            )
            src_dest_udp_set = set((0, 0))
        elif len(src_dest_udp_set) > 1:
            logging.warning(
                'Endpoint filter: Flow %r: Multiple UDP source/destination'
                ' port combinations is not yet supported.'
                ' You may expect reported loss.', flow.name
            )
        ip_src_address = flow.source.ip
        src_dest_udp = next(iter(src_dest_udp_set))
        udp_src_port, udp_dest_port = src_dest_udp
        return ip_src_address, udp_src_port, udp_dest_port
