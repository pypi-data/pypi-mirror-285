from typing import Optional  # for type hinting

from pandas import DataFrame  # for type hinting

from ..._traffic.tcpflow import HttpMethod
from ...exceptions import UnsupportedHTTPMethod
from ..data_analysis.tcp import HttpDataAnalyser, L4SHttpDataAnalyser
from ..helpers import to_bitrate
from ..plotting import GenericChart
from ..storage.tcp import (
    HTTP_DATA_INTERVAL_DURATION,
    HTTP_DATA_RX_BYTES,
    HTTP_DATA_TX_BYTES,
    LOCAL_ECN_MARKINGS,
    REMOTE_ECN_MARKINGS,
    TCP_DATA_AVERAGE_RTT,
    TCP_DATA_FAST_RETRANSMISSIONS,
    TCP_DATA_INTERVAL_DURATION,
    TCP_DATA_MAXIMUM_RTT,
    TCP_DATA_MINIMUM_RTT,
    TCP_DATA_RX_TOTAL_BYTES,
    TCP_DATA_SLOW_RETRANSMISSIONS,
    TCP_DATA_TX_TOTAL_BYTES,
)
from .renderer import AnalysisDetails, Renderer

_RENDER_HTTP_DATA_GOODPUT = 'Goodput'
_RENDER_TCP_DATA_THROUGHPUT = 'Throughput'

_NANOSECONDS_PER_MILLISECOND = 1e6
_NANOSECONDS_PER_SECOND = 1e9

_AXIS_TITLE_RTT = "Round Trip Time"
_AXIS_UNIT_RTT = "ms"
_AXIS_UNIT_SPEED = "bits/s"


class HttpRenderer(Renderer):

    __slots__ = ('_data_analyser',)

    def __init__(self, data_analyser: HttpDataAnalyser) -> None:
        super().__init__()
        self._data_analyser = data_analyser

    def render(self) -> str:
        analysis_log = self._data_analyser.log
        mobile_client = self._data_analyser.mobile_client
        # Get the data
        http_method = self._data_analyser.http_method
        tcp_data_total_bytes = TCP_DATA_RX_TOTAL_BYTES
        http_data_bytes = HTTP_DATA_RX_BYTES
        if http_method == HttpMethod.GET.value:
            df_tx_tcp = self._data_analyser.df_tcp_server
            if mobile_client:
                df_rx_tcp = self._data_analyser.df_tcp_server
                df_rx_http = self._data_analyser.df_http_server
                tcp_data_total_bytes = TCP_DATA_TX_TOTAL_BYTES
                http_data_bytes = HTTP_DATA_TX_BYTES
            else:
                df_rx_tcp = self._data_analyser.df_tcp_client
                df_rx_http = self._data_analyser.df_http_client
        elif http_method == HttpMethod.PUT.value:
            if mobile_client:
                df_tx_tcp = self._data_analyser.df_tcp_server
            else:
                df_tx_tcp = self._data_analyser.df_tcp_client
            df_rx_tcp = self._data_analyser.df_tcp_server
            df_rx_http = self._data_analyser.df_http_server
        else:
            raise UnsupportedHTTPMethod('Unsupported HTTP Method')

        # Determine HTTP average goodput (in bits per second)
        df_http_avg_goodput = df_rx_http[[
            http_data_bytes, HTTP_DATA_INTERVAL_DURATION
        ]]
        df_http_avg_goodput = _to_data_rate(
            df_http_avg_goodput, http_data_bytes, HTTP_DATA_INTERVAL_DURATION
        )
        # Filtered view on the 'Goodput' column only
        df_http_avg_goodput_bits = to_bitrate(
            (df_http_avg_goodput, http_data_bytes)
        )
        df_http_avg_goodput_bits.rename(
            columns={http_data_bytes: _RENDER_HTTP_DATA_GOODPUT}
        )

        # Determine TCP average throughput (in bits per second)
        df_tcp_avg_throughput = df_rx_tcp[[
            tcp_data_total_bytes, TCP_DATA_INTERVAL_DURATION
        ]]
        df_tcp_avg_throughput = _to_data_rate(
            df_tcp_avg_throughput, tcp_data_total_bytes,
            TCP_DATA_INTERVAL_DURATION
        )
        # Filtered view on the 'Throughput' column only
        df_tcp_avg_throughput_bits = to_bitrate(
            (df_tcp_avg_throughput, tcp_data_total_bytes)
        )
        df_tcp_avg_throughput_bits.rename(
            columns={tcp_data_total_bytes: _RENDER_TCP_DATA_THROUGHPUT}
        )

        # Get RTT values and convert nanoseconds -> milliseconds:
        df_min_rtt = (
            df_tx_tcp[[TCP_DATA_MINIMUM_RTT]] / _NANOSECONDS_PER_MILLISECOND
        )
        df_max_rtt = (
            df_tx_tcp[[TCP_DATA_MAXIMUM_RTT]] / _NANOSECONDS_PER_MILLISECOND
        )
        df_avg_rtt = (
            df_tx_tcp[[TCP_DATA_AVERAGE_RTT]] / _NANOSECONDS_PER_MILLISECOND
        )

        # Filter out retransmission counters and make sure
        # we store the count as int:
        df_tcp_retransmissions = (
            df_tx_tcp[[
                TCP_DATA_SLOW_RETRANSMISSIONS, TCP_DATA_FAST_RETRANSMISSIONS
            ]].astype(
                {
                    TCP_DATA_SLOW_RETRANSMISSIONS: int,
                    TCP_DATA_FAST_RETRANSMISSIONS: int,
                }
            )
        )
        df_tcp_retransmissions['retransmissions'] = (
            df_tcp_retransmissions[[
                TCP_DATA_SLOW_RETRANSMISSIONS, TCP_DATA_FAST_RETRANSMISSIONS
            ]].sum(axis='columns')
        )
        # Filtered view on the retransmissions column only
        df_tcp_retransmissions = df_tcp_retransmissions[['retransmissions']]

        # Set the summary
        result = self._verbatim(analysis_log)

        # Build the graph
        chart = GenericChart(
            "HTTP statistics",
            x_axis_options={"type": "datetime"},
            chart_options={"zoomType": "x"}
        )

        chart.add_series(
            list(df_tcp_avg_throughput_bits.itertuples(index=True)),
            "line",
            "Throughput",
            "Dataspeed",
            _AXIS_UNIT_SPEED,
        )
        chart.add_series(
            list(df_http_avg_goodput_bits.itertuples(index=True)),
            "line",
            "Goodput",
            "Dataspeed",
            _AXIS_UNIT_SPEED,
        )
        chart.add_series(
            list(df_tcp_retransmissions.itertuples(index=True)),
            "column",
            "Retransmissions",
            "Retransmissions",
            "",
        )
        chart.add_series(
            list(df_avg_rtt.itertuples(index=True)),
            "line",
            "Average Round Trip Time",
            _AXIS_TITLE_RTT,
            _AXIS_UNIT_RTT,
        )
        chart.add_series(
            list(df_min_rtt.itertuples(index=True)),
            "line",
            "Minimum Round Trip Time",
            _AXIS_TITLE_RTT,
            _AXIS_UNIT_RTT,
        )
        chart.add_series(
            list(df_max_rtt.itertuples(index=True)),
            "line",
            "Maximum Round Trip Time",
            _AXIS_TITLE_RTT,
            _AXIS_UNIT_RTT,
        )

        result += chart.plot(f'http_container{HttpRenderer.container_id}')
        HttpRenderer.container_id += 1

        return result

    def details(self) -> Optional[AnalysisDetails]:
        # Get the data
        df_tcp_server = self._data_analyser.df_tcp_server
        df_tcp_client = self._data_analyser.df_tcp_client
        df_http_client = self._data_analyser.df_http_client
        df_http_server = self._data_analyser.df_http_server
        total_rx_client = self._data_analyser.total_rx_client
        total_tx_client = self._data_analyser.total_tx_client
        total_rx_server = self._data_analyser.total_rx_server
        total_tx_server = self._data_analyser.total_tx_server
        ts_rx_first_client = self._data_analyser.rx_first_client
        ts_rx_last_client = self._data_analyser.rx_last_client
        ts_tx_first_client = self._data_analyser.tx_first_client
        ts_tx_last_client = self._data_analyser.tx_last_client
        ts_rx_first_server = self._data_analyser.rx_first_server
        ts_rx_last_server = self._data_analyser.rx_last_server
        ts_tx_first_server = self._data_analyser.tx_first_server
        ts_tx_last_server = self._data_analyser.tx_last_server
        http_method = self._data_analyser.http_method

        df_over_time_results_client = df_http_client

        df_over_time_results_client = df_over_time_results_client.rename(
            columns={
                HTTP_DATA_TX_BYTES: 'txBytes',
                HTTP_DATA_RX_BYTES: 'rxBytes',
            }
        )

        df_over_time_results_server = df_http_server

        df_over_time_results_server = df_over_time_results_server.rename(
            columns={
                HTTP_DATA_TX_BYTES: 'txBytes',
                HTTP_DATA_RX_BYTES: 'rxBytes',
            }
        )

        details: AnalysisDetails = {
            'method': http_method,
            'tcpClient': {
                'overTimeResults': df_tcp_client
            },
            'tcpServer': {
                'overTimeResults': df_tcp_server
            },
            'httpClient': {
                'rxBytes': total_rx_client,
                'txBytes': total_tx_client,
                'rxFirst': ts_rx_first_client,
                'rxLast': ts_rx_last_client,
                'txFirst': ts_tx_first_client,
                'txLast': ts_tx_last_client,
                'overTimeResults': df_over_time_results_client
            },
            'httpServer': {
                'rxBytes': total_rx_server,
                'txBytes': total_tx_server,
                'rxFirst': ts_rx_first_server,
                'rxLast': ts_rx_last_server,
                'txFirst': ts_tx_first_server,
                'txLast': ts_tx_last_server,
                'overTimeResults': df_over_time_results_server
            }
        }

        return details


class L4SHttpRenderer(HttpRenderer):
    """
    Render report for the analysis of metrics from an L4S-enabled HTTP flow.
    """
    __slots__ = ()

    def __init__(self, data_analyser: L4SHttpDataAnalyser) -> None:
        super().__init__(data_analyser)

    def render(self) -> str:
        analysis_log = self._data_analyser.log
        mobile_client = self._data_analyser.mobile_client
        # Get the data
        http_method = self._data_analyser.http_method
        tcp_data_total_bytes = TCP_DATA_RX_TOTAL_BYTES
        http_data_bytes = HTTP_DATA_RX_BYTES
        ecn_markings = REMOTE_ECN_MARKINGS
        if http_method == HttpMethod.GET.value:
            df_tx_tcp = self._data_analyser.df_tcp_server
            if mobile_client:
                df_rx_tcp = self._data_analyser.df_tcp_server
                df_rx_http = self._data_analyser.df_http_server
                tcp_data_total_bytes = TCP_DATA_TX_TOTAL_BYTES
                http_data_bytes = HTTP_DATA_TX_BYTES
            else:
                df_rx_tcp = self._data_analyser.df_tcp_client
                df_rx_http = self._data_analyser.df_http_client
        elif http_method == HttpMethod.PUT.value:
            if mobile_client:
                df_tx_tcp = self._data_analyser.df_tcp_server
                ecn_markings = LOCAL_ECN_MARKINGS
            else:
                df_tx_tcp = self._data_analyser.df_tcp_client
            df_rx_tcp = self._data_analyser.df_tcp_server
            df_rx_http = self._data_analyser.df_http_server
        else:
            raise UnsupportedHTTPMethod('Unsupported HTTP Method')

        # Get CE Counters
        tcp_ce_count = df_tx_tcp[[ecn_markings]]

        # Determine HTTP average goodput (in bits per second)
        df_http_avg_goodput = df_rx_http[[
            http_data_bytes, HTTP_DATA_INTERVAL_DURATION
        ]]
        df_http_avg_goodput = _to_data_rate(
            df_http_avg_goodput, http_data_bytes, HTTP_DATA_INTERVAL_DURATION
        )
        # Filtered view on the 'Goodput' column only
        df_http_avg_goodput_bits = to_bitrate(
            (df_http_avg_goodput, http_data_bytes)
        )
        df_http_avg_goodput_bits.rename(
            columns={http_data_bytes: _RENDER_HTTP_DATA_GOODPUT}
        )

        # Determine TCP average throughput (in bits per second)
        df_tcp_avg_throughput = df_rx_tcp[[
            tcp_data_total_bytes, TCP_DATA_INTERVAL_DURATION
        ]]
        df_tcp_avg_throughput = _to_data_rate(
            df_tcp_avg_throughput, tcp_data_total_bytes,
            TCP_DATA_INTERVAL_DURATION
        )
        # Filtered view on the 'Throughput' column only
        df_tcp_avg_throughput_bits = to_bitrate(
            (df_tcp_avg_throughput, tcp_data_total_bytes)
        )
        df_tcp_avg_throughput_bits.rename(
            columns={tcp_data_total_bytes: _RENDER_TCP_DATA_THROUGHPUT}
        )

        # Get RTT values and convert nanoseconds -> milliseconds:
        df_min_rtt = (
            df_tx_tcp[[TCP_DATA_MINIMUM_RTT]] / _NANOSECONDS_PER_MILLISECOND
        )
        df_max_rtt = (
            df_tx_tcp[[TCP_DATA_MAXIMUM_RTT]] / _NANOSECONDS_PER_MILLISECOND
        )
        df_avg_rtt = (
            df_tx_tcp[[TCP_DATA_AVERAGE_RTT]] / _NANOSECONDS_PER_MILLISECOND
        )

        # Filter out retransmission counters and make sure
        # we store the count as int:
        df_tcp_retransmissions = (
            df_tx_tcp[[
                TCP_DATA_SLOW_RETRANSMISSIONS, TCP_DATA_FAST_RETRANSMISSIONS
            ]].astype(
                {
                    TCP_DATA_SLOW_RETRANSMISSIONS: int,
                    TCP_DATA_FAST_RETRANSMISSIONS: int,
                }
            )
        )
        df_tcp_retransmissions['retransmissions'] = (
            df_tcp_retransmissions[[
                TCP_DATA_SLOW_RETRANSMISSIONS, TCP_DATA_FAST_RETRANSMISSIONS
            ]].sum(axis='columns')
        )
        # Filtered view on the retransmissions column only
        df_tcp_retransmissions = df_tcp_retransmissions[['retransmissions']]

        # Set the summary
        result = self._verbatim(analysis_log)

        # Build the graph
        chart = GenericChart(
            "L4S HTTP statistics",
            x_axis_options={"type": "datetime"},
            chart_options={"zoomType": "x"}
        )

        chart.add_series(
            list(df_tcp_avg_throughput_bits.itertuples(index=True)),
            "line",
            "Throughput",
            "Dataspeed",
            _AXIS_UNIT_SPEED,
        )
        chart.add_series(
            list(df_http_avg_goodput_bits.itertuples(index=True)),
            "line",
            "Goodput",
            "Dataspeed",
            _AXIS_UNIT_SPEED,
        )
        chart.add_series(
            list(df_tcp_retransmissions.itertuples(index=True)),
            "column",
            "Retransmissions",
            "Retransmissions",
            "",
        )
        chart.add_series(
            list(df_avg_rtt.itertuples(index=True)),
            "line",
            "Average Round Trip Time",
            _AXIS_TITLE_RTT,
            _AXIS_UNIT_RTT,
        )
        chart.add_series(
            list(df_min_rtt.itertuples(index=True)),
            "line",
            "Minimum Round Trip Time",
            _AXIS_TITLE_RTT,
            _AXIS_UNIT_RTT,
        )
        chart.add_series(
            list(df_max_rtt.itertuples(index=True)),
            "line",
            "Maximum Round Trip Time",
            _AXIS_TITLE_RTT,
            _AXIS_UNIT_RTT,
        )
        chart.add_series(
            list(tcp_ce_count.itertuples(index=True)),
            "column",
            "Counted ECN Markings",
            "ECN Notifications",
            "",
        )

        result += chart.plot(
            f'l4s_http_container{L4SHttpRenderer.container_id}'
        )
        L4SHttpRenderer.container_id += 1

        return result


def _to_data_rate(
    data_snapshot: DataFrame, count_field: str, duration_field: str
) -> DataFrame:
    avg_data_rate_nanoseconds = data_snapshot[[count_field]].div(
        # NOTE: Using filtered view (`[[duration_field]]`)
        #       does not work with `.div()`
        data_snapshot[duration_field].values,
        axis='index'
    )
    return avg_data_rate_nanoseconds.mul(_NANOSECONDS_PER_SECOND)
