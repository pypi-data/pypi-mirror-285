import logging
from datetime import timedelta  # for type hinting
from typing import Optional  # for type hinting

from pandas import Timestamp  # for type hinting

from .._traffic.tcpflow import TcpFlow  # for type hinting
from .data_analysis.tcp import HttpDataAnalyser, L4SHttpDataAnalyser
from .data_gathering.tcp import HttpDataGatherer, L4SHttpDataGatherer
from .flow_analyser import AnalysisDetails, FlowAnalyser
from .render.tcp import HttpRenderer, L4SHttpRenderer
from .storage.tcp import HttpData, L4SHttpData


class HttpAnalyser(FlowAnalyser):
    """Analyse HTTP and TCP statistics over time.

    The analyser currently only provides the HTTP goodput over time
    and the average HTTP goodput over the duration of the test.

    .. note::
       There is no specific analysis performed and the test
       will always state no analysis is done.

    This analyser is intended for use with a :class:`~.traffic.HTTPFlow`.

    Supports:

    * Analysis of a single flow

    .. warning::
        Does not support aggregation data from multiple flows
        (via :class:`~.analysis.AnalyserAggregator`).
    """

    __slots__ = (
        '_http_data',
        '_data_gatherer',
        '_data_analyser',
        '_renderer',
    )

    def __init__(
        self, analyser_type: str = "HTTP analyser", http_data_class=HttpData
    ):
        """Create the HTTP and TCP statistics over time analyser."""
        super().__init__(analyser_type)
        self._http_data = http_data_class()
        self._data_gatherer = None
        self._data_analyser = None
        self._renderer = None

    @property
    def flow(self) -> TcpFlow:
        """Return Flow implementation.

        Useful for correct type hinting.
        """
        return self._flow

    def _initialize(self) -> None:
        self._data_gatherer = HttpDataGatherer(
            self._http_data, self.flow._bb_tcp_clients
        )
        self._data_analyser = HttpDataAnalyser(self._http_data)
        self._renderer = HttpRenderer(self._data_analyser)

    def prepare_configure(self) -> None:
        self._data_gatherer.prepare_configure()

    def initialize(self) -> None:
        self._data_gatherer.initialize()

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        super().prepare_start()
        if self.flow._bb_tcp_server is None:
            logging.warning(
                'Flow %r: No TCP server available.'
                ' No data gathering done for TCP server.',
                self.flow.name,
            )
        self._data_gatherer.set_http_server(self.flow._bb_tcp_server)
        self._data_gatherer.prepare_start(maximum_run_time=maximum_run_time)
        self._data_analyser.prepare_start()

    def process(self) -> None:
        self._data_gatherer.process()

    def updatestats(self) -> None:
        """Analyse the result.

        What would be bad?

        * TCP sessions not going to Finished
        """
        # Let's analyse the result
        self._data_gatherer.updatestats()

    @property
    def finished(self) -> bool:
        # NOTE: No need to check whether HTTP Client(s)/Server have finished.
        #       The HTTP Client(s) are always on Endpoints and whether they
        #       have finished is already checked at the HTTPFlow.
        #       So we should be safe to always return ``True`` here.
        #       It saves us some client-server communication delays.
        return True

    def analyse(self) -> None:
        # Currently, no pass/fail criteria.
        self._data_gatherer.summarize()
        self._data_analyser.analyse()
        self._set_result(self._data_analyser.has_passed)
        self._add_failure_causes(self._data_analyser.failure_causes)

    def release(self) -> None:
        super().release()
        self._data_gatherer.release()

    @property
    def log(self) -> str:
        """Return the summary log text.

        .. note::
           Used for textual representation of the results in test reports.

        :return: Summary log text.
        :rtype: str
        """
        return self._data_analyser.log

    def render(self) -> str:
        return self._renderer.render()

    def details(self) -> Optional[AnalysisDetails]:
        return self._renderer.details()

    @property
    def http_method(self):
        """Return the configured HTTP Request Method."""
        return self._data_analyser.http_method

    @property
    def total_rx_client(self) -> int:
        """Number of received bytes at HTTP Client."""
        return self._data_analyser.total_rx_client

    @property
    def total_tx_client(self) -> int:
        """Number of transmitted bytes at HTTP Client."""
        return self._data_analyser.total_tx_client

    @property
    def total_rx_server(self) -> int:
        """Number of received bytes at HTTP Server."""
        return self._data_analyser.total_rx_server

    @property
    def total_tx_server(self) -> int:
        """Number of transmitted bytes at HTTP Server."""
        return self._data_analyser.total_tx_server

    @property
    def rx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Client."""
        return self._data_analyser.rx_first_client

    @property
    def rx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Client."""
        return self._data_analyser.rx_last_client

    @property
    def tx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Client."""
        return self._data_analyser.tx_first_client

    @property
    def tx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Client."""
        return self._data_analyser.tx_last_client

    @property
    def rx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Server."""
        return self._data_analyser.rx_first_server

    @property
    def rx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Server."""
        return self._data_analyser.rx_last_server

    @property
    def tx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Server."""
        return self._data_analyser.tx_first_server

    @property
    def tx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Server."""
        return self._data_analyser.tx_last_server


class L4SHttpAnalyser(HttpAnalyser):
    """
    Analyse L4S enabled HTTP and TCP statistics over time.

    Over the duration of the test, this analyser provides:

    * HTTP goodput over time
    * HTTP retransmissions
    * Average Round Trip Time (RTT)
    * Min/Max RTT
    * Congestion Experienced (CE) count

    .. note::
       There is no specific analysis performed and the test
       will always state no analysis is done.

    This analyser is used with a :class:`~.traffic.HTTPFlow`, where
    **TCP Prague** is **enabled**.

    Supports:

    * Analysis of a single flow

    .. warning::
        Does not support aggregation data from multiple flows
        (via :class:`~.analysis.AnalyserAggregator`).

    .. note::
       - L4S support requires at least ByteBlower API v2.22.0, Server
         and Meeting Point v2.22.0, and ByteBlower Endpoint v2.22.0
       - When using Endpoints, L4S must be supported and enabled
         in the hosting OS

    .. versionadded:: 1.3.0
       Added L4S enabled HTTP and its analysers.
    """
    __slots__ = ()

    def __init__(self):
        """
        Create the L4S and RTT statistics for HTTP and TCP over time analyser.
        """
        super().__init__("L4S HTTP analyser", L4SHttpData)

    def _initialize(self) -> None:
        self._data_gatherer = L4SHttpDataGatherer(
            self._http_data, self.flow._bb_tcp_clients
        )
        self._data_analyser = L4SHttpDataAnalyser(self._http_data)
        self._renderer = L4SHttpRenderer(self._data_analyser)
