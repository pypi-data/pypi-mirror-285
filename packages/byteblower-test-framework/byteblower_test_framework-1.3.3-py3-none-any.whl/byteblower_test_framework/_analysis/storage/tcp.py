"""Data storage for TCP flow related information."""
from typing import TYPE_CHECKING, List, Optional, Tuple  # for type hinting

import pandas
from byteblowerll.byteblower import HTTPRequestStatus  # for type hinting
from byteblowerll.byteblower import HTTPServerStatus  # for type hinting
from pandas import Timestamp  # for type hinting

from .data_store import DataStore

if TYPE_CHECKING:
    # NOTE: Used in documentation only
    from ..._traffic.tcpflow import TcpFlow

__all__ = (
    'TcpStatusData',
    'HttpData',
)

# See
# https://api.byteblower.com/json/byteblower_json_documentation.html#httpFlows_items_tcpClient_overTimeResults_items_txTotal
TCP_DATA_INTERVAL_DURATION = 'duration'
TCP_DATA_TX_TOTAL_BYTES = 'txTotal'
TCP_DATA_RX_TOTAL_BYTES = 'rxTotal'
TCP_DATA_MINIMUM_RTT = 'rttMinimum'
TCP_DATA_MAXIMUM_RTT = 'rttMaximum'
TCP_DATA_AVERAGE_RTT = 'rttAverage'
TCP_DATA_SLOW_RETRANSMISSIONS = 'slowRetransmissions'
TCP_DATA_FAST_RETRANSMISSIONS = 'fastRetransmissions'

# See
# https://api.byteblower.com/json/byteblower_json_documentation.html#httpFlows_items_httpServer_overTimeResults_items_txBytes
HTTP_DATA_INTERVAL_DURATION = 'duration'
HTTP_DATA_TX_BYTES = 'TX Bytes'
HTTP_DATA_RX_BYTES = 'RX Bytes'

REMOTE_ECN_MARKINGS = 'remoteECNMarkings'
LOCAL_ECN_MARKINGS = 'localECNMarkings'


class TcpStatusData(DataStore):
    """Status data from a :class:`TcpFlow`."""

    __slots__ = (
        '_server_status',
        '_client_status',
    )

    def __init__(self) -> None:
        """Create TcpFlow status data container."""
        super().__init__()
        self._server_status: Optional[HTTPServerStatus] = None
        self._client_status: List[Tuple[HTTPRequestStatus, str]] = []

    def server_status(self) -> Optional[HTTPServerStatus]:
        """Return the final TCP server status.

        :return: Final TCP server status
        :rtype: Optional[HTTPServerStatus]
        """
        return self._server_status

    def client_status(self) -> List[Tuple[HTTPRequestStatus, str]]:
        """Return the final status of all TCP clients.

        :return: Final status of all TCP clients.
        :rtype: List[Tuple[HTTPRequestStatus, str]]
        """
        return self._client_status


class HttpData(DataStore):

    __slots__ = (
        '_http_method',
        '_df_tcp_client',
        '_df_http_client',
        '_df_tcp_server',
        '_df_http_server',
        '_http_avg_goodput',
        '_mobile_client',
        '_total_rx_client',
        '_total_tx_client',
        '_total_rx_server',
        '_total_tx_server',
        '_ts_rx_first_client',
        '_ts_rx_last_client',
        '_ts_tx_first_client',
        '_ts_tx_last_client',
        '_ts_rx_first_server',
        '_ts_rx_last_server',
        '_ts_tx_first_server',
        '_ts_tx_last_server',
    )

    def __init__(self) -> None:
        self._df_tcp_client = pandas.DataFrame(
            columns=[
                TCP_DATA_INTERVAL_DURATION,
                TCP_DATA_TX_TOTAL_BYTES,
                TCP_DATA_RX_TOTAL_BYTES,
                # 'AVG dataspeed',  # TODO: not available: Calculate it !?
                TCP_DATA_MINIMUM_RTT,
                TCP_DATA_MAXIMUM_RTT,
                TCP_DATA_AVERAGE_RTT,
                TCP_DATA_SLOW_RETRANSMISSIONS,
                TCP_DATA_FAST_RETRANSMISSIONS,
            ]
        )
        self._df_http_client = pandas.DataFrame(
            columns=[
                HTTP_DATA_INTERVAL_DURATION,
                HTTP_DATA_TX_BYTES,
                HTTP_DATA_RX_BYTES,
                # 'AVG dataspeed',
            ]
        )

        self._df_tcp_server = pandas.DataFrame(
            columns=[
                TCP_DATA_INTERVAL_DURATION,
                TCP_DATA_TX_TOTAL_BYTES,
                TCP_DATA_RX_TOTAL_BYTES,
                # 'AVG dataspeed',  # TODO: not available: Calculate it !?
                TCP_DATA_MINIMUM_RTT,
                TCP_DATA_MAXIMUM_RTT,
                TCP_DATA_AVERAGE_RTT,
                TCP_DATA_SLOW_RETRANSMISSIONS,
                TCP_DATA_FAST_RETRANSMISSIONS,
            ]
        )
        self._df_http_server = pandas.DataFrame(
            columns=[
                HTTP_DATA_INTERVAL_DURATION,
                HTTP_DATA_TX_BYTES,
                HTTP_DATA_RX_BYTES,
                # 'AVG dataspeed',
            ]
        )

        self._http_method: Optional[str] = None

        self._http_avg_goodput: Optional[float] = None
        self._mobile_client: Optional[bool] = None
        self._total_rx_client: int = 0
        self._total_tx_client: int = 0
        self._total_rx_server: int = 0
        self._total_tx_server: int = 0
        self._ts_rx_first_client: Optional[Timestamp] = None
        self._ts_rx_last_client: Optional[Timestamp] = None
        self._ts_tx_first_client: Optional[Timestamp] = None
        self._ts_tx_last_client: Optional[Timestamp] = None

        self._ts_rx_first_server: Optional[Timestamp] = None
        self._ts_rx_last_server: Optional[Timestamp] = None
        self._ts_tx_first_server: Optional[Timestamp] = None
        self._ts_tx_last_server: Optional[Timestamp] = None

    @property
    def http_method(self) -> str:
        """Return the configured HTTP Request Method."""
        return self._http_method

    @property
    def df_tcp_client(self) -> pandas.DataFrame:
        """TCP client results over time."""
        return self._df_tcp_client

    @property
    def df_tcp_server(self) -> pandas.DataFrame:
        """TCP server results over time."""
        return self._df_tcp_server

    @property
    def df_http_client(self) -> pandas.DataFrame:
        """HTTP client results over time."""
        return self._df_http_client

    @property
    def df_http_server(self) -> pandas.DataFrame:
        """HTTP server results over time."""
        return self._df_http_server

    @property
    def http_avg_goodput(self) -> Optional[float]:
        """Average HTTP goodput in Bytes per second."""
        return self._http_avg_goodput

    @property
    def mobile_client(self) -> Optional[bool]:
        """Whether a mobile HTTP Client was used."""
        return self._mobile_client

    @property
    def total_rx_client(self) -> int:
        """Number of received bytes at HTTP Client."""
        return self._total_rx_client

    @property
    def total_tx_client(self) -> int:
        """Number of transmitted bytes at HTTP Client."""
        return self._total_tx_client

    @property
    def total_rx_server(self) -> int:
        """Number of received bytes at HTTP Server."""
        return self._total_rx_server

    @property
    def total_tx_server(self) -> int:
        """Number of transmitted bytes at HTTP Server."""
        return self._total_tx_server

    @property
    def ts_rx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Client."""
        return self._ts_rx_first_client

    @property
    def ts_rx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Client."""
        return self._ts_rx_last_client

    @property
    def ts_tx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Client."""
        return self._ts_tx_first_client

    @property
    def ts_tx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Client."""
        return self._ts_tx_last_client

    @property
    def ts_rx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Server."""
        return self._ts_rx_first_server

    @property
    def ts_rx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Server."""
        return self._ts_rx_last_server

    @property
    def ts_tx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Server."""
        return self._ts_tx_first_server

    @property
    def ts_tx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Server."""
        return self._ts_tx_last_server


class L4SHttpData(HttpData):
    __slots__ = ()

    def __init__(self) -> None:
        super().__init__()
        self._df_tcp_client[LOCAL_ECN_MARKINGS] = []
        self._df_tcp_client[REMOTE_ECN_MARKINGS] = []
        self._df_tcp_server[LOCAL_ECN_MARKINGS] = []
        self._df_tcp_server[REMOTE_ECN_MARKINGS] = []
