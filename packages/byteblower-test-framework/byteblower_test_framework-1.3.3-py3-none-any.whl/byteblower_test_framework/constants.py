"""
Constants used along the ByteBlower Test Framework.

.. versionadded:: 1.2.0
   Keep all commonly used constants together.

.. _RFC 6335, Port Number Ranges: https://datatracker.ietf.org/doc/html/rfc6335#section-6
.. _Dynamic, private or ephemeral ports: https://en.wikipedia.org/wiki/List_of_TCP_and_UDP_port_numbers#Dynamic,_private_or_ephemeral_ports
"""  # pylint: disable=line-too-long

# IPv4 endpoint constants

#: Default netmask for an :class:`IPv4Port`
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
DEFAULT_IPV4_NETMASK = '255.255.255.0'

# Ethernet frame constants

#: Default length for a frame.
#:
#: This is the Ethernet frame size *excluding* FCS.
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
DEFAULT_FRAME_LENGTH: int = 1024  # [Bytes]

# IP frame constants

#: Default value for IP Differentiated Services Code Point (DSCP).
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
DEFAULT_IP_DSCP: int = 0x00
#: Default value for IP Explicit Congestion Notification (ECN).
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
DEFAULT_IP_ECN: int = 0x00

# UDP frame constants

#: First available UDP / TCP port number for dynamic assignment.
#:
#: It is the fir port number which is not in the range of port numbers
#: allocated by IANA for System Ports or User Ports.
#:
#: The range 49152-65535 (2^15 + 2^14 to 2^16 - 1) contains
#: dynamic or private ports that cannot be registered with IANA.
#:
#: See also:
#:
#: * `RFC 6335, Port Number Ranges`_
#: * `Dynamic, private or ephemeral ports`_
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
UDP_DYNAMIC_PORT_START: int = 49152

# Traffic generation constants

#: Default rate at which the frames are transmitted
#: in frame blasting based flows (in frames per second).
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
DEFAULT_FRAME_RATE: float = 100.0

#: Number of frames to define when you want to transmit *forever*
#: in frame blasting based flows.
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
INFINITE_NUMBER_OF_FRAMES: int = -1

#: Default number of frames to transmit
#: in frame blasting based flows.
#:
#: .. versionchanged:: 1.2.0
#:    Moved *common constants* to the
#:    ``byteblower_test_framework.constants`` module.
DEFAULT_NUMBER_OF_FRAMES: int = INFINITE_NUMBER_OF_FRAMES

#: Default packetization used for G.711 voice traffic simulation.
#: Defined in number of milliseconds
#:
#: .. versionchanged:: 1.2.0
#:    Renamed from ``DEFAULT_PACKETIZATION`` and moved *common constants*
#:    to the ``byteblower_test_framework.constants`` module.
DEFAULT_G711_PACKETIZATION: int = 20  # ms
