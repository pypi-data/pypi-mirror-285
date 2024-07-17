"""
Behavior module for TCP clients.

The TCPClientController extract device-specific API calls
to behavior interfaces for the test framework.
"""
import logging
from datetime import datetime, timedelta
from math import ceil
from time import sleep
from typing import (  # for type hinting
    TYPE_CHECKING,
    Generator,
    List,
    Optional,
    Union,
    cast,
)

from byteblowerll.byteblower import (
    DomainError,
    ParseHTTPRequestMethodFromString,
    ParseTCPCongestionAvoidanceAlgorithmFromString,
    RequestStartType,
)

from .._helpers.syncexec import SynchronizedExecutable
from ..exceptions import FeatureNotSupported

if TYPE_CHECKING:
    # for type hinting
    from ipaddress import IPv4Address, IPv6Address

    from byteblowerll.byteblower import (
        HTTPClient,
        HTTPClientMobile,
        HTTPServer,
    )

    from .._endpoint.endpoint import Endpoint
    from .._endpoint.port import Port
    from .constants import HttpMethod, TCPCongestionAvoidanceAlgorithm

_DEFAULT_DURATION_SECONDS: float = 10.0
_NANOSECONDS_PER_SECOND: int = 1000000000

_BYTES_PER_MB: float = 1000000.0


class PortTCPClientController(object):
    """TCP client controller for Port interfaces."""

    @staticmethod
    def supports_tcp_parameters() -> bool:
        """Return whether this HTTP Client supports setting TCP parameters.

        This is related to the TCP parameters which can
        be given to the :meth:`add_client_session`.

        :return: Whether or not setting TCP parameters is supported.
        :rtype: bool
        """
        return True

    @staticmethod
    def add_client_session(
        http_method: 'HttpMethod',
        client_port: 'Port',
        server_port: 'Port',
        bb_tcp_server: Optional['HTTPServer'] = None,
        request_duration: Optional[timedelta] = None,
        request_size: Optional[int] = None,
        maximum_bitrate: Optional[Union[int, float]] = None,
        ittw: Optional[timedelta] = None,
        enable_tcp_prague: Optional[bool] = None,
        receive_window_scaling: Optional[int] = None,
        slow_start_threshold: Optional[int] = None,
        caa: Optional['TCPCongestionAvoidanceAlgorithm'] = None,
        tcp_port: Optional[int] = None,
        ip_traffic_class: Optional[int] = None,
    ) -> Generator[SynchronizedExecutable, None, 'HTTPClient']:
        """
        Start a "scheduled" HTTP session.

        .. note::
           The returned HTTP client session is added to the
           list of client sessions, but not yet started!

        :param ittw: Initial time to wait.

        :return:
            The newly created HTTP Client.
        """
        # Create the client
        clientsession = cast(
            'HTTPClient', client_port.bb_port.ProtocolHttpClientAdd()
        )

        # Endpoint-specific configuration on the client
        # NOTE: The request start type MUST be set before configuring
        #       the initial time to wait!
        #       * (ByteBlower API v2.22 at the time of writing)
        clientsession.RequestStartTypeSet(RequestStartType.Scheduled)

        # Common configuration on the client
        _configure_client(
            client_port,
            http_method=http_method,
            clientsession=clientsession,
            remote_address=server_port.ip,
            bb_tcp_server=bb_tcp_server,
            request_duration=request_duration,
            request_size=request_size,
            maximum_bitrate=maximum_bitrate,
            ittw=ittw,
            enable_tcp_prague=enable_tcp_prague,
            tcp_port=tcp_port,
            ip_traffic_class=ip_traffic_class,
        )

        # Endpoint-specific configuration on the client

        # TCP settings
        if receive_window_scaling is not None:
            clientsession.ReceiveWindowScalingEnable(True)
            clientsession.ReceiveWindowScalingValueSet(receive_window_scaling)
        if slow_start_threshold is not None:
            clientsession.SlowStartThresholdSet(slow_start_threshold)
        if caa is not None:
            clientsession.TcpCongestionAvoidanceAlgorithmSet(
                ParseTCPCongestionAvoidanceAlgorithmFromString(caa.value)
            )

        yield SynchronizedExecutable(clientsession)
        return clientsession

    @staticmethod
    def finished(
        _endpoint: 'Port', bb_tcp_clients: List['HTTPClient']
    ) -> bool:
        """Check whether the HTTP Clients finished their session.

        :param _endpoint: Port where the client was created on
        :type _endpoint: Port
        :param bb_tcp_clients: Port-specific TCP Clients
        :type bb_tcp_clients: List['HTTPClient']
        :return: Whether HTTP sessions finished
        :rtype: bool
        """
        for tcp_client in bb_tcp_clients:
            if not tcp_client.FinishedGet():
                return False
        return True

    @staticmethod
    def wait_until_finished(
        _endpoint: 'Port', bb_tcp_clients: List['HTTPClient'],
        wait_for_finish: timedelta, _result_timeout: timedelta
    ) -> None:
        """Wait until the HTTP Clients finished their session.

        :param _endpoint: Port where the client was created on
        :type _endpoint: Port
        :param bb_tcp_clients: Port-specific TCP Clients
        :type bb_tcp_clients: List[HTTPClient]
        :param wait_for_finish: Time to wait for sessions closing
           and final packets being received.
        :type wait_for_finish: timedelta
        :param _result_timeout: Time to wait for Ports to finalize
           and return their results to the Server/Client.
        :type _result_timeout: timedelta
        """
        finish_time = datetime.now() + wait_for_finish
        for tcp_client in bb_tcp_clients:
            remaining_wait_time = finish_time - datetime.now()
            if remaining_wait_time > timedelta(seconds=0):
                try:
                    tcp_client.WaitUntilFinished(
                        ceil(remaining_wait_time.total_seconds()) *
                        _NANOSECONDS_PER_SECOND
                    )
                except DomainError as error:
                    logging.warning(
                        "Failed to wait for TCP client %r: %s",
                        tcp_client.ServerClientIdGet(),
                        error.getMessage(),
                    )
            else:
                return

    @staticmethod
    def stop(bb_tcp_clients: List['HTTPClient']) -> None:
        """Stop the HTTP Client sessions.

        :param bb_tcp_clients: Port-specific TCP Clients
        :type bb_tcp_clients: List[HTTPClient]
        """
        for tcp_client in bb_tcp_clients:
            tcp_client.RequestStop()

    @staticmethod
    def release(
        endpoint: 'Port', bb_tcp_clients: List['HTTPClient'] = None
    ) -> None:
        """Release the HTTP Clients for the given Port.

        :param endpoint: Port where the client was created on
        :type endpoint: Port
        :param bb_tcp_clients: Port-specific TCP Clients
        :type bb_tcp_clients: List[HTTPClient]
        """
        for tcp_client in bb_tcp_clients:
            endpoint.bb_port.ProtocolHttpClientRemove(tcp_client)


class EndpointTCPClientController(object):
    """HTTP client controller for Endpoint interfaces."""

    @staticmethod
    def supports_tcp_parameters() -> bool:
        """Return whether this HTTP Client supports setting TCP parameters.

        This is related to the TCP parameters which can
        be given to the :meth:`add_client_session`.

        :return: Whether or not setting TCP parameters is supported.
        :rtype: bool
        """
        return False

    @staticmethod
    def add_client_session(
        http_method: 'HttpMethod',
        client_port: 'Endpoint',
        server_port: 'Port',
        bb_tcp_server: Optional['HTTPServer'] = None,
        request_duration: Optional[timedelta] = None,
        request_size: Optional[int] = None,
        maximum_bitrate: Optional[Union[int, float]] = None,
        ittw: Optional[timedelta] = None,
        enable_tcp_prague: Optional[bool] = None,
        tcp_port: Optional[int] = None,
        ip_traffic_class: Optional[int] = None,
        **kwargs
    ) -> Generator[SynchronizedExecutable, None, 'HTTPClientMobile']:
        """
        Start a "scheduled" HTTP session.

        .. note::
           The returned Endpoint-specific HTTP client session
           is added to the list of client sessions,
           but not yet started!

        :param ittw: Initial time to wait.

        :return:
            The newly created Endpoint-specific HTTP Client.
        """
        for value in kwargs.values():
            if value is not None:
                raise FeatureNotSupported(
                    f'Configuring {value} on ByteBlower Endpoint'
                    f' {client_port.name} is not possible. This should be'
                    ' configured on the host of the endpoint instead.'
                )

        # Create the client
        clientsession = cast(
            'HTTPClientMobile', client_port.bb_endpoint.ProtocolHttpClientAdd()
        )

        # Common configuration on the client
        _configure_client(
            client_port,
            http_method=http_method,
            clientsession=clientsession,
            remote_address=server_port.ip,
            bb_tcp_server=bb_tcp_server,
            request_duration=request_duration,
            request_size=request_size,
            maximum_bitrate=maximum_bitrate,
            ittw=ittw,
            enable_tcp_prague=enable_tcp_prague,
            tcp_port=tcp_port,
            ip_traffic_class=ip_traffic_class,
        )

        # NOTE: turn this function into an "empty" generator
        #
        # See also
        #   https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/61496399#61496399  # pylint: disable=line-too-long
        # for considerations regarding performance.
        yield from ()
        return clientsession

    @staticmethod
    def finished(
        endpoint: 'Endpoint',
        _bb_tcp_clients: List['HTTPClientMobile'] = None
    ) -> bool:
        """Check whether the HTTP Clients finished their session.

        :param endpoint: Endpoint where the client was created on
        :type endpoint: Endpoint
        :param _bb_tcp_clients: Endpoint-specific TCP Clients
        :type _bb_tcp_clients: List[HTTPClientMobile]
        :return: Whether HTTP sessions finished
        :rtype: bool
        """
        return not endpoint.active

    @staticmethod
    def wait_until_finished(
        endpoint: 'Endpoint', _bb_tcp_clients: List['HTTPClientMobile'],
        wait_for_finish: timedelta, result_timeout: timedelta
    ) -> None:
        """Wait until the HTTP Clients finished their session.

        :param endpoint: Endpoint where the client was created on
        :type endpoint: Endpoint
        :param _bb_tcp_clients: Endpoint-specific TCP Clients
        :type _bb_tcp_clients: List[HTTPClientMobile]
        :param wait_for_finish: Time to wait for sessions closing
           and final packets being received.
        :type wait_for_finish: timedelta
        :param result_timeout: Time to wait for Endpoints to finalize
           and return their results to the Meeting Point.
        :type result_timeout: timedelta
        """
        finish_time = datetime.now() + wait_for_finish
        timeout = datetime.now() + result_timeout
        while datetime.now() <= finish_time:
            if EndpointTCPClientController.finished(endpoint):
                logging.debug(
                    'Endpoint %r finished transmission in time.'
                    ' Good job! 💪', endpoint.name
                )
                return
            sleep(0.5)
        logging.warning(
            'Endpoint %r did not finish transmission in time.'
            ' Waiting for some extra time.', endpoint.name
        )
        while datetime.now() <= timeout:
            if EndpointTCPClientController.finished(endpoint):
                logging.debug(
                    'Endpoint %r finished transmission after finish wait time.'
                    ' Could have done better. 😕', endpoint.name
                )
                return
            sleep(0.5)
        logging.warning(
            'Endpoint %r did not finish transmission before timeout.'
            ' Results might not be available.', endpoint.name
        )

    @staticmethod
    def stop(_bb_tcp_clients: List['HTTPClientMobile']):
        """Stop the HTTP Client sessions.

        :param _bb_tcp_clients: Endpoint-specific TCP Clients
        :type _bb_tcp_clients: List[HTTPClientMobile]
        """

    @staticmethod
    def release(
        endpoint: 'Endpoint',
        bb_tcp_clients: List['HTTPClientMobile'] = None
    ) -> None:
        """Release the HTTP Clients for the given Endpoint.

        :param endpoint: Endpoint where the client was created on
        :type endpoint: Endpoint
        :param bb_tcp_clients: Endpoint-specific TCP Clients
        :type bb_tcp_clients: List[HTTPClientMobile]
        """
        for tcp_client in bb_tcp_clients:
            endpoint.bb_endpoint.ProtocolHttpClientRemove(tcp_client)


def _configure_client(
    client_endpoint: Union['Port', 'Endpoint'],
    http_method: 'HttpMethod',
    clientsession: Union['HTTPClient', 'HTTPClientMobile'],
    remote_address: Union['IPv4Address', 'IPv6Address'],
    bb_tcp_server: Optional['HTTPServer'] = None,
    request_duration: Optional[timedelta] = None,
    request_size: Optional[int] = None,
    maximum_bitrate: Optional[Union[int, float]] = None,
    ittw: Optional[timedelta] = None,
    enable_tcp_prague: Optional[bool] = None,
    tcp_port: Optional[int] = None,
    ip_traffic_class: Optional[int] = None
) -> None:

    # Sanity checks
    if request_size is None and request_duration is None:
        logging.info(
            'Neither HTTP request size or duration are given.'
            ' Default to duration of %fs',
            _DEFAULT_DURATION_SECONDS,
        )
        request_duration = timedelta(seconds=_DEFAULT_DURATION_SECONDS)
    ittw = ittw or timedelta(seconds=0)

    if tcp_port is not None:
        clientsession.LocalPortSet(tcp_port)
    clientsession.RemoteAddressSet(remote_address.compressed)
    tcpserverport = bb_tcp_server.PortGet()
    clientsession.RemotePortSet(tcpserverport)
    clientsession.HttpMethodSet(
        ParseHTTPRequestMethodFromString(http_method.value)
    )

    ittw_nanoseconds = int(ittw.total_seconds() * _NANOSECONDS_PER_SECOND)
    clientsession.RequestInitialTimeToWaitSet(ittw_nanoseconds)

    # Sanity checks
    if request_duration is not None:
        if request_size is not None:
            logging.warning(
                'Both HTTP request duration and size are given.'
                ' Using duration.'
            )
        # Set the duration
        logging.debug('Requesting HTTP data during %s.', request_duration)
        duration_nanoseconds = int(
            request_duration.total_seconds() * _NANOSECONDS_PER_SECOND
        )
        clientsession.RequestDurationSet(duration_nanoseconds)
    elif request_size is not None:
        # Set the size
        logging.debug(
            'Requesting HTTP data of %f MB.',
            request_size / _BYTES_PER_MB,
        )
        clientsession.RequestSizeSet(request_size)

    # Session metrics
    if maximum_bitrate:
        clientsession.RequestRateLimitSet(int(maximum_bitrate / 8))

    # IP settings
    if ip_traffic_class is not None:
        clientsession.TypeOfServiceSet(ip_traffic_class)

    # TCP settings
    if enable_tcp_prague is not None:
        logging.info('Endpoint %r: Enabling TCP Prague.', client_endpoint.name)
        clientsession.TcpPragueEnable(enable_tcp_prague)
