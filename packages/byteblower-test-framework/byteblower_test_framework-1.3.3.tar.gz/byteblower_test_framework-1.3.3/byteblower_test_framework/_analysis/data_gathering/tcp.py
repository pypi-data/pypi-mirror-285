import logging
from typing import (  # for type hinting
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
    cast,
)

from byteblowerll.byteblower import DataRate  # for type hinting
from byteblowerll.byteblower import HTTPClient  # for type hinting
from byteblowerll.byteblower import HTTPRequestMethod  # for type hinting
from byteblowerll.byteblower import HTTPResultData  # for type hinting
from byteblowerll.byteblower import HTTPResultHistory  # for type hinting
from byteblowerll.byteblower import HTTPServer  # for type hinting
from byteblowerll.byteblower import HTTPSessionInfo  # for type hinting
from byteblowerll.byteblower import TCPResultData  # for type hinting
from byteblowerll.byteblower import TCPResultHistory  # for type hinting
from byteblowerll.byteblower import TCPSessionInfo  # for type hinting
from byteblowerll.byteblower import (
    ByteBlowerAPIException,
    ConfigError,
    HTTPClientMobile,
)
from pandas import DataFrame  # for type hinting
from pandas import Timestamp  # for type hinting
from pandas import Int64Dtype, to_datetime

from ..storage.tcp import HttpData  # for type hinting
from ..storage.tcp import L4SHttpData  # for type hinting
from ..storage.tcp import (
    HTTP_DATA_INTERVAL_DURATION,
    HTTP_DATA_RX_BYTES,
    HTTP_DATA_TX_BYTES,
    LOCAL_ECN_MARKINGS,
    REMOTE_ECN_MARKINGS,
    TCP_DATA_FAST_RETRANSMISSIONS,
    TCP_DATA_INTERVAL_DURATION,
    TCP_DATA_RX_TOTAL_BYTES,
    TCP_DATA_SLOW_RETRANSMISSIONS,
    TCP_DATA_TX_TOTAL_BYTES,
)
from .data_gatherer import DataGatherer

_LOGGER = logging.getLogger(__name__)


class HttpDataGatherer(DataGatherer):

    __slots__ = (
        '_http_data',
        '_bb_tcp_clients',
        '_bb_tcp_server',
        '_client_index',
    )

    def __init__(
        self,
        http_data: HttpData,
        bb_tcp_clients: Union[List[HTTPClient], List[HTTPClientMobile]],
    ) -> None:
        super().__init__()
        self._http_data = http_data
        self._bb_tcp_clients = bb_tcp_clients
        self._bb_tcp_server: Optional[HTTPServer] = None

        self._client_index = 0

    def set_http_server(self, bb_tcp_server: HTTPServer) -> None:
        self._bb_tcp_server = bb_tcp_server

    def updatestats(self) -> None:
        """
        Analyse the result.

        .. warning::
           What would be bad?

           - TCP sessions not going to ``Finished`` state.
        """
        # Let's analyse the result
        self._update_history_snapshots()

    def summarize(self) -> None:
        """
        Store the final results.

        Stores the average data speed over the complete session.

        .. warning::
           This summary does not support multiple clients yet.
           It is only created for the last client.
        """
        # NOTE: Could still end up as None
        #       when no client started at all!
        http_method = None

        # Set HTTP data transfer results
        # ! FIXME - Take average over multiple clients
        http_avg_goodput = None

        # Set HTTP client results
        http_avg_goodput_client = None
        mobile_client = None
        total_rx_client = 0
        total_tx_client = 0
        rx_first_client = None
        rx_last_client = None
        tx_first_client = None
        tx_last_client = None

        # Set HTTP server results
        http_avg_goodput_server = None
        total_rx_server = 0
        total_tx_server = 0
        rx_first_server = None
        rx_last_server = None
        tx_first_server = None
        tx_last_server = None

        # Sanity checks
        if len(self._bb_tcp_clients) > 1:
            _LOGGER.warning(
                'HttpAnalyser summary only supports one client for now.'
                ' The test used %d clients.', len(self._bb_tcp_clients)
            )

        # Add remaining history snapshots
        # ! FIXME: Avoid multiple HTTPResultHistory.Refresh() calls
        self._update_history_snapshots()

        # Take only the last client (if one available)
        for client in self._bb_tcp_clients[-1:]:
            mobile_client = isinstance(client, HTTPClientMobile)
            server_client_id = client.ServerClientIdGet()
            http_method = cast(HTTPRequestMethod, client.HttpMethodGet())
            try:
                # Get TCP/HTTP Session Info
                http_session_info_client = cast(
                    HTTPSessionInfo, client.HttpSessionInfoGet()
                )

                # NOTE: We MUST refresh the result history *again*
                #       to be able to get the latest result snapshot.
                #     * It was cleared in `self._update_history_snapshots()` !
                http_session_info_client.Refresh()

                # Get latest HTTP results
                http_result_history_client = cast(
                    HTTPResultHistory, client.ResultHistoryGet()
                )
                (
                    http_avg_goodput_client,
                    total_rx_client,
                    total_tx_client,
                    rx_first_client,
                    rx_last_client,
                    tx_first_client,
                    tx_last_client,
                ) = self._get_http_summary_data(
                    f'HTTP Client {server_client_id!r}',
                    http_result_history_client,
                    self._http_data.df_http_client,
                    True,
                )

                # Get latest TCP results
                try:
                    tcp_session_info_client = cast(
                        TCPSessionInfo,
                        http_session_info_client.TcpSessionInfoGet()
                    )
                except ConfigError as error:
                    _LOGGER.debug(
                        "Couldn't get TCP Client %r result history"
                        " in HttpAnalyser summary: %s."
                        " Running on an Endpoint?",
                        server_client_id,
                        error.getMessage(),
                    )
                else:
                    self._get_tcp_summary_date(
                        f'HTTP Client {server_client_id!r}',
                        tcp_session_info_client,
                        self._http_data.df_tcp_client,
                    )
            except ByteBlowerAPIException as error:
                _LOGGER.warning(
                    "Couldn't get HTTP Client %r result history"
                    " in HttpAnalyser summary: %s",
                    server_client_id,
                    error.getMessage(),
                )

            try:
                # Get TCP/HTTP Session Info
                http_session_info_server = cast(
                    HTTPSessionInfo,
                    self._bb_tcp_server.HttpSessionInfoGet(server_client_id)
                )
                tcp_session_info_server = cast(
                    TCPSessionInfo,
                    http_session_info_server.TcpSessionInfoGet()
                )

                # NOTE: We MUST refresh the result history *again*
                #       to be able to get the latest result snapshot.
                #     * It was cleared in `self._update_history_snapshots()` !
                http_session_info_server.Refresh()

                # Get latest TCP results
                self._get_tcp_summary_date(
                    f'HTTP Server for Client {server_client_id!r}',
                    tcp_session_info_server,
                    self._http_data.df_tcp_server,
                )

                # Get latest HTTP results
                http_result_history_server = cast(
                    HTTPResultHistory,
                    http_session_info_server.ResultHistoryGet()
                )
            except ByteBlowerAPIException as error:
                _LOGGER.warning(
                    "Couldn't get HTTP Server for Client %r"
                    " result history in HttpAnalyser summary: %s",
                    server_client_id,
                    error.getMessage(),
                )
                # No further processing
                continue
            (
                http_avg_goodput_server,
                total_rx_server,
                total_tx_server,
                rx_first_server,
                rx_last_server,
                tx_first_server,
                tx_last_server,
            ) = self._get_http_summary_data(
                f'HTTP Server for Client {server_client_id!r}',
                http_result_history_server,
                self._http_data.df_http_server,
                http_avg_goodput_client is None,
            )

        http_avg_goodput = (
            http_avg_goodput_client
            if http_avg_goodput_client is not None else http_avg_goodput_server
        )

        if http_method == HTTPRequestMethod.Get:
            http_method_string = "GET"
        elif http_method == HTTPRequestMethod.Put:
            http_method_string = "PUT"
        else:
            _LOGGER.warning(
                'HttpDataGatherer: Unsupported HTTP Method (%s).'
                ' Storing original value.', http_method
            )
            http_method_string = str(http_method)

        # Store the HTTP Method string
        self._http_data._http_method = http_method_string

        # Set TCP client results
        # Make sure we store the count and duration (in nanoseconds) as Int64:
        self._http_data._df_tcp_client = (
            self._http_data._df_tcp_client.astype(
                {
                    TCP_DATA_INTERVAL_DURATION: Int64Dtype(),
                    TCP_DATA_TX_TOTAL_BYTES: Int64Dtype(),
                    TCP_DATA_RX_TOTAL_BYTES: Int64Dtype(),
                    # 'AVG dataspeed': Float64Dtype(),
                    TCP_DATA_SLOW_RETRANSMISSIONS: Int64Dtype(),
                    TCP_DATA_FAST_RETRANSMISSIONS: Int64Dtype(),
                }
            )
        )

        # Set TCP server results
        # Make sure we store the count and duration (in nanoseconds) as Int64:
        self._http_data._df_tcp_server = (
            self._http_data._df_tcp_server.astype(
                {
                    TCP_DATA_INTERVAL_DURATION: Int64Dtype(),
                    TCP_DATA_TX_TOTAL_BYTES: Int64Dtype(),
                    TCP_DATA_RX_TOTAL_BYTES: Int64Dtype(),
                    # 'AVG dataspeed': Float64Dtype(),
                    TCP_DATA_SLOW_RETRANSMISSIONS: Int64Dtype(),
                    TCP_DATA_FAST_RETRANSMISSIONS: Int64Dtype(),
                }
            )
        )

        # Set HTTP data traffic results
        self._http_data._http_avg_goodput = http_avg_goodput

        # Set client results
        self._http_data._mobile_client = mobile_client
        self._http_data._total_rx_client = total_rx_client
        self._http_data._total_tx_client = total_tx_client
        self._http_data._ts_rx_first_client = rx_first_client
        self._http_data._ts_rx_last_client = rx_last_client
        self._http_data._ts_tx_first_client = tx_first_client
        self._http_data._ts_tx_last_client = tx_last_client
        # Make sure we store the count and duration (in nanoseconds) as Int64:
        self._http_data._df_http_client = (
            self._http_data._df_http_client.astype(
                {
                    HTTP_DATA_INTERVAL_DURATION: Int64Dtype(),
                    HTTP_DATA_TX_BYTES: Int64Dtype(),
                    HTTP_DATA_RX_BYTES: Int64Dtype(),
                    # 'AVG dataspeed': Float64Dtype(),
                }
            )
        )

        # Set HTTP server results
        self._http_data._total_rx_server = total_rx_server
        self._http_data._total_tx_server = total_tx_server
        self._http_data._ts_rx_first_server = rx_first_server
        self._http_data._ts_rx_last_server = rx_last_server
        self._http_data._ts_tx_first_server = tx_first_server
        self._http_data._ts_tx_last_server = tx_last_server
        # Make sure we store the count and duration (in nanoseconds) as Int64:
        self._http_data._df_http_server = (
            self._http_data._df_http_server.astype(
                {
                    HTTP_DATA_INTERVAL_DURATION: Int64Dtype(),
                    HTTP_DATA_TX_BYTES: Int64Dtype(),
                    HTTP_DATA_RX_BYTES: Int64Dtype(),
                    # 'AVG dataspeed': Float64Dtype(),
                }
            )
        )

    def release(self) -> None:
        super().release()
        # NOTE: HTTP Server and Clients will be released from the TcpFlow.
        try:
            del self._bb_tcp_clients
        except AttributeError:
            _LOGGER.warning(
                'HttpDataGatherer: TCP clients already destroyed?',
                exc_info=True
            )
        try:
            del self._bb_tcp_server
        except AttributeError:
            _LOGGER.warning(
                'HttpDataGatherer: TCP server already destroyed?',
                exc_info=True
            )

    def _get_tcp_summary_date(
        self,
        _name: str,
        tcp_session_info: TCPSessionInfo,
        over_time_results: DataFrame,
    ):
        tcp_result_history: TCPResultHistory = (
            tcp_session_info.ResultHistoryGet()
        )
        tcp_results: TCPResultData = tcp_result_history.CumulativeLatestGet()
        # Persist TCP latest/final snapshot
        timestamp_ns: int = tcp_results.TimestampGet()
        tcp_interval_snapshot: TCPResultData = (
            tcp_result_history.IntervalGetByTime(timestamp_ns)
        )
        timestamp = to_datetime(timestamp_ns, unit='ns', utc=True)
        self._persist_tcp_history_snapshot(
            _name, timestamp, tcp_interval_snapshot, over_time_results
        )

    def _get_http_summary_data(
        self, _name: str, result_history: HTTPResultHistory,
        over_time_results: DataFrame, need_http_avg_goodput: bool
    ) -> Tuple[
            Optional[float],
            Optional[int],
            Optional[int],
            Optional[Timestamp],
            Optional[Timestamp],
            Optional[Timestamp],
            Optional[Timestamp],
    ]:
        http_avg_goodput = None
        # Set HTTP results
        total_rx = 0
        total_tx = 0
        rx_first = None
        rx_last = None
        tx_first = None
        tx_last = None

        if result_history.CumulativeLengthGet() > 0:
            http_result_data: HTTPResultData = (
                result_history.CumulativeLatestGet()
            )
            try:
                total_rx: int = http_result_data.RxByteCountTotalGet()
                total_tx: int = http_result_data.TxByteCountTotalGet()
                rx_first = to_datetime(
                    cast(int, http_result_data.RxTimestampFirstGet()),
                    unit='ns',
                    utc=True,
                )
                rx_last = to_datetime(
                    cast(int, http_result_data.RxTimestampLastGet()),
                    unit='ns',
                    utc=True,
                )
                tx_first = to_datetime(
                    cast(int, http_result_data.TxTimestampFirstGet()),
                    unit='ns',
                    utc=True,
                )
                tx_last = to_datetime(
                    cast(int, http_result_data.TxTimestampLastGet()),
                    unit='ns',
                    utc=True,
                )

                if need_http_avg_goodput:
                    average_data_speed: DataRate = (
                        http_result_data.AverageDataSpeedGet()
                    )
                    http_avg_goodput: float = average_data_speed.ByteRateGet()

                # Persist latest/final snapshot
                timestamp_ns: int = http_result_data.TimestampGet()
                interval_snapshot: HTTPResultData = (
                    result_history.IntervalGetByTime(timestamp_ns)
                )
                timestamp = to_datetime(timestamp_ns, unit='ns', utc=True)
                self._persist_http_history_snapshot(
                    _name, timestamp, interval_snapshot, over_time_results
                )
            except ByteBlowerAPIException as error:
                _LOGGER.warning(
                    "Couldn't get %r results in HttpAnalyser: %s",
                    _name,
                    error.getMessage(),
                    exc_info=True,
                )
        else:
            _LOGGER.info("HttpAnalyser: No final %r results", _name)

        return (
            http_avg_goodput,
            total_rx,
            total_tx,
            rx_first,
            rx_last,
            tx_first,
            tx_last,
        )

    def _update_history_snapshots(self) -> None:
        """Add all the history interval results."""
        # NOTE - Not analysing results for finished HTTP clients
        #        in a previous iteration of "update stats":
        for client in self._bb_tcp_clients[self._client_index:]:
            self._update_client_history_snapshots(client)

            self._update_server_history_snapshots(client)

        # NOTE - Don't analyse results for finished HTTP clients
        #        in a next iteration of updatestats:
        self._client_index = len(self._bb_tcp_clients)
        if self._client_index > 0:
            # ! FIXME - Shouldn't we check if HTTP client actually finished?
            self._client_index -= 1

    def _update_client_history_snapshots(
        self, client: Union[HTTPClient, HTTPClientMobile]
    ) -> None:
        """Add all the history interval results."""
        server_client_id = client.ServerClientIdGet()
        try:
            # Get TCP/HTTP Session Info
            http_session_info: HTTPSessionInfo = client.HttpSessionInfoGet()

            # Update history snapshots
            self._update_http_history_snapshots(
                f'HTTP Client {server_client_id!r}',
                http_session_info,
                self._http_data.df_tcp_client,
                self._http_data.df_http_client,
            )
        except ByteBlowerAPIException as error:
            # "Session is not available" can happen when
            # the client request was not sent (yet)
            if 'Session is not available' not in error.getMessage():
                _LOGGER.warning(
                    "Couldn't get HTTP Client %r result in HttpAnalyser: %s",
                    server_client_id,
                    error.getMessage(),
                )

    def _update_server_history_snapshots(
        self, client: Union[HTTPClient, HTTPClientMobile]
    ) -> None:
        server_client_id = client.ServerClientIdGet()
        try:
            # Get TCP/HTTP Session Info
            http_session_info: HTTPSessionInfo = (
                self._bb_tcp_server.HttpSessionInfoGet(server_client_id)
            )

            # Update history snapshots
            self._update_http_history_snapshots(
                f'HTTP Server for Client {server_client_id!r}',
                http_session_info,
                self._http_data.df_tcp_server,
                self._http_data.df_http_server,
            )
        except ByteBlowerAPIException as error:
            # "Session is not available" can happen when
            # the client request was not received (yet)
            if 'Session is not available' not in error.getMessage():
                _LOGGER.warning(
                    "Couldn't get HTTP Server for Client %r result"
                    " in HttpAnalyser: %s",
                    server_client_id,
                    error.getMessage(),
                )

    def _update_http_history_snapshots(
        self, _name: str, http_session_info: HTTPSessionInfo,
        tcp_over_time_results: DataFrame, http_over_time_results: DataFrame
    ) -> None:
        # Refresh the result history
        http_session_info.Refresh()

        self._persist_history_snapshots(
            _name, http_session_info, tcp_over_time_results,
            http_over_time_results
        )

        # Clear the result history
        cast(HTTPResultHistory, http_session_info.ResultHistoryGet()).Clear()
        try:
            tcp_session_info = cast(
                TCPSessionInfo, http_session_info.TcpSessionInfoGet()
            )
        except ConfigError as error:
            _LOGGER.debug(
                "%s: Couldn't clear TCP session info: %s."
                " Running on an Endpoint?",
                _name,
                error.getMessage(),
            )
        else:
            cast(TCPResultHistory, tcp_session_info.ResultHistoryGet()).Clear()

    def _persist_history_snapshots(
        self, _name: str, http_session_info: HTTPSessionInfo,
        tcp_over_time_results: DataFrame, http_over_time_results: DataFrame
    ) -> None:
        # Get result history
        http_result_history = cast(
            HTTPResultHistory, http_session_info.ResultHistoryGet()
        )

        self._persist_http_history_snapshots(
            _name, http_result_history, http_over_time_results
        )

        try:
            tcp_session_info = cast(
                TCPSessionInfo, http_session_info.TcpSessionInfoGet()
            )
        except ConfigError as error:
            _LOGGER.debug(
                "%s: Couldn't get TCP session info: %s."
                " Running on an Endpoint?",
                _name,
                error.getMessage(),
            )
        else:
            tcp_result_history = cast(
                TCPResultHistory, tcp_session_info.ResultHistoryGet()
            )

            self._persist_tcp_history_snapshots(
                _name, tcp_result_history, tcp_over_time_results
            )

    def _persist_tcp_history_snapshots(
        self, _name: str, result_history: TCPResultHistory,
        over_time_results: DataFrame
    ) -> None:
        # Cfr. TCPResultDataList
        interval_snapshots: Sequence[TCPResultData] = (
            result_history.IntervalGet()
        )

        for interval_snapshot in interval_snapshots[:-1]:
            timestamp_ns: int = interval_snapshot.TimestampGet()
            timestamp = to_datetime(timestamp_ns, unit='ns', utc=True)
            self._persist_tcp_history_snapshot(
                _name, timestamp, interval_snapshot, over_time_results
            )

    def _persist_http_history_snapshots(
        self, _name: str, result_history: HTTPResultHistory,
        over_time_results: DataFrame
    ) -> None:
        # Cfr. byteblowerll.byteblower.HTTPResultDataList
        interval_snapshots: Sequence[HTTPResultData] = (
            result_history.IntervalGet()
        )
        for interval_snapshot in interval_snapshots[:-1]:
            timestamp_ns: int = interval_snapshot.TimestampGet()
            timestamp = to_datetime(timestamp_ns, unit='ns', utc=True)
            self._persist_http_history_snapshot(
                _name, timestamp, interval_snapshot, over_time_results
            )

    def _persist_tcp_history_snapshot(
        self, _name: str, timestamp: Timestamp,
        interval_snapshot: TCPResultData, over_time_results: DataFrame
    ) -> None:
        interval_duration = interval_snapshot.IntervalDurationGet()
        interval_rx_bytes = interval_snapshot.RxByteCountTotalGet()
        interval_tx_bytes = interval_snapshot.TxByteCountTotalGet()
        minimum_rtt = interval_snapshot.RoundTripTimeMinimumGet()
        maximum_rtt = interval_snapshot.RoundTripTimeMaximumGet()
        average_rtt = interval_snapshot.RoundTripTimeAverageGet()
        slow_retransmission_count = (
            interval_snapshot.RetransmissionCountSlowGet()
        )
        fast_retransmission_count = (
            interval_snapshot.RetransmissionCountFastGet()
        )
        try:
            existing_snapshot = over_time_results.loc[timestamp]
        except KeyError:
            over_time_results.loc[timestamp] = (
                interval_duration,
                interval_tx_bytes,
                interval_rx_bytes,
                minimum_rtt,
                maximum_rtt,
                average_rtt,
                slow_retransmission_count,
                fast_retransmission_count,
            )
        else:
            _LOGGER.warning(
                '%s: Found existing TCP snapshot @ %r',
                _name,
                timestamp,
            )
            existing_duration = existing_snapshot[TCP_DATA_INTERVAL_DURATION]
            if existing_duration != interval_duration:
                _LOGGER.warning(
                    '%s: Found existing TCP snapshot'
                    ' with different duration (%r <> %r)',
                    _name,
                    existing_duration,
                    interval_duration,
                )
            existing_snapshot[TCP_DATA_TX_TOTAL_BYTES] += interval_tx_bytes
            existing_snapshot[TCP_DATA_RX_TOTAL_BYTES] += interval_rx_bytes

    def _persist_http_history_snapshot(
        self, _name: str, timestamp: Timestamp,
        interval_snapshot: HTTPResultData, over_time_results: DataFrame
    ) -> None:
        interval_duration = interval_snapshot.IntervalDurationGet()
        interval_rx_bytes = interval_snapshot.RxByteCountTotalGet()
        interval_tx_bytes = interval_snapshot.TxByteCountTotalGet()
        try:
            existing_snapshot = over_time_results.loc[timestamp]
        except KeyError:
            over_time_results.loc[timestamp] = (
                interval_duration,
                interval_tx_bytes,
                interval_rx_bytes,
            )
        else:
            _LOGGER.warning(
                '%s: Found existing HTTP snapshot @ %r',
                _name,
                timestamp,
            )
            existing_duration = existing_snapshot[HTTP_DATA_INTERVAL_DURATION]
            if existing_duration != interval_duration:
                _LOGGER.warning(
                    '%s: Found existing HTTP snapshot'
                    ' with different duration (%r <> %r)',
                    _name,
                    existing_duration,
                    interval_duration,
                )
            existing_snapshot[HTTP_DATA_TX_BYTES] += interval_tx_bytes
            existing_snapshot[HTTP_DATA_RX_BYTES] += interval_rx_bytes


class L4SHttpDataGatherer(HttpDataGatherer):
    """Collection of L4S-enabled HTTP flow metrics over time."""
    __slots__ = ()

    def __init__(
        self, http_data: L4SHttpData, bb_tcp_clients: List[HTTPClient]
    ) -> None:
        super().__init__(http_data, bb_tcp_clients)

    def _persist_tcp_history_snapshot(
        self, _name: str, timestamp: Timestamp,
        interval_snapshot: TCPResultData, over_time_results: DataFrame
    ) -> None:
        interval_duration = interval_snapshot.IntervalDurationGet()
        interval_rx_bytes = interval_snapshot.RxByteCountTotalGet()
        interval_tx_bytes = interval_snapshot.TxByteCountTotalGet()
        minimum_rtt = interval_snapshot.RoundTripTimeMinimumGet()
        maximum_rtt = interval_snapshot.RoundTripTimeMaximumGet()
        average_rtt = interval_snapshot.RoundTripTimeAverageGet()
        slow_retransmission_count = (
            interval_snapshot.RetransmissionCountSlowGet()
        )
        fast_retransmission_count = (
            interval_snapshot.RetransmissionCountFastGet()
        )

        local_ecn_markings = (
            interval_snapshot.RxLocalCongestionNotificationCountGet()
        )
        remote_ecn_markings = (
            interval_snapshot.RxRemoteCongestionNotificationCountGet()
        )

        try:
            existing_snapshot = over_time_results.loc[timestamp]
        except KeyError:
            over_time_results.loc[timestamp] = (
                interval_duration,
                interval_tx_bytes,
                interval_rx_bytes,
                minimum_rtt,
                maximum_rtt,
                average_rtt,
                slow_retransmission_count,
                fast_retransmission_count,
                local_ecn_markings,
                remote_ecn_markings,
            )
        else:
            _LOGGER.warning(
                '%s: Found existing TCP snapshot @ %r',
                _name,
                timestamp,
            )
            existing_duration = existing_snapshot[TCP_DATA_INTERVAL_DURATION]
            if existing_duration != interval_duration:
                _LOGGER.warning(
                    '%s: Found existing TCP snapshot'
                    ' with different duration (%r <> %r)',
                    _name,
                    existing_duration,
                    interval_duration,
                )
            existing_snapshot[TCP_DATA_TX_TOTAL_BYTES] += interval_tx_bytes
            existing_snapshot[TCP_DATA_RX_TOTAL_BYTES] += interval_rx_bytes
            existing_snapshot[TCP_DATA_SLOW_RETRANSMISSIONS
                              ] += slow_retransmission_count
            existing_snapshot[TCP_DATA_FAST_RETRANSMISSIONS
                              ] += fast_retransmission_count
            existing_snapshot[LOCAL_ECN_MARKINGS] += local_ecn_markings
            existing_snapshot[REMOTE_ECN_MARKINGS] += remote_ecn_markings
