import logging
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Iterable, Optional, Union  # for type hinting

from byteblowerll.byteblower import DomainError

from .._analysis.bufferanalyser import BufferAnalyser
from .._endpoint.endpoint import Endpoint
from .._endpoint.port import Port  # for type hinting
from ..exceptions import (
    ByteBlowerTestFrameworkException,
    FeatureNotSupported,
    InfiniteDuration,
)
from .helpers import get_ip_traffic_class
from .tcpflow import TCPCongestionAvoidanceAlgorithm, TcpFlow

if TYPE_CHECKING:
    # NOTE: Used for type hinting only
    from .._helpers.syncexec import SynchronizedExecutable


class VideoFlow(TcpFlow):
    """Flow simulating video traffic."""

    __slots__ = (
        '_segment_size',
        '_segment_duration',
        '_buffering_goal',
        '_bytes_per_ms',
        '_bufferanalyser',
        '_last_consume_time',
        '_ip_traffic_class',
    )

    _CONFIG_ELEMENTS = TcpFlow._CONFIG_ELEMENTS + (
        "segment_size",
        "segment_duration",
        "buffering_goal",
    )

    def __init__(
        self,
        source: Port,
        destination: Port,
        name: Optional[str] = None,
        segment_size: int = 2 * 1000 * 1000,
        segment_duration: Union[timedelta, float] = timedelta(seconds=2.500),
        buffering_goal: Union[timedelta, float] = timedelta(seconds=60),
        play_goal: Union[timedelta, float] = timedelta(seconds=5),
        ip_dscp: Optional[int] = None,
        ip_ecn: Optional[int] = None,
        ip_traffic_class: Optional[int] = None,
        # *args,
        **kwargs,
    ) -> None:
        """Create a video flow.

        :param source: Sending endpoint of the data traffic
        :type source: Port
        :param destination: Receiving endpoint of the data traffic
        :type destination: Port
        :param name:  Name of this Flow, defaults to auto-generated name
           when set to ``None``.
        :type name: Optional[str], optional
        :param segment_size: size of video segment, defaults to 2*1000*1000
        :type segment_size: int, optional
        :param segment_duration: duration of video segment,
           defaults to timedelta(seconds=2.500)
        :type segment_duration: Union[timedelta, float], optional
        :param buffering_goal: _description_, defaults to timedelta(seconds=60)
        :type buffering_goal: Union[timedelta, float], optional
        :param play_goal: _description_, defaults to timedelta(seconds=5)
        :type play_goal: Union[timedelta, float], optional
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
        :raises FeatureNotSupported: When video flow is using ByteBlower
           Endpoint
        :raises ValueError: When an invalid value for ``segment_duration``
           is used
        :raises ValueError: When an invalid value for ``buffering_goal``
           is used
        :raises ValueError: When an invalid value for ``play_goal``
           is used
        """

        if isinstance(source, Endpoint) or isinstance(destination, Endpoint):
            raise FeatureNotSupported(
                "VideoFlow does not support ByteBlower Endpoint yet"
            )
        super().__init__(source, destination, name=name, **kwargs)
        # super().__init__(source, destination, *args, name=name, **kwargs)
        self._segment_size = segment_size
        if isinstance(segment_duration, timedelta):
            # Already timedelta
            self._segment_duration = segment_duration
        elif isinstance(segment_duration, (float, int)):
            # Convert to timedelta
            self._segment_duration = timedelta(seconds=segment_duration)
        else:
            raise ValueError(
                f'Invalid value for segment_duration: {segment_duration!r}'
            )
        if isinstance(buffering_goal, timedelta):
            # Already timedelta
            self._buffering_goal = buffering_goal
        elif isinstance(buffering_goal, (float, int)):
            # Convert to timedelta
            self._buffering_goal = timedelta(seconds=buffering_goal)
        else:
            raise ValueError(
                f'Invalid value for buffering_goal: {buffering_goal!r}'
            )
        if isinstance(play_goal, timedelta):
            # Already timedelta
            pass
        elif isinstance(play_goal, (float, int)):
            # Convert to timedelta
            play_goal = timedelta(seconds=play_goal)
        else:
            raise ValueError(f'Invalid value for play_goal: {play_goal!r}')
        self._ip_traffic_class = get_ip_traffic_class(
            "IP Traffic Class",
            ip_traffic_class=ip_traffic_class,
            ip_dscp=ip_dscp,
            ip_ecn=ip_ecn,
        )
        self._bytes_per_ms = (
            self._segment_size / self._segment_duration.total_seconds() / 1000
        )  # video bitrate expressed in bytes/s
        bitrate = 8000 * self._bytes_per_ms
        logging.info(
            'Video bitrate will be %.03f MBit/s',
            bitrate / 1000000.0,
        )
        buffering_goal_segments = (
            self._buffering_goal.total_seconds() /
            self._segment_duration.total_seconds()
        )

        buffering_goal_bytes = int(
            buffering_goal_segments * self._segment_size
        )
        play_goal_bytes = (
            int(
                play_goal.total_seconds() /
                self._segment_duration.total_seconds()
            ) * self._segment_size
        )
        self._bufferanalyser = BufferAnalyser(
            buffering_goal_bytes, play_goal_bytes
        )
        self.add_analyser(self._bufferanalyser)
        self._last_consume_time: datetime = None

    @property
    def segment_size(self) -> int:
        return self._segment_size

    @property
    def segment_duration(self) -> timedelta:
        return self._segment_duration

    @property
    def buffering_goal(self) -> timedelta:
        return self._buffering_goal

    @property
    def initial_time_to_wait(self) -> timedelta:
        """Return the time to wait before the flow starts."""
        return timedelta()

    @property
    def duration(self) -> timedelta:
        """Returns the duration of the Video flow.

        :raises InfiniteDuration: The video flow always runs forever.
        :returns: duration of the flow.
        :rtype: timedelta
        """
        raise InfiniteDuration()

    def prepare_start(
        self,
        maximum_run_time: Optional[timedelta] = None
    ) -> Iterable['SynchronizedExecutable']:
        bb_tcp_server = self._set_tcp_server(
            server_port=self.source,
            receive_window_scaling=7,
            slow_start_threshold=1000000000,
            caa=TCPCongestionAvoidanceAlgorithm.SACK_WITH_CUBIC,
        )
        if bb_tcp_server is not None:
            # New HTTP server (not re-using existing one)
            # NOTE: Does not support scheduled start!
            bb_tcp_server.Start()
        self._last_consume_time = datetime.now()
        # Set the initial stats:
        self._bufferanalyser.updatestats()

        # NOTE: We initiate the TCPClientController during the prepare_start
        # phase in the video flow because the TCP client is not added yet
        self._set_tcp_client()

        yield from super().prepare_start(maximum_run_time=maximum_run_time)

    def _elapsed_time_ms(self) -> float:
        now = datetime.now()
        difference: timedelta = now - self._last_consume_time
        self._last_consume_time = now
        return difference.total_seconds() * 1000

    def _download_segment(self) -> None:

        # NOTE: this is a helper function for the generator
        # to be able to return the HTTPClient so we can start it immediately
        def start_new_client():
            bb_tcp_client = yield from self._add_client_session(
                client_port=self.destination,
                server_port=self.source,
                request_size=self._segment_size,
                receive_window_scaling=7,
                slow_start_threshold=1000000000,
                caa=TCPCongestionAvoidanceAlgorithm.SACK_WITH_CUBIC,
                ip_traffic_class=self._ip_traffic_class,
            )
            bb_tcp_client.RequestStart()

        for _ in start_new_client():
            pass

    def _segment_download_required(self) -> bool:
        return (
            self._bufferanalyser.size + self._segment_size
            < self._bufferanalyser.size_max
        )

    def process(self) -> None:
        try:
            bb_tcp_client = self._last_client_session()
        except ByteBlowerTestFrameworkException:
            if self._segment_download_required():
                self._download_segment()
        else:
            # Wait maximum 10 milliseconds
            try:
                if bb_tcp_client.WaitUntilFinished(10000000):
                    # Destroy the http client
                    test_tcp_client = self._bb_tcp_clients.pop()
                    assert (
                        test_tcp_client == bb_tcp_client
                    ), 'OOPS, clearing invalid TCP client'
                    self.destination.bb_port.ProtocolHttpClientRemove(
                        bb_tcp_client
                    )
                    self._bufferanalyser.buffer_fill(self._segment_size)

            except DomainError as e:
                logging.error(
                    "No video statistics available. Unexpected error: %s",
                    e.getMessage(),
                )
            except Exception as e:
                logging.error(
                    "No video statistics available. Unexpected error: %s", e
                )

        elapsed_bytes = self._elapsed_time_ms() * self._bytes_per_ms
        self._bufferanalyser.buffer_consume(elapsed_bytes)

        super().process()

    def updatestats(self) -> None:
        return super().updatestats()

    def analyse(self) -> None:
        """Pass or fail for this test."""
        self.updatestats()

        return super().analyse()

    def release(self) -> None:
        super().release()
        super()._release()
