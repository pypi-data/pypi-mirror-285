"""Helpers related to handling endpoint configuration."""
from typing import TYPE_CHECKING, Iterator, Sequence, Union  # for type hinting

from byteblowerll.byteblower import VLANTag  # for type hinting

# XXX - Avoid circular import with scapy 2.4.5 on macOS Monterey:
# Similar to https://github.com/secdev/scapy/issues/3246
# from scapy.layers.l2 import Dot1AD, Dot1Q
from scapy.all import Dot1AD, Dot1Q  # pylint: disable=no-name-in-module

from .._traffic.constants import VLAN_HEADER_LENGTH  # for sanity check
from .._traffic.constants import VLAN_C_TAG, VLAN_S_TAG
from ..exceptions import (
    ByteBlowerTestFrameworkException,
    FeatureNotSupported,
    InvalidInput,
)
from .endpoint import Endpoint
from .port import Port

if TYPE_CHECKING:
    # NOTE: Import does not work at runtime: cyclic import dependencies
    # See also: https://mypy.readthedocs.io/en/stable/runtime_troubles.html#import-cycles, pylint: disable=line-too-long
    from .._endpoint.port import VlanFlatConfig  # for type hinting

assert VLAN_HEADER_LENGTH == len(Dot1Q()), "Unexpected VLAN header length"


def vlan_header_length(endpoint: Union[Port, Endpoint]) -> int:
    """Return the total length of all VLAN headers on the endpoint.

    :param endpoint: Endpoint to check the VLAN configuration on
    :type endpoint: Union[Port, Endpoint]
    :raises FeatureNotSupported: When an unsupported endpoint type is given
    :return: Total length of layer 2.5 headers in packets sent by the endpoint
    :rtype: int
    """
    if not isinstance(endpoint, (Port, Endpoint)):
        raise FeatureNotSupported(
            'Unsupported endpoint'
            f' type: {type(endpoint).__name__!r}'
        )

    try:
        vlan_config = list(endpoint.vlan_config)
        return len(vlan_config) * VLAN_HEADER_LENGTH
    except FeatureNotSupported:
        # (currently) not supported for Endpoint
        return 0


def build_layer2_5_headers(
    source_port: 'Port'
) -> Sequence[Union[Dot1Q, Dot1AD]]:
    """Build list Layer 2.5 headers to add to an Ethernet frame.

    These are the Layer 2.5 (VLAN, PPPoE, ...) headers which are required
    when transmitting that Ethernet frame from the given source port.

    :param source_port: Port transmitting that frame.
    :type source_port: Port
    :return: Ordered list of VLAN tags to add to the Ethernet frame.
    :rtype: Sequence[Union[Dot1Q, Dot1AD]]
    """
    return [
        _build_layer2_5_header(*vlan_config)
        for vlan_config in _vlan_config(source_port)
    ]


def _vlan_config(source_port: 'Port') -> Iterator[Sequence['VlanFlatConfig']]:
    """Return list of VLAN (stack) configuration (generator).

    Similar to :meth:`Port.vlan_config`, but raises an exception
    when we have Layer 2.5 configurations other than :class:`VLANTag`
    or we have unsupported VLAN configurations.

    :param source_port: Port to get the VLAN configuration from
    :type source_port: Port
    :raises ByteBlowerTestFrameworkException: In case of Layer 2.5
        other than VLAN
    :return:
        Ordered collection (Outer -> Inner) of VLAN configuration tuples
    :yield: VLAN configuration for current layer 2.5
    :rtype: Iterator[Sequence[VlanFlatConfig]]
    """
    layer2_5 = source_port.layer2_5
    for l2_5 in layer2_5:
        if not isinstance(l2_5, VLANTag):
            raise ByteBlowerTestFrameworkException(
                f'Unsupported Layer 2.5 configuration: {type(l2_5)!r}'
            )
        yield (
            l2_5.ProtocolIDGet(), l2_5.IDGet(), l2_5.DropEligibleGet(),
            l2_5.PriorityGet()
        )


def _build_layer2_5_header(
    vlan_tpid: int, vlan_id: int, vlan_dei: bool, vlan_pcp: int
) -> Union[Dot1Q, Dot1AD]:
    """Build a layer 2.5 header for the given VLAN configuration.

    :param vlan_tpid: VLAN Protocol ID (TPID)
    :type vlan_tpid: int
    :param vlan_id: VLAN ID (VID)
    :type vlan_id: int
    :param vlan_dei: Drop Eligible flag (DEI)
    :type vlan_dei: bool
    :param vlan_pcp: Priority Code Point (PCP)
    :type vlan_pcp: int
    :raises InvalidInput: When VLAN is configured with an unsupported TPID
    :return: scapy header for Layer2.5
    :rtype: Union[Dot1Q, Dot1AD]
    """
    if vlan_tpid == VLAN_S_TAG:
        return Dot1AD(prio=vlan_pcp, id=vlan_dei, vlan=vlan_id)
    if vlan_tpid == VLAN_C_TAG:
        return Dot1Q(prio=vlan_pcp, id=vlan_dei, vlan=vlan_id)
    raise InvalidInput(
        f'VLAN TPID {vlan_tpid} is not supported.'
        f' Please use S-Tag {VLAN_S_TAG} or C-tag {VLAN_C_TAG}'
    )
