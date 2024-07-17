"""Flow analysers for frame loss related analysis."""
from datetime import timedelta  # for type hinting
from typing import Optional  # for type hinting

from pandas import DataFrame, Timestamp  # for type hinting

from .._report.options import Layer2Speed
from .._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting
from .data_analysis.frameblasting import FrameCountAnalyser
from .data_gathering.trigger import (
    BaseFrameCountDataGatherer,
    FrameCountDataGatherer,
)
from .flow_analyser import AnalysisDetails, FlowAnalyser
from .render.frameblasting import FrameCountRenderer
from .storage.frame_count import FrameCountData

#: Default maximum frame loss percentage (range ``[0.0, 100.0]``)
#: used in the frame loss related analysers.
DEFAULT_LOSS_PERCENTAGE = 1.0


class BaseFrameLossAnalyser(FlowAnalyser):
    """Base class for analysis of frame count over time.

    The analyser also provides the RX and TX frame count and byte loss
    over the duration of the test.

    This analyser is intended for use with
    :class:`~.analysis.FlowAnalyser` based on a
    :class:`~.traffic.FrameBlastingFlow`
    (for example :class:`~.traffic.GamingFlow`).

    Supports:

    * Analysis of a single flow
    * Usage in :class:`~.analysis.AnalyserAggregator`.
    """

    #: Data gatherer implementation
    #:
    #: Overwritten by the FrameLossAnalyser implementation(s)
    _DATA_GATHERER_CLASS = BaseFrameCountDataGatherer

    __slots__ = (
        '_data',
        '_data_gatherer',
        '_data_analyser',
        '_renderer',
        '_layer2_speed',
        '_max_loss_percentage',
    )

    def __init__(
        self,
        _type: str,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        max_loss_percentage: float = DEFAULT_LOSS_PERCENTAGE
    ):
        """Create frame count over time analyser base.

        :param _type: Descriptive type for the analyser implementation
        :type type: str
        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param max_loss_percentage: Maximum allowed packet loss in %,
           defaults to :const:`DEFAULT_LOSS_PERCENTAGE`
        :type max_loss_percentage: float, optional
        """
        super().__init__(_type)
        self._data = FrameCountData()
        self._data_gatherer: BaseFrameCountDataGatherer = None
        self._data_analyser = None
        self._renderer = None
        self._layer2_speed = layer2_speed
        self._max_loss_percentage = max_loss_percentage

    @property
    def flow(self) -> FrameBlastingFlow:
        """Return Flow implementation.

        Useful for correct type hinting.
        """
        return self._flow

    def _initialize(self) -> None:
        flow = self.flow
        flow.require_stream_data_gatherer()
        self._data_gatherer = self._DATA_GATHERER_CLASS(self._data, flow)
        self._data_analyser = FrameCountAnalyser(
            flow.stream_frame_count_data, self._data, self._layer2_speed,
            self._max_loss_percentage
        )
        self._renderer = FrameCountRenderer(self._data_analyser)

    def prepare_configure(self) -> None:
        self._data_gatherer.prepare_configure()

    def initialize(self) -> None:
        self._data_gatherer.initialize()

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        super().prepare_start()
        self._data_gatherer.prepare_start(maximum_run_time=maximum_run_time)
        self._data_analyser.prepare_start()

    def process(self) -> None:
        self._data_gatherer.process()

    def updatestats(self) -> None:
        self._data_gatherer.updatestats()

    @property
    def finished(self) -> bool:
        return self._data_gatherer.finished

    def analyse(self) -> None:
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
    def df_tx_bytes(self) -> DataFrame:
        """Return ``DataFrame`` of transmitted bytes per interval.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.df_tx_bytes

    @property
    def df_rx_bytes(self) -> DataFrame:
        """Return ``DataFrame`` of received bytes per interval.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.df_rx_bytes

    @property
    def total_tx_bytes(self) -> int:
        """Return total transmitted number of bytes.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.total_tx_bytes

    @property
    def total_rx_bytes(self) -> int:
        """Return total received number of bytes.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.total_rx_bytes

    @property
    def total_tx_vlan_bytes(self) -> int:
        """Return total number of bytes transmitted in Layer2.5 VLAN header.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.total_tx_vlan_bytes

    @property
    def total_rx_vlan_bytes(self) -> int:
        """Return total number of bytes received in Layer2.5 VLAN header.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.total_rx_vlan_bytes

    @property
    def total_tx_packets(self) -> int:
        """Return total transmitted number of packets.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.total_tx_packets

    @property
    def total_rx_packets(self) -> int:
        """Return total received number of packets.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.total_rx_packets

    @property
    def timestamp_tx_first(self) -> Optional[Timestamp]:
        """Return the timestamp of the first transmitted packet."""
        return self._data_analyser.timestamp_tx_first

    @property
    def timestamp_tx_last(self) -> Optional[Timestamp]:
        """Return the timestamp of the last transmitted packet."""
        return self._data_analyser.timestamp_tx_last

    @property
    def timestamp_rx_first(self) -> Timestamp:
        """Return the timestamp of the first received packet.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.timestamp_rx_first

    @property
    def timestamp_rx_last(self) -> Timestamp:
        """Return the timestamp of the last received packet.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._data_analyser.timestamp_rx_last


class FrameLossAnalyser(BaseFrameLossAnalyser):
    """Analyse frame count over time.

    The analyser also provides the RX and TX frame count and frame loss
    over the duration of the test.

    This analyser is intended for use with a
    :class:`~.traffic.Flow` based on a
    :class:`~.traffic.FrameBlastingFlow`
    (for example :class:`~.traffic.GamingFlow`).

    Supports:

    * Analysis of a single flow
    * Usage in :class:`~.analysis.AnalyserAggregator`.
    """

    _DATA_GATHERER_CLASS = FrameCountDataGatherer

    __slots__ = ()

    def __init__(
        self,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        max_loss_percentage: float = DEFAULT_LOSS_PERCENTAGE
    ):
        """Create frame count over time analyser.

        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param max_loss_percentage: Maximum allowed packet loss in %,
           defaults to :const:`DEFAULT_LOSS_PERCENTAGE`
        :type max_loss_percentage: float, optional
        """
        super().__init__(
            'Frame loss analyser',
            layer2_speed=layer2_speed,
            max_loss_percentage=max_loss_percentage
        )
