from typing import Optional  # for type hinting

from pandas import DataFrame, Timestamp  # for type hinting

from ..helpers import MEGA, to_bitrate
from ..storage.tcp import HttpData  # for type hinting
from ..storage.tcp import L4SHttpData  # for type hinting
from .data_analyser import DataAnalyser


class HttpDataAnalyser(DataAnalyser):
    """
    Data Analysis for HTTP Flow.

    Currently, data analysis is not yet implemented.
    """

    __slots__ = ('_http_data',)

    def __init__(self, http_data: HttpData) -> None:
        super().__init__()
        self._http_data = http_data

    def analyse(self) -> None:
        """
        .. note::
           Currently, no pass/fail criteria.
        """
        # Get the data
        http_avg_goodput = self._http_data.http_avg_goodput

        if http_avg_goodput is not None:
            http_avg_goodput = to_bitrate(
                http_avg_goodput, scaling_factor=MEGA
            )

        self._set_log(
            f'Average HTTP goodput: {(http_avg_goodput or 0):0.3f} Mbits/s'
        )
        # Actually nothing is analysed here
        # self._set_result(True)

    @property
    def http_method(self):
        """Return the configured HTTP Request Method."""
        return self._http_data.http_method

    @property
    def mobile_client(self):
        """Whether a mobile HTTP Client was used."""
        return self._http_data.mobile_client

    @property
    def df_tcp_client(self) -> DataFrame:
        """Return TCP statistics on Client side."""
        return self._http_data.df_tcp_client

    @property
    def df_tcp_server(self) -> DataFrame:
        """Return TCP statistics on Server side."""
        return self._http_data.df_tcp_server

    @property
    def df_http_client(self) -> DataFrame:
        """Return HTTP statistics on Client side."""
        return self._http_data.df_http_client

    @property
    def df_http_server(self) -> DataFrame:
        """Return HTTP statistics on the Server side."""
        return self._http_data.df_http_server

    @property
    def total_rx_client(self) -> int:
        """Number of received bytes at HTTP Client."""
        return self._http_data.total_rx_client

    @property
    def total_tx_client(self) -> int:
        """Number of transmitted bytes at HTTP Client."""
        return self._http_data.total_tx_client

    @property
    def total_rx_server(self) -> int:
        """Number of received bytes at HTTP Server."""
        return self._http_data.total_rx_server

    @property
    def total_tx_server(self) -> int:
        """Number of transmitted bytes at HTTP Server."""
        return self._http_data.total_tx_server

    @property
    def rx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Client."""
        return self._http_data.ts_rx_first_client

    @property
    def rx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Client."""
        return self._http_data.ts_rx_last_client

    @property
    def tx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Client."""
        return self._http_data.ts_tx_first_client

    @property
    def tx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Client."""
        return self._http_data.ts_tx_last_client

    @property
    def rx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Server."""
        return self._http_data.ts_rx_first_server

    @property
    def rx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Server."""
        return self._http_data.ts_rx_last_server

    @property
    def tx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Server."""
        return self._http_data.ts_tx_first_server

    @property
    def tx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Server."""
        return self._http_data.ts_tx_last_server


class L4SHttpDataAnalyser(HttpDataAnalyser):
    """
    Data Analysis for L4S-enabled HTTP Flow.

    Currently, data analysis is not yet implemented.
    """

    def __init__(self, l4s_http_data: L4SHttpData) -> None:
        super().__init__(l4s_http_data)
