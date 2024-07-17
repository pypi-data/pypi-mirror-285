"""ByteBlower TCP interface module."""
import logging
from datetime import timedelta
from typing import Generator, List, Optional, Union, cast  # for type hinting

# Helper functions to parse the strings (TCP congestion avoidance, ...)
# to the enumerations used by the API and vice versa
from byteblowerll.byteblower import HTTPClient  # for type hinting
from byteblowerll.byteblower import HTTPClientMobile  # for type hinting
from byteblowerll.byteblower import HTTPRequestStatus  # for type hinting
from byteblowerll.byteblower import HTTPServer  # for type hinting
from byteblowerll.byteblower import HTTPSessionInfo  # for type hinting
from byteblowerll.byteblower import TCPSessionInfo  # for type hinting
from byteblowerll.byteblower import (
    ConfigError,
    HTTPServerStatus,
    ParseTCPCongestionAvoidanceAlgorithmFromString,
    TechnicalError,
)

from .._analysis.storage.tcp import TcpStatusData
from .._endpoint.endpoint import Endpoint
from .._endpoint.port import Port
from .._helpers.capabilities import (
    CAPABILITY_TCP_L4S,
    DESCRIPTION_CAPABILITY_TCP_L4S,
    capability_supported,
)
from .._helpers.compat import CompatUnsupportedFeature
from .._helpers.syncexec import SynchronizedExecutable  # for type hinting
from ..exceptions import (
    ByteBlowerTestFrameworkException,
    IncompatibleHttpServer,
    InvalidInput,
)
from ._http_client_controller import (
    EndpointTCPClientController,
    PortTCPClientController,
)
from .constants import HttpMethod, TCPCongestionAvoidanceAlgorithm
from .flow import RuntimeErrorInfo  # for type hinting
from .flow import Flow


class TcpFlow(Flow):
    """
    Flow, supporting multiple and/or restarting TCP clients.

    - Single HTTP server on the "WAN side" of the network.
    - One or multiple clients on the "CPE side" of the network.
    """

    __slots__ = (
        '_bb_tcp_server',
        '_bb_tcp_clients',
        '_http_method',
        '_applied_http_method',
        '_tcp_status_data',
        '_tcp_client_controller',
        '_client_port',
        '_server_port',
    )

    _CONFIG_ELEMENTS = Flow._CONFIG_ELEMENTS + ('http_method',)

    def __init__(
        self,
        source: Union[Port, Endpoint],
        destination: Union[Port, Endpoint],
        name: Optional[str] = None,
        http_method: HttpMethod = HttpMethod.AUTO,
        **kwargs,
    ) -> None:
        """
        Create a new TCP Flow.

        No clients, servers or sessions are created yet.

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
        :raises NotImplementedError: When the HTTP method provided
           is not supported. Only Automatic method is supported for now.
        """
        super().__init__(source, destination, name=name, **kwargs)
        self._bb_tcp_server: Optional[HTTPServer] = None
        self._bb_tcp_clients: Union[List[HTTPClient],
                                    List[HTTPClientMobile]] = []
        self._http_method = http_method
        self._applied_http_method = http_method
        self._tcp_status_data = TcpStatusData()

        self._tcp_client_controller: Union[PortTCPClientController,
                                           EndpointTCPClientController]

        self._server_port: Port
        self._client_port: Union[Port, Endpoint]

        # Sanity checks
        if self._http_method != HttpMethod.AUTO:
            raise NotImplementedError(
                f'TCP Flow {self.name!r} only supports'
                ' automatic HTTP method for now'
            )

    @property
    def http_method(self) -> str:
        """HTTP method used for HTTP (client) session."""
        return self._applied_http_method.value

    @property
    def finished(self) -> bool:
        """Returns True if the flow is done."""
        return self._tcp_client_controller.finished(
            self._client_port, self._bb_tcp_clients
        )

    @property
    def runtime_error_info(self) -> RuntimeErrorInfo:
        error_info = {}
        http_server_status = self._tcp_status_data._server_status
        if http_server_status == HTTPServerStatus.Error:
            # NOTE: No error message available for the server
            # server_error_message = (
            #     self._tcp_status_data._server_error_message
            # )
            server_error_message = "Failed to start HTTP Server"
            error_info['server_error_message'] = server_error_message
        client_error_messages = [
            client_error_message for (
                http_request_status,
                client_error_message,
            ) in self._tcp_status_data._client_status
            if http_request_status == HTTPRequestStatus.Error
        ]
        if client_error_messages:
            error_info['client_error_messages'] = client_error_messages
        return error_info

    def _set_tcp_server(
        self,
        server_port: Optional[Port] = None,
        tcp_port: Optional[int] = None,
        enable_tcp_prague: Optional[bool] = None,
        receive_window_scaling: Optional[int] = None,
        slow_start_threshold: Optional[int] = None,
        caa: Optional[TCPCongestionAvoidanceAlgorithm] = None,
    ) -> Optional[HTTPServer]:
        """Create a HTTP server.

        .. note::
           When a TCP port is given, an existing HTTP server can be re-used.

        :param server_port: Force HTTP server on the given ByteBlower Port.
           When set to ``None``, choose the port based on the :ref:HttpMethod,
           defaults to None
        :type server_port: Optional[Port], optional
        :param tcp_port: TCP port where the HTTP server listens to,
           defaults to None
        :type tcp_port: Optional[int], optional
        :param enable_tcp_prague: Whether TCP Prague should be enabled,
           defaults to None
        :type enable_tcp_prague: Optional[bool], optional
        :param receive_window_scaling: When given, enable receive window
           scaling with the given scale factor, defaults to None
        :type receive_window_scaling: Optional[int], optional
        :param slow_start_threshold: TCP Slow start threshold value,
           defaults to None
        :type slow_start_threshold: Optional[int], optional
        :param caa: Use the given TCP congestion avoidance algorithm,
           defaults to None (server default)
        :type caa: Optional[TCPCongestionAvoidanceAlgorithm], optional
        :raises ByteBlowerTestFrameworkException: When a TCP server is
           already configured.
        :raises NotImplementedError: When no ``server_port`` is given and
           HttpMethod is not set to AUTO.
        :raises IncompatibleHttpServer: When an HTTP server is already
           configured with incompatible settings.
        :return: The new or existing HTTP Server. When it is already active,
           ``None`` is returned since we don't allow reconfiguring it
           once started.
        :rtype: Optional[HTTPServer]
        """
        # Sanity checks
        if self._bb_tcp_server:
            raise ByteBlowerTestFrameworkException('TCP server is already set')

        # Set the default client and server port
        if not server_port:
            if self._http_method != HttpMethod.AUTO:
                # TODO - Implement for given HTTP Method
                raise NotImplementedError(
                    f'TCP Flow {self.name!r} only support'
                    ' automatic HTTP method (for now)'
                )
            if self.source.require_nat_discovery:
                # Base Flow does not allow both source and destination
                # behind a NAT/NAPT gateway
                assert not self.destination.require_nat_discovery, (
                    'Source + destination behind a NAT/NAPT gateway'
                    ' is not supported'
                )
                server_port = self.destination
            else:
                server_port = self.source

        # Sanity checks
        if enable_tcp_prague is not None:
            capability_supported(
                server_port, CAPABILITY_TCP_L4S, DESCRIPTION_CAPABILITY_TCP_L4S
            )

        if tcp_port is not None:
            # Re-use existing HTTP Server.
            # Raise an error when incompatible settings are requested.
            for http_server in server_port.bb_port.ProtocolHttpServerGet():
                if http_server.PortGet() != tcp_port:
                    continue

                if (enable_tcp_prague is not None and
                        http_server.TcpPragueIsEnabled() != enable_tcp_prague):
                    raise IncompatibleHttpServer()
                if receive_window_scaling is not None:
                    if not http_server.ReceiveWindowScalingIsEnabled():
                        raise IncompatibleHttpServer()
                    if (http_server.ReceiveWindowScalingValueGet()
                            != receive_window_scaling):
                        raise IncompatibleHttpServer()
                if (slow_start_threshold is not None
                        and (http_server.SlowStartThresholdGet()
                             != slow_start_threshold)):
                    raise IncompatibleHttpServer()
                if caa is not None and (
                        http_server.TcpCongestionAvoidanceAlgorithmGet()
                        != ParseTCPCongestionAvoidanceAlgorithmFromString(
                            caa.value)):
                    raise IncompatibleHttpServer()

                self._bb_tcp_server = http_server

                http_server_status = http_server.StatusGet()
                if http_server_status == HTTPServerStatus.Running:
                    # Do not return the HTTP server.
                    # The caller should not start or re-configure
                    # active HTTP servers.
                    return None
                return self._bb_tcp_server

        # Create a TCP server on the destination.
        http_server: HTTPServer = server_port.bb_port.ProtocolHttpServerAdd()
        if tcp_port is not None:
            http_server.PortSet(tcp_port)
        if enable_tcp_prague is not None:
            logging.info('Endpoint %r: Enabling TCP Prague.', server_port.name)
            http_server.TcpPragueEnable(enable_tcp_prague)
        if receive_window_scaling is not None:
            http_server.ReceiveWindowScalingEnable(True)
            http_server.ReceiveWindowScalingValueSet(receive_window_scaling)
        if slow_start_threshold is not None:
            http_server.SlowStartThresholdSet(slow_start_threshold)
        if caa is not None:
            http_server.TcpCongestionAvoidanceAlgorithmSet(
                ParseTCPCongestionAvoidanceAlgorithmFromString(caa.value)
            )
        self._bb_tcp_server = http_server

        return self._bb_tcp_server

    def _set_tcp_client(
        self,
        client_port: Optional[Union[Port, Endpoint]] = None,
        server_port: Optional[Port] = None
    ):
        # Set the default client and server port
        if not client_port and not server_port:
            if self.source.require_nat_discovery:
                # Base Flow does not allow both source and destination
                # behind a NAT/NAPT gateway
                assert not self.destination.require_nat_discovery, (
                    'Source + destination behind a NAT/NAPT gateway'
                    ' is not supported'
                )
                logging.debug('%s: Server at destination', self.name)
                server_port = self.destination
                client_port = self.source
            else:
                logging.debug('%s: Server at source', self.name)
                server_port = self.source
                client_port = self.destination

        elif not server_port:
            raise InvalidInput(
                f'TCP Flow {self.name!r}: Client Port {client_port.name!r}'
                ' given without server Port'
            )
        elif not client_port:
            raise InvalidInput(
                f'TCP Flow {self.name!r}: Server Port {server_port.name!r}'
                ' given without client Port'
            )

        # NOTE: This check will also work when _client_port / _server_port
        #       were not configured yet:
        if (getattr(self, '_server_port', server_port) is not server_port or
                getattr(self, '_client_port', client_port) is not client_port):
            raise InvalidInput(
                'Using inconsistent HTTP Server/Client endpoints'
            )
        self._server_port = server_port
        self._client_port = client_port

        if getattr(self, '_tcp_client_controller', None) is None:
            if isinstance(client_port, Port):
                self._tcp_client_controller = PortTCPClientController
            elif isinstance(client_port, Endpoint):
                self._tcp_client_controller = EndpointTCPClientController

        if self._http_method == HttpMethod.AUTO:
            if self._client_port == self.source:
                logging.debug('%s: Using PUT', self.name)
                self._applied_http_method = HttpMethod.PUT
            else:
                logging.debug('%s: Using GET', self.name)
                self._applied_http_method = HttpMethod.GET

    def _client_supports_tcp_parameters(self) -> bool:
        """Return whether the HTTP Client port supports setting TCP parameters.

        This is related to the TCP parameters which can
        be given to the :meth:`_add_client_session`.

        :return: Whether or not setting TCP parameters is supported.
        :rtype: bool
        """
        self._set_tcp_client()
        return self._tcp_client_controller.supports_tcp_parameters()

    def _add_client_session(
        self,
        client_port: Optional[Union[Port, Endpoint]] = None,
        server_port: Optional[Port] = None,
        request_duration: Optional[timedelta] = None,
        request_size: Optional[int] = None,
        maximum_bitrate: Optional[Union[int, float]] = None,
        ittw: Optional[timedelta] = None,
        enable_tcp_prague: Optional[bool] = None,
        receive_window_scaling: Optional[int] = None,
        slow_start_threshold: Optional[int] = None,
        caa: Optional[TCPCongestionAvoidanceAlgorithm] = None,
        tcp_port: Optional[int] = None,
        ip_traffic_class: Optional[int] = None,
    ) -> Generator[SynchronizedExecutable, None, Union[HTTPClient,
                                                       HTTPClientMobile]]:
        """Start a "scheduled" HTTP session.

        .. note::
           The returned HTTP client session is added to the
           list of client sessions, but not yet started!

        :param client_port: Force HTTP Client on the given
           ByteBlower Port or endpoint, defaults to None
        :type client_port: Optional[Union[Port, Endpoint]], optional
        :param server_port: Force HTTP Server on the given ByteBlower Port,
           defaults to None
        :type server_port: Optional[Port], optional
        :param request_duration: Duration of the HTTP request Mutual exclusive
           with ``request_size``, defaults to None
        :type request_duration: Optional[timedelta], optional
        :param request_size: Size of the HTTP request (in Bytes).
           Mutual exclusive with ``request_duration``, defaults to None
        :type request_size: Optional[int], optional
        :param maximum_bitrate: Limit the data traffic rate
           (in bits per second), defaults to None (== *no limit*)
        :type maximum_bitrate:  Optional[Union[int, float]], optional
        :param ittw: Initial time to wait to start the flow, defaults to None
        :type ittw: Optional[timedelta], optional
        :param receive_window_scaling: Receive window scaling value of TCP,
           defaults to None
        :type receive_window_scaling: Optional[int], optional
        :param slow_start_threshold: Slow start threshold value of TCP,
           defaults to None
        :type slow_start_threshold: Optional[int], optional
        :param caa: TCP Congestion Avoidance algorithm to use, defaults
           defaults to None (*default algorithm use by the ByteBlower Server*)
        :type caa: Optional[TCPCongestionAvoidanceAlgorithm], optional
        :param tcp_port: TCP port used for this client, defaults to None
           (*ByteBlower Server automatically assigns next available port*)
        :type tcp_port: Optional[int], optional
        :param ip_traffic_class: The IP traffic class value is used to
           specify the exact value of either the *IPv4 ToS field* or the
           *IPv6 Traffic Class field*,, defaults to None
        :type ip_traffic_class: Optional[int], optional
        :return: Initialized HTTP client instance
        :yield: Executable for synchronized start / stop
        :rtype: Generator[SynchronizedExecutable, None, Union[HTTPClient,
            HTTPClientMobile]]
        """
        self._set_tcp_client(client_port=client_port, server_port=server_port)

        # Sanity checks
        if enable_tcp_prague is not None:
            capability_supported(
                self._client_port, CAPABILITY_TCP_L4S,
                DESCRIPTION_CAPABILITY_TCP_L4S
            )

        http_client_generator = self._tcp_client_controller.add_client_session(
            http_method=self._applied_http_method,
            client_port=self._client_port,
            server_port=self._server_port,
            bb_tcp_server=self._bb_tcp_server,
            request_duration=request_duration,
            request_size=request_size,
            maximum_bitrate=maximum_bitrate,
            enable_tcp_prague=enable_tcp_prague,
            ittw=ittw,
            receive_window_scaling=receive_window_scaling,
            slow_start_threshold=slow_start_threshold,
            caa=caa,
            tcp_port=tcp_port,
            ip_traffic_class=ip_traffic_class,
        )

        http_client = yield from http_client_generator

        # Add the returned HTTP Client instance
        self._bb_tcp_clients.append(http_client)

        return http_client

    def _last_client_session(self) -> Union[HTTPClient, HTTPClientMobile]:
        if not self._bb_tcp_clients:
            raise ByteBlowerTestFrameworkException('No TCP client created yet')
        return self._bb_tcp_clients[-1]

    def wait_until_finished(
        self, wait_for_finish: timedelta, result_timeout: timedelta
    ) -> None:
        """Wait until the flow finished traffic generation and processing.

        :param wait_for_finish: Time to wait for sessions closing
           and final packets being received.
        :type wait_for_finish: timedelta
        :param result_timeout: Time to wait for Endpoints to finalize
           and return their results to the Meeting Point.
        :type result_timeout: timedelta
        """
        self._tcp_client_controller.wait_until_finished(
            self._client_port, self._bb_tcp_clients, wait_for_finish,
            result_timeout
        )

    def stop(self) -> None:
        # 1. Stop all TCP clients
        self._tcp_client_controller.stop(self._bb_tcp_clients)

        # 2. Stop TCP Server
        if self._bb_tcp_server is not None:
            self._bb_tcp_server.Stop()

        super().stop()

    def analyse(self) -> None:
        self._tcp_status_data._server_status = self._bb_tcp_server.StatusGet()
        # NOTE: No error message available for the server
        # self._tcp_status_data._server_error_message = (
        #     self._bb_tcp_server.ErrorMessageGet()
        # )
        for tcp_client in self._bb_tcp_clients:
            try:
                http_request_status = cast(
                    HTTPRequestStatus, tcp_client.RequestStatusGet()
                )
            except (TechnicalError, CompatUnsupportedFeature) as error:
                # NOTE: Raises UnsupportedFeature since API v2.22
                # NOTE: HTTPClientMobile.RequestStatusGet() is not implemented
                #       (as for API v2.21)
                http_request_status = None
                server_client_id = cast(str, tcp_client.ServerClientIdGet())
                logging.warning(
                    "%s: Unable to get HTTP Client %r request status: %s",
                    self._client_port.name,
                    server_client_id,
                    error.getMessage(),
                )
            client_error_message = cast(str, tcp_client.ErrorMessageGet())
            self._tcp_status_data._client_status.append(
                (http_request_status, client_error_message)
            )

            # Add L4S negotiation status info
            client_error_message = self._get_l4s_negotiation_status(tcp_client)
            if client_error_message is not None:
                self._tcp_status_data._client_status.append(
                    (HTTPRequestStatus.Error, client_error_message)
                )

        super().analyse()

    def _get_l4s_negotiation_status(
        self, tcp_client: Union[HTTPClient, HTTPClientMobile]
    ) -> Optional[str]:
        try:
            if (not tcp_client.TcpPragueIsEnabled()
                    and not self._bb_tcp_server.TcpPragueIsEnabled()):
                return None

            client_http_session_info = cast(
                HTTPSessionInfo, tcp_client.HttpSessionInfoGet()
            )
            try:
                client_tcp_session_info = cast(
                    TCPSessionInfo,
                    client_http_session_info.TcpSessionInfoGet()
                )
                prague_is_enabled = cast(
                    bool, client_tcp_session_info.PragueIsEnabled()
                )
            except ConfigError as error:
                # NOTE: TcpSessionInfoGet() is not implemented
                #       on HTTPClientMobile (as for ByteBlower <= v2.22.0)
                server_client_id = cast(str, tcp_client.ServerClientIdGet())
                logging.warning(
                    "%s: Unable to get HTTP Client %r TCP Session info: %s."
                    " Getting it from the HTTP Server.",
                    self._client_port.name,
                    server_client_id,
                    error.getMessage(),
                )
                server_http_session_info = cast(
                    HTTPSessionInfo,
                    self._bb_tcp_server.HttpSessionInfoGet(server_client_id)
                )
                server_tcp_session_info = cast(
                    TCPSessionInfo,
                    server_http_session_info.TcpSessionInfoGet()
                )
                prague_is_enabled = cast(
                    bool, server_tcp_session_info.PragueIsEnabled()
                )
        except CompatUnsupportedFeature as error:
            # NOTE: TCP Prague is not supported by ByteBlower <= v2.22
            server_client_id = cast(str, tcp_client.ServerClientIdGet())
            logging.info(
                "%s: L4S status not supported on HTTP Client %r: %s",
                self._client_port.name,
                server_client_id,
                error.getMessage(),
            )
            return None
        except TechnicalError as error:
            server_client_id = cast(str, tcp_client.ServerClientIdGet())
            logging.warning(
                "%s: Unable to get HTTP Client %r L4S status: %s",
                self._client_port.name,
                server_client_id,
                error.getMessage(),
            )
            return (
                'Unable to check if L4S negotiation failed'
                f': {error.getMessage()}. Server: {self._server_port.name}.'
                f' Client: {self._client_port.name}'
            )

        if not prague_is_enabled:
            return (
                f'L4S negotiation failed. Server: {self._server_port.name}.'
                f' Client: {self._client_port.name}'
            )
        return None

    def _release(self) -> None:
        client_port = self._client_port
        server_port = self._server_port

        try:
            bb_tcp_clients = self._bb_tcp_clients
            del self._bb_tcp_clients
        except AttributeError:
            logging.warning(
                'TcpFlow: TCP clients already destroyed?', exc_info=True
            )
        else:
            self._tcp_client_controller.release(client_port, bb_tcp_clients)
        try:
            del self._client_port
        except AttributeError:
            logging.warning(
                'TcpFlow: TCP client already removed?', exc_info=True
            )

        # ! FIXME: Don't destroy when re-used existing HTTP Server !
        try:
            bb_tcp_server = self._bb_tcp_server
            del self._bb_tcp_server
        except AttributeError:
            logging.warning(
                'TcpFlow: TCP server already destroyed?', exc_info=True
            )
        else:
            if bb_tcp_server is not None:
                server_port.bb_port.ProtocolHttpServerRemove(bb_tcp_server)
        try:
            del self._server_port
        except AttributeError:
            logging.warning(
                'TcpFlow: TCP server already removed?', exc_info=True
            )
