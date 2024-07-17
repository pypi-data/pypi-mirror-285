"""ByteBlower Port interface module."""
import logging
from abc import ABC, abstractmethod
from collections import abc
from ipaddress import IPv4Address, IPv4Network, IPv6Address, IPv6Network
from itertools import count
from typing import (  # for type hinting
    TYPE_CHECKING,
    Dict,
    Iterator,
    List,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from byteblowerll.byteblower import (  # for type hinting
    ByteBlowerPort,
    EthernetConfiguration,
    Layer3Configuration,
    Layer25Configuration,
    VLANTag,
)

from .._helpers.taggable import Taggable
from .._host.server import Server  # for type hinting
from ..constants import UDP_DYNAMIC_PORT_START

if TYPE_CHECKING:
    # NOTE: Used in documentation only
    from .._scenario import Scenario
    from .._traffic.flow import Flow

_MAC_FORMAT = "{BYTE0:02x}:{BYTE1:02x}:{BYTE2:02x}" \
    ":{BYTE3:02x}:{BYTE4:02x}:{BYTE5:02x}"

# Type aliases

#: VLAN configuration parameters
#:
#: #. 'protocol_id': VLAN Protocol ID (``TPID``) (16-bit field). IEEE 802.1AD
#:    specifies the VLAN C-TAG (customer tag) and S-TAG (service-provider tag).
#:    The C-TAG (0x8100) is used on the innermost VLAN tag, while the
#:    S-TAG (0x88a8) is used on all other VLAN tags.
#:
#:    .. note:: Requires at least ByteBlower server version >= 2.20
#:
#: #. 'id': VLAN ID (``VID``). Value: 0-4095 (12-bit field)
#: #. 'drop_eligible': Drop eligible indicator (``DEI``).
#:    Value: 0-1 (1-bit field)
#: #. 'priority': Priority code point (``PCP``). Value: 0-7 (3-bit field)
VlanConfig = Mapping[str, Union[int, bool]]
VlanFlatConfig = Tuple[int, int, bool, int]
_PortConfig = Dict[str, Union[str, VlanConfig, IPv4Address, IPv6Address]]


class _MacGenerator(object):
    """Mac generator helper class."""

    __slots__ = ('_prefix',)

    _start = 1

    def __init__(self):
        self._prefix = [0x00, 0xFF, 0x0A]

    def generate_mac(self):
        result = _MAC_FORMAT.format(
            BYTE0=self._prefix[0],
            BYTE1=self._prefix[1],
            BYTE2=self._prefix[2],
            BYTE3=(int(_MacGenerator._start / (256 * 256))) % 256,
            BYTE4=int((_MacGenerator._start / (256))) % 256,
            BYTE5=_MacGenerator._start % 256,
        )
        _MacGenerator._start += 1
        return result


class Port(Taggable, ABC):
    """ByteBlower Port interface."""

    __slots__ = (
        '_server',
        '_interface',
        '_bb_port',
        '_port_l2',
        '_port_l2_5',
        '_port_l3',
        '_conf',
        '_name',
    )

    _number = count(start=1)
    _mac_generator = _MacGenerator()

    def __init__(
        self,
        server: Server,
        interface: str = None,
        name: Optional[str] = None,
        mac: Optional[str] = None,
        vlans: Optional[Sequence[VlanConfig]] = None,
        tags: Optional[Sequence[str]] = None,
        **kwargs,
    ) -> None:
        """
        Initialize a ByteBlowerPort.

        .. note::
           L2 is *only* configured if:

           1. Explicitly given MAC address
           2. Layer 3 is configured

           A port without L2/L3 configuration can for example be used
           for pure 'promiscuous' capturing of data.

        .. note::
           Configuring VLAN Protocol ID (``TPID``) requires at least
           ByteBlower server version >= 2.20
        """
        super().__init__(tags=tags)
        self._server = server
        self._interface = interface

        self._bb_port: ByteBlowerPort = None
        self._port_l2: EthernetConfiguration = None
        self._port_l2_5: Optional[List[Layer25Configuration]] = None
        self._port_l3: Layer3Configuration = None
        self._conf: _PortConfig = {}

        # NOTE: Always increment, even with given name
        port_number = next(Port._number)
        if name is not None:
            self._name = name
        else:
            self._name = f'Port {port_number}'

        if kwargs:
            logging.error(
                'Unsupported keyword arguments for %r on %r: %r', self._name,
                self._interface,
                [f'{key}={value!r}' for key, value in kwargs.items()]
            )
            raise ValueError(
                f'Unsupported configuration parameters for {self._name!r}'
                f' on {self._interface!r}: {[key for key in kwargs]!r}'
            )

        if self._interface is None:
            raise ValueError(
                f'Missing interface name for ByteBlower Port {self._name!r}'
            )

        if mac is not None:
            self._conf['mac'] = mac

        if vlans is not None:
            # Sanity checks
            if not isinstance(vlans, abc.Sequence):
                raise ValueError(
                    'VLAN configuration is not a sequence of items'
                    f' but {type(vlans)!r}'
                )
            for vlan_config in vlans:
                if not isinstance(vlan_config, abc.Mapping):
                    raise ValueError(
                        'VLAN configuration item is not a mapping'
                        f' but {type(vlan_config)!r}'
                    )
            self._conf['vlans'] = vlans

        if tags is not None:
            for tag in tags:
                self.add_tag(tag)

    def _configure(self):
        self._bb_port: ByteBlowerPort = (
            self._server.bb_server.PortCreate(self._interface)
        )

        mac_addr = self._conf.get('mac')
        if mac_addr is not None:
            logging.info('Setting MAC to %r', mac_addr)
            try:
                self._configure_l2(mac_addr)
            except Exception:
                logging.exception(
                    'Failed to set MAC of ByteBlower port: value: %r.'
                    ' Fall-back to auto-generated MAC address.', mac_addr
                )
                self._configure_l2_mac()
            # Layer 2.5 configuration MUST be done after L2 and before L3
            self._configure_l2_5()
        self._port_l3 = self._configure_l3()
        logging.debug(self._bb_port.DescriptionGet())

    def _configure_l2(self, mac_addr: Optional[str] = None) -> None:
        # Check if Layer 2 is already configured on this port
        if self._port_l2 is None:
            self._port_l2 = self._bb_port.Layer2EthIISet()
            self._configure_l2_mac(mac_addr=mac_addr)

    def _configure_l2_mac(self, mac_addr: Optional[str] = None) -> None:
        """Configure L2 MAC address.

        .. note::
           Use at base Port only!
           Forces generating and setting MAC when configuration
           with user-provided MAC address fails.

        :param mac_addr:
           If given, configure that MAC address, defaults to None
        :type mac_addr: Optional[str], optional
        """
        if mac_addr is None:
            mac_addr = Port._mac_generator.generate_mac()
        self._port_l2.MacSet(mac_addr)

    def _configure_l2_5(self) -> None:
        if self._port_l2_5 is None:
            vlans = self._conf.get('vlans')
            if vlans is not None:
                self._configure_l2_5_vlans(vlans)

    def _configure_l2_5_vlans(self, vlans: Sequence[VlanConfig]) -> None:
        if self._port_l2_5 is None:
            self._port_l2_5 = []
        for vlan_config in vlans:
            vlan_tag = self._configure_l2_5_vlan(**vlan_config)
            self._port_l2_5.append(vlan_tag)

    def _configure_l2_5_vlan(
        self,
        id: Optional[int] = None,
        drop_eligible: Optional[bool] = None,
        priority: Optional[int] = None,
        protocol_id: Optional[int] = None,
        **kwargs
    ) -> None:
        # Sanity checks
        if kwargs:
            logging.error(
                'Unsupported VLAN configuration parameters for %r on %r: %r',
                self._name, self._interface,
                [f'{key}={value!r}' for key, value in kwargs.items()]
            )
            raise ValueError(
                'Unsupported VLAN configuration configuration parameters'
                f' for {self._name!r} on {self._interface!r}'
                f': {[key for key in kwargs]!r}'
            )
        if id is not None and (id < 0 or id > 4095):
            raise ValueError(
                f'Invalid VLAN ID for {self._name!r} on {self._interface!r}.'
                ' MUST be 0-4095.'
            )
        if priority is not None and (priority < 0 or priority > 7):
            raise ValueError(
                f'Invalid VLAN PCP for {self._name!r} on {self._interface!r}.'
                ' MUST be 0-7.'
            )
        vlan_tag: VLANTag = self._bb_port.Layer25VlanAdd()
        vlan_tag.IDSet(id)
        if drop_eligible is not None:
            vlan_tag.DropEligibleSet(bool(drop_eligible))
        if priority is not None:
            vlan_tag.PrioritySet(priority)
        if protocol_id is not None:
            # NOTE: Requires at least ByteBlower server version >= 2.20
            vlan_tag.ProtocolIDSet(protocol_id)
        return vlan_tag

    @abstractmethod
    def _configure_l3(self) -> Layer3Configuration:
        raise NotImplementedError()

    def release(self) -> None:
        """
        Release this endpoint resources used on the ByteBlower system.

        .. warning::
           Releasing resources related to traffic generation and analysis
           should be done *first* via the :meth:`Scenario.release()`
           and/or :meth:`Flow.release()`.

        .. note::
           The ByteBlower Server is not released. This should be done
           afterwards via :meth:`Server.release()`
        """
        try:
            bb_port = self._bb_port
            del self._bb_port
        except AttributeError:
            logging.warning('Port: Already destroyed?', exc_info=True)
        else:
            self._server.bb_server.PortDestroy(bb_port)

    def __del__(self) -> None:
        logging.debug("Should destroy port")

    @property
    def name(self) -> str:
        """Return this endpoint's given friendly name."""
        return self._name

    @property
    def mac(self) -> str:
        """Return the MAC address currently configured on this endpoint."""
        return self._port_l2.MacGet()

    @property
    @abstractmethod
    def failed(self) -> bool:
        """Return whether (IP) address configuration failed."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def ip(self) -> Union[IPv4Address, IPv6Address]:
        """
        Return the *preferred* IP address.

        .. note::
           Subject to change in dual stack implementations.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def network(self) -> Union[IPv4Network, IPv6Network]:
        """
        Return the network of the *preferred* IP address.

        .. note::
           Subject to change in dual stack implementations.
        """
        raise NotImplementedError()

    @property
    @abstractmethod
    def gateway(self) -> Union[IPv4Address, IPv6Address]:
        """
        Return the default gateway.

        .. note::
           Subject to change in dual stack implementations.
        """
        raise NotImplementedError()

    # NOTE: Deprecated ``is_natted`` in v1.2.0,
    # TODO: Remove ``is_natted`` in v1.4.0
    @property
    def is_natted(self) -> bool:
        """
        Return whether this endpoint requires NAT/NAPT discovery.

        .. deprecated:: 1.2.0
           Use :meth:`require_nat_discovery` instead. Will be removed in v1.4.0

        :meta private:
        """
        logging.warning(
            'DEPRECATED: Port.is_natted is replaced by'
            ' Port.require_nat_discovery. It will be removed'
            ' in the next release. Please update your script accordingly.'
        )
        return self.require_nat_discovery

    @property
    def require_nat_discovery(self) -> bool:
        """
        Return whether this endpoint requires NAT/NAPT discovery.

        This is typically required when this endpoint is located
        behind a NAT/NAPT gateway or you are testing on a
        `carrier-grade NAT`_ (CGN/CGNAT, `RFC 6888`_) network.

        .. _carrier-grade NAT: https://en.wikipedia.org/wiki/Carrier-grade_NAT
        .. _RFC 6888: https://datatracker.ietf.org/doc/html/rfc6888

        .. note::
           Hook function for extending Port implementations.

        .. versionchanged:: 1.2.0
           Improved naming for NAT/NAPT discovery related interfaces.
        """
        return False

    def discover_nat(
        self,
        remote_port: 'Port',  # pylint: disable=unused-argument
        remote_udp_port: int = UDP_DYNAMIC_PORT_START,  # pylint: disable=unused-argument
        local_udp_port: int = UDP_DYNAMIC_PORT_START
    ) -> Tuple[Union[IPv4Address, IPv6Address], int]:
        """
        Resolve the IP address (and/or UDP port) as seen by `remote_port`.

        This will resolve either the IP address of the endpoint
        or the public IP address of the (IPv4 NAT/NAPT) gateway when
        the endpoint is using IPv4 and is located behind a NAT/NAPT
        gateway.

        .. note::
           UDP ports (``remote_udp_port`` and ``local_udp_port``) can be
           left to the default if you are only interested in the public IP.

        .. versionchanged:: 1.2.0
           Make endpoint interfaces consistent. Generic interface
           which will return the *own* IP address and *local* UDP
           port when no address/port discovery is required.
        """
        return self.ip, local_udp_port

    @property
    def server(self) -> Server:
        return self._server

    @property
    def bb_port(self) -> ByteBlowerPort:
        return self._bb_port

    @property
    def layer2_5(self) -> Sequence[Layer25Configuration]:
        """Layer 2.5 configurations of the ByteBlower Lower Layer API.

        :return: Ordered collection of Layer 2.5 Configuration objects
        :rtype: Sequence[Layer25Configuration]
        """
        # NOTE: We return the cached list instead of the actual configured list
        #       on the ByteBlower Port
        # return (self._bb_port.Layer25VlanGet() +
        #         self._bb_port.Layer25PPPoEGet())
        return self._port_l2_5 or tuple()

    @property
    def vlan_config(self) -> Iterator[Sequence[VlanFlatConfig]]:
        """VLAN configurations of the ByteBlower Lower Layer API.

        :return:
           Ordered collection (Outer -> Inner) of VLAN configuration tuples
        :yield: VLAN configuration for current layer 2.5
        :rtype: Iterator[Sequence[VlanFlatConfig]]
        """
        return (
            (
                l2_5.ProtocolIDGet(),
                l2_5.IDGet(),
                l2_5.DropEligibleGet(),
                l2_5.PriorityGet(),
            ) for l2_5 in self.layer2_5 if isinstance(l2_5, VLANTag)
        )

    @property
    def layer3(self) -> Layer3Configuration:
        """
        Layer 3 configuration of the ByteBlower Lower Layer API.

        .. note::
           Subject to change in dual stack implementations.
        """
        return self._port_l3

    @name.setter
    def name(self, new_name: str) -> None:
        self._name = new_name

    @property
    def port_type(self) -> str:
        return "Wired"
