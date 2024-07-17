"""ByteBlower HTTP interface module."""
import logging
from datetime import timedelta
from typing import Iterable, Optional, Union  # for type hinting

from .._endpoint.endpoint import Endpoint  # for type hinting
from .._endpoint.port import Port  # for type hinting
from .._helpers.syncexec import SynchronizedExecutable
from ..exceptions import ConflictingInput, NotDurationBased
from .helpers import get_ip_traffic_class
from .tcpflow import HttpMethod, TcpFlow

_LOGGER = logging.getLogger(__name__)


class HTTPFlow(TcpFlow):
    r"""
    Flow for generating and analyzing TCP and HTTP data traffic.

    HTTP flow involves a client initiating a TCP connection to a server,
    exchanging HTTP requests and responses (GET/PUT), and then closing the
    connection. This enables the transfer of web content between client and
    server.

    Since v2.22.0, ByteBlower supports L4S for HTTP flow.
    `Low Latency, Low Loss, and Scalable Throughput (L4S)`_ is a versatile
    technology enhancing internet performance across various networks like
    fibre, 5G, and Wi-Fi networks. It innovates on traditional TCP by using
    the Prague requirements, to more effectively signal and respond to
    congestion through Explicit Congestion Notification (ECN). This approach
    allows for quicker, more precise adjustments in data transmission, leading
    to increased network efficiency and reduced latency. More details on L4S
    and low latency testing can be found in `Test Case: Low Latency`_.

    .. _Test Case\: Low Latency: https://api.byteblower.com/test-framework/latest/test-cases/low-latency/overview.html
    .. _Low Latency, Low Loss, and Scalable Throughput (L4S): https://datatracker.ietf.org/doc/html/rfc9330

    .. versionchanged:: 1.3.0
       Support for L4S was added
    """  # pylint: disable=line-too-long

    __slots__ = (
        '_tcp_server_port',
        '_tcp_client_port',
        '_request_duration',
        '_request_size',
        '_initial_time_to_wait',
        '_rate_limit',
        '_enable_tcp_prague',
        '_receive_window_scaling',
        '_slow_start_threshold',
        '_maximum_bitrate',
        '_tcp_server_receive_window_scaling',
        '_tcp_server_slow_start_threshold',
        '_ip_traffic_class',
    )

    _CONFIG_ELEMENTS = TcpFlow._CONFIG_ELEMENTS + (
        'tcp_server_port',
        'maximum_bitrate',
        'enable_tcp_prague',
        'receive_window_scaling',
        'slow_start_threshold',
    )

    def __init__(
        self,
        source: Union[Port, Endpoint],
        destination: Union[Port, Endpoint],
        name: Optional[str] = None,
        http_method: HttpMethod = HttpMethod.AUTO,
        tcp_server_port: Optional[int] = None,
        tcp_client_port: Optional[int] = None,
        request_duration: Optional[Union[timedelta, float, int]] = None,
        request_size: Optional[int] = None,
        initial_time_to_wait: Optional[Union[timedelta, float,
                                             int]] = None,  # [seconds]
        rate_limit: Optional[int] = None,  # [bytes/s]
        maximum_bitrate: Optional[Union[int, float]] = None,  # [bps]
        enable_tcp_prague: Optional[bool] = None,
        receive_window_scaling: Optional[int] = None,
        slow_start_threshold: Optional[int] = None,
        ip_dscp: Optional[int] = None,
        ip_ecn: Optional[int] = None,
        ip_traffic_class: Optional[int] = None,
        **kwargs
    ) -> None:
        """Create an HTTP flow.

        :param source: Sending endpoint of the data traffic
        :type source: Union[Port, Endpoint]
        :param destination: Receiving endpoint of the data traffic
        :type destination: Union[Port, Endpoint]
        :param name:  Name of this Flow, defaults to auto-generated name
           when set to ``None``.
        :type name: Optional[str], optional
        :param http_method: HTTP Method of this request, defaults to
           HttpMethod.AUTO
        :type http_method: HttpMethod, optional
        :param tcp_server_port: TCP port of the HTTP server, defaults to None
        :type tcp_server_port: Optional[int], optional
        :param tcp_client_port: TCP port of the HTTP client, defaults to None
        :type tcp_client_port: Optional[int], optional
        :param request_duration: Duration of the HTTP data transfer.
           Mutual exclusive with ``request_size``, defaults to None
        :type request_duration: Optional[Union[timedelta, float, int]],
           optional
        :param request_size: Size of the HTTP data to transfer (in Bytes).
           Mutual exclusive with ``request_duration``, defaults to None
        :type request_size: Optional[int], optional
        :param initial_time_to_wait: Initial time to wait to start the flow,
           defaults to None
        :type initial_time_to_wait: Optional[Union[timedelta, float, int]],
           optional
        :param rate_limit: Limit the data traffic rate (in Bytes per second).
           Mutual exclusive with ``maximum_bitrate``, defaults to None
           (== *no limit*)

           .. deprecated:: 1.2.0
              Deprecated ``rate_limit`` in favor of ``maximum_bitrate``.
              Will be removed in the next release.
        :type rate_limit: Optional[int], optional
        :param maximum_bitrate: Limit the data traffic rate
           (in bits per second). Mutual exclusive with ``rate_limit``,
           defaults to None (== *no limit*)

           .. versionadded:: 1.2.0
              Added ``maximum_bitrate`` deprecating ``rate_limit``.
        :type maximum_bitrate:  Optional[Union[int, float]], optional
        :param enable_tcp_prague: When given, enable TCP Prague congestion avoidance
           algorithm on both TCP client and server, defaults to ``None``.
           (Server default; default for ByteBlower Port, host operating system
           default for ByteBlower Endpoint).

           .. note::
              - L4S support requires at least ByteBlower API v2.22.0, Server
                and Meeting Point v2.22.0, and ByteBlower Endpoint v2.22.0
              - When using Endpoints, L4S must be supported and enabled
                in the hosting OS

           .. versionadded:: 1.3.0
              Added ``enable_tcp_prague`` for L4S support in HTTP flow.
        :type enable_tcp_prague:  Optional[bool], optional
        :param receive_window_scaling: When given, enable receive window
           scaling with the given scale factor, defaults to ``None``.

           When ByteBlower Endpoints are involved, this setting will not be
           applied on them, but only on the HTTP Server on the ByteBlower Port.
           The ByteBlower Endpoint has no control over the TCP parameters of
           the host operating system's. It is then up to the Endpoint's host
           configuration whether this setting will be applicable or not.
        :type receive_window_scaling: Optional[int], optional
        :param slow_start_threshold: Slow start threshold value of TCP,
           defaults to ``None``.

           When ByteBlower Endpoints are involved, this setting will not be
           applied on them, but only on the HTTP Server on the ByteBlower Port.
           The ByteBlower Endpoint has no control over the TCP parameters of
           the host operating system's. It is then up to the Endpoint's host
           configuration whether this setting will be applicable or not.
        :type slow_start_threshold: Optional[int], optional
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
        :raises ConflictingInput: When invalid combination of configuration
           parameters is given
        """
        super().__init__(
            source, destination, name=name, http_method=http_method, **kwargs
        )
        self._tcp_server_port = tcp_server_port
        self._tcp_client_port = tcp_client_port
        self._request_size = request_size

        if isinstance(request_duration, (float, int)):
            # Convert to timedelta
            self._request_duration = timedelta(seconds=request_duration)
        else:
            # Either already timedelta or None:
            self._request_duration = request_duration
        if isinstance(initial_time_to_wait, (float, int)):
            # Convert to timedelta
            self._initial_time_to_wait = timedelta(
                seconds=initial_time_to_wait
            )
        else:
            # Either already timedelta or None:
            # Default to 0s
            self._initial_time_to_wait = initial_time_to_wait or timedelta()

        #  Sanity checks
        if rate_limit is not None:
            if maximum_bitrate is None:
                maximum_bitrate = rate_limit * 8
                logging.warning(
                    "DEPRECATED: 'rate_limit' is replaced by"
                    " 'maximum_bitrate'. This parameter will be removed in"
                    " the next feature release."
                )
            else:
                raise ConflictingInput(
                    "DEPRECATED: 'rate_limit' is replaced"
                    " by 'maximum_bitrate'. This parameter will be removed in"
                    " the next feature release."
                    " Please provide either maximum_bitrate (preferred)"
                    " or rate_limit but not both.'"
                )

        if enable_tcp_prague is not None and (ip_traffic_class is not None
                                              or ip_ecn is not None
                                              or ip_dscp is not None):
            raise ConflictingInput(
                "When enabling TCP Prague, do not provide IP traffic class"
                " and DSCP/ECN"
            )

        self._maximum_bitrate = maximum_bitrate
        self._enable_tcp_prague = enable_tcp_prague
        self._receive_window_scaling = receive_window_scaling
        self._slow_start_threshold = slow_start_threshold
        self._tcp_server_receive_window_scaling = receive_window_scaling
        self._tcp_server_slow_start_threshold = slow_start_threshold
        self._ip_traffic_class = get_ip_traffic_class(
            "IP Traffic Class",
            ip_traffic_class=ip_traffic_class,
            ip_ecn=ip_ecn,
            ip_dscp=ip_dscp,
        )
        # Sanity check
        if (self._request_duration is not None
                and self._request_size is not None):
            raise ConflictingInput(
                f'Flow {self._name!r}: Please provide'
                ' either request duration or request size but not both.'
            )

    @property
    def tcp_server_port(self) -> Optional[int]:
        """TCP port of the HTTP server."""
        return self._tcp_server_port

    @property
    def rate_limit(self) -> Optional[float]:
        """Return the requested HTTP rate limit.

        :return: The rate limit, in bytes per second.
        :rtype: Optional[float]
        """
        logging.warning(
            "DEPRECATED: 'rate_limit' is replaced by"
            " 'maximum_bitrate'. This parameter will be removed in"
            " the next feature release."
        )
        if self._maximum_bitrate:
            return self._maximum_bitrate / 8
        return None

    @property
    def maximum_bitrate(self) -> Optional[Union[int, float]]:
        """Return the requested HTTP rate limit.

        :return: The maximum bitrate, in bits per second.
        :rtype: Optional[int]
        """
        return self._maximum_bitrate

    @property
    def enable_tcp_prague(self) -> Optional[bool]:
        """
        Whether TCP Prague is enabled.

        .. versionadded:: 1.3.0
           Add enabling TCP Prague for L4S
        """
        return self._enable_tcp_prague

    @property
    def receive_window_scaling(self) -> Optional[int]:
        """TCP Receive Window scaling."""
        return self._tcp_server_receive_window_scaling

    @property
    def slow_start_threshold(self) -> Optional[int]:
        """TCP Slow Start Threshold."""
        return self._tcp_server_slow_start_threshold

    @property
    def duration(self) -> timedelta:
        """Returns the duration of the HTTP flow.

        :raises NotDurationBased: If the HTTPFlow is sized based.
        :returns: duration of the flow.
        :rtype: timedelta
        """
        if self._request_duration is not None:
            return self._request_duration
        raise NotDurationBased()

    @property
    def initial_time_to_wait(self) -> timedelta:
        """Return the time to wait before the flow starts."""
        return self._initial_time_to_wait

    def prepare_start(
        self,
        maximum_run_time: Optional[timedelta] = None,
    ) -> Iterable[SynchronizedExecutable]:
        """Start a HTTP server and schedule the client data transfer."""
        # Limit maximum run time if required
        if (maximum_run_time is not None and self._request_size is None
                and (self._request_duration is None or maximum_run_time
                     < self._request_duration + self._initial_time_to_wait)):
            self._request_duration = (
                maximum_run_time - self._initial_time_to_wait
            )

        # Create a TCP server on the destination.
        http_server = self._set_tcp_server(
            tcp_port=self._tcp_server_port,
            enable_tcp_prague=self._enable_tcp_prague,
            receive_window_scaling=self._receive_window_scaling,
            slow_start_threshold=self._slow_start_threshold
        )

        # NOTE: Persisting value, so they are available after self.release() !
        self._tcp_server_port = self._bb_tcp_server.PortGet()
        if self._bb_tcp_server.ReceiveWindowScalingIsEnabled():
            self._tcp_server_receive_window_scaling = (
                self._bb_tcp_server.ReceiveWindowScalingValueGet()
            )
        else:
            self._tcp_server_receive_window_scaling = None
        self._tcp_server_slow_start_threshold = (
            self._bb_tcp_server.SlowStartThresholdGet()
        )

        if http_server is not None:
            # New HTTP server (not re-using existing one)
            # NOTE: Does not support scheduled start!
            http_server.Start()

        # Create the first client session so we will get started
        if self._client_supports_tcp_parameters():
            client_receive_window_scaling = self._receive_window_scaling
            client_slow_start_threshold = self._slow_start_threshold
        else:
            _LOGGER.warning(
                'Flow %r: Client Endpoint does not support setting TCP session'
                ' parameters. This should be configured on the host'
                ' of the endpoint instead.', self.name
            )
            client_receive_window_scaling = None
            client_slow_start_threshold = None
        http_client_generator = self._add_client_session(
            request_duration=self._request_duration,
            request_size=self._request_size,
            maximum_bitrate=self._maximum_bitrate,
            ittw=self._initial_time_to_wait,
            enable_tcp_prague=self._enable_tcp_prague,
            receive_window_scaling=client_receive_window_scaling,
            slow_start_threshold=client_slow_start_threshold,
            tcp_port=self._tcp_client_port,
            ip_traffic_class=self._ip_traffic_class,
        )

        yield from super().prepare_start(maximum_run_time=maximum_run_time)
        yield from http_client_generator

    def release(self) -> None:
        super().release()
        super()._release()
