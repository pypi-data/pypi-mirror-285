"""Frame interface module."""
import logging
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Sequence, Union  # for type hinting

from .._endpoint.helpers import build_layer2_5_headers
from ..constants import DEFAULT_FRAME_LENGTH, UDP_DYNAMIC_PORT_START
from ..exceptions import InvalidInput

if TYPE_CHECKING:
    # For type hinting and avoiding cyclic imports

    from byteblowerll.byteblower import Frame as TxFrame
    from byteblowerll.byteblower import FrameTagTx
    from byteblowerll.byteblower import Stream as TxStream

    # XXX - Avoid circular import with scapy 2.4.5 on macOS Monterey:
    # Similar to https://github.com/secdev/scapy/issues/3246
    # from scapy.layers.l2 import Ether
    # from scapy.layers.l2 import Dot1AD, Dot1Q
    from scapy.all import (
        Ether,  # for type hinting; pylint: disable=no-name-in-module
    )
    from scapy.all import Dot1AD, Dot1Q  # pylint: disable=no-name-in-module

    # NOTE: Import does not work at runtime: cyclic import dependencies
    # See also: https://mypy.readthedocs.io/en/stable/runtime_troubles.html#import-cycles, pylint: disable=line-too-long
    from .._endpoint.endpoint import Endpoint
    from .._endpoint.port import Port


class Frame(ABC):
    """Frame interface."""

    __slots__ = (
        '_length',
        '_udp_src',
        '_udp_dest',
        '_latency_tag',
        '_frame',
    )

    def __init__(
        self,
        _minimum_length: int,
        length: Optional[int] = None,
        udp_src: Optional[int] = None,
        udp_dest: Optional[int] = None,
        latency_tag: bool = False
    ) -> None:
        """Create the base frame.

        :param _minimum_length: Required minimum length of the frame,
           used for sanity check
        :type _minimum_length: int
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
        :param latency_tag: Enable latency tag generation in the Frame,
           defaults to ``False``
        :type latency_tag: bool, optional
        :raises InvalidInput: When invalid configuration values are given.
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
        self._frame: 'TxFrame' = None

        # Sanity checks
        if self._length < _minimum_length:
            raise InvalidInput(
                'Frame length too small.'
                f' Must be at least {_minimum_length}B.'
            )

    def _build_layer2_5_headers(
        self, source_port: 'Port'
    ) -> Sequence[Union['Dot1Q', 'Dot1AD']]:
        return build_layer2_5_headers(source_port)

    def _build_payload(self, header_length: int) -> str:
        return 'a' * (self._length - header_length)

    @abstractmethod
    def build_frame_content(
        self, source_port: Union['Port', 'Endpoint'],
        destination_port: Union['Port', 'Endpoint']
    ) -> 'Ether':
        """Obtain needed information to build the frame.

        .. warning::
           Internal use only. Use with care.

        .. versionadded:: 1.2.0
           Added for ByteBlower Endpoint support.

        :meta private:
        """

    def add(self, frame_content: 'Ether', stream: 'TxStream') -> None:
        """Add created frame to the stream.

        .. warning::
           Internal use only. Use with care.

        .. versionadded:: 1.2.0
           Added for ByteBlower Endpoint support.

        :meta private:
        """

        # Add this frame to the stream
        frame_content = bytearray(bytes(frame_content))

        # The ByteBlower API expects an 'str' as input
        # for the Frame::BytesSet(), we need to convert the bytearray.
        hexbytes = ''.join((format(b, '02x') for b in frame_content))
        self._frame: 'TxFrame' = stream.FrameAdd()
        self._frame.BytesSet(hexbytes)

        if self._latency_tag:
            # Enable latency for this frame.
            # The frame frame contents will be altered
            # so it contains a timestamp.
            frame_tag: 'FrameTagTx' = self._frame.FrameTagTimeGet()
            frame_tag.Enable(True)

        # Enable auto checksum, ....
        self._frame.L3AutoChecksumEnable(True)
        self._frame.L3AutoLengthEnable(True)
        self._frame.L4AutoChecksumEnable(True)
        self._frame.L4AutoLengthEnable(True)

    def release(self, stream: 'TxStream') -> None:
        """
        Release this frame resources used on the ByteBlower system.

        .. note::
           The resources related to the stream itself is not released.
        """
        try:
            bb_frame = self._frame
            del self._frame
        except AttributeError:
            logging.warning('Frame: Already destroyed?', exc_info=True)
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
