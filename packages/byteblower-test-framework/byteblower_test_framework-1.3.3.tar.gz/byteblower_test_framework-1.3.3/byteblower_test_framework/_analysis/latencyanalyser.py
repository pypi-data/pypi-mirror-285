"""Flow analysers for latency related analysis."""
import warnings
from datetime import timedelta  # for type hinting
from typing import Optional  # for type hinting

from pandas import DataFrame, Timestamp  # for type hinting

from .._report.options import Layer2Speed
from .._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting
from .data_analysis.frameblasting import (
    FrameCountAnalyser,
    LatencyAnalyser,
    LatencyCDFAnalyser,
)
from .data_gathering.data_gatherer import DataGatherer  # for type hinting
from .data_gathering.trigger import (
    BaseLatencyCDFFrameCountDataGatherer,
    BaseLatencyFrameCountDataGatherer,
    LatencyCDFFrameCountDataGatherer,
    LatencyFrameCountDataGatherer,
)
from .flow_analyser import AnalysisDetails, FlowAnalyser
from .render.frameblasting import LatencyCDFRenderer, LatencyFrameCountRenderer
from .storage.frame_count import FrameCountData
from .storage.trigger import LatencyData, LatencyDistributionData

#: Default maximum frame loss percentage (range ``[0.0, 100.0]``)
#: used in the latency and frame loss related analysers.
DEFAULT_LOSS_PERCENTAGE: float = 1.0
#: Default maximum average latency in milliseconds
#: used in the latency and frame loss related analysers.
DEFAULT_MAX_LATENCY_THRESHOLD: float = 5  # [ms]
#: Default quantile (range ``[0.0, 100.0]``) for maximum latency
#: used in the latency and frame loss related analysers.
DEFAULT_QUANTILE: float = 99.9


class BaseLatencyFrameLossAnalyser(FlowAnalyser):
    """Base class for analysis of latency and frame count over time.

    The analyser also provides the RX and TX frame count and byte loss
    over the duration of the test.
    For the latency results you will also have the average, minimum and
    maximum latency and average latency jitter.

    This analyser is intended for use with a
    :class:`~.analysis.FlowAnalyser` based on a
    :class:`~.traffic.FrameBlastingFlow`
    (for example :class:`~.traffic.GamingFlow`).

    Supports:

    * Analysis of a single flow
    * Usage in :class:`~.analysis.AnalyserAggregator`.
    """

    #: Data gatherer implementation
    #:
    #: Overwritten by the LatencyFrameLossAnalyser implementation(s)
    _DATA_GATHERER_CLASS = BaseLatencyFrameCountDataGatherer

    __slots__ = (
        '_data_framecount',
        '_data_latency',
        '_data_gatherer',
        '_framecount_analyser',
        '_latency_analyser',
        '_renderer',
        '_layer2_speed',
        '_max_threshold_latency',
        '_max_loss_percentage',
    )

    def __init__(
        self,
        _type: str,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        max_loss_percentage: float = DEFAULT_LOSS_PERCENTAGE,
        max_threshold_latency: float = DEFAULT_MAX_LATENCY_THRESHOLD
    ):
        """Create the latency and frame count over time analyser base.

        :param _type: Descriptive type for the analyser implementation
        :type type: str
        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param max_loss_percentage: Maximum allowed byte loss in %,
           defaults to :const:`DEFAULT_LOSS_PERCENTAGE`
        :type max_loss_percentage: float, optional
        :param max_threshold_latency: Maximum allowed average latency in
           milliseconds, defaults to :const:`DEFAULT_MAX_LATENCY_THRESHOLD`
        :type max_threshold_latency: float, optional
        """
        super().__init__(_type)
        self._data_framecount = FrameCountData()
        self._data_latency = LatencyData()
        self._data_gatherer = None
        self._framecount_analyser = None
        self._latency_analyser = None
        self._renderer = None
        self._layer2_speed = layer2_speed
        self._max_loss_percentage = max_loss_percentage
        self._max_threshold_latency = max_threshold_latency

    def _initialize(self) -> None:
        flow = self.flow
        flow.require_stream_data_gatherer()
        self._data_gatherer: DataGatherer = self._DATA_GATHERER_CLASS(
            self._data_framecount, self._data_latency, self.flow
        )
        self._framecount_analyser = FrameCountAnalyser(
            flow.stream_frame_count_data, self._data_framecount,
            self._layer2_speed, self._max_loss_percentage
        )
        self._latency_analyser = LatencyAnalyser(
            self._data_latency, self._max_threshold_latency
        )
        self._renderer = LatencyFrameCountRenderer(
            self._framecount_analyser, self._latency_analyser
        )

    def prepare_configure(self) -> None:
        self._data_gatherer.prepare_configure()

    def initialize(self) -> None:
        self._data_gatherer.initialize()

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        super().prepare_start()
        self._data_gatherer.prepare_start(maximum_run_time=maximum_run_time)
        self._framecount_analyser.prepare_start()
        self._latency_analyser.prepare_start()

    def process(self) -> None:
        self._data_gatherer.process()

    def updatestats(self) -> None:
        self._data_gatherer.updatestats()

    @property
    def finished(self):
        return self._data_gatherer.finished

    def analyse(self) -> None:
        self._data_gatherer.summarize()
        self._framecount_analyser.analyse()
        self._latency_analyser.analyse()

        if (self._framecount_analyser.has_passed is None
                and self._latency_analyser.has_passed is None):
            has_passed = None
        else:
            has_passed = (
                self._framecount_analyser.has_passed
                and self._latency_analyser.has_passed
            )

        self._set_result(has_passed)
        self._add_failure_causes(self._framecount_analyser.failure_causes)
        self._add_failure_causes(self._latency_analyser.failure_causes)

    def release(self) -> None:
        super().release()
        self._data_gatherer.release()

    def render(self) -> str:
        return self._renderer.render()

    def details(self) -> Optional[AnalysisDetails]:
        return self._renderer.details()

    @property
    def flow(self) -> FrameBlastingFlow:
        """Return Flow implementation.

        Useful for correct type hinting.
        """
        return self._flow

    @property
    def log(self) -> str:
        """Return the summary log text.

        .. note::
           Used for textual representation of the results in test reports.

        :return: Summary log text.
        :rtype: str
        """
        return '\n'.join(
            (self._framecount_analyser.log, self._latency_analyser.log)
        )

    @property
    def df_tx_bytes(self) -> DataFrame:
        """Return ``DataFrame`` of transmitted bytes per interval.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.df_tx_bytes

    @property
    def df_rx_bytes(self) -> DataFrame:
        """Return ``DataFrame`` of received bytes per interval.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.df_rx_bytes

    @property
    def total_tx_bytes(self) -> int:
        """Return total transmitted number of bytes.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_tx_bytes

    @property
    def total_rx_bytes(self) -> int:
        """Return total received number of bytes.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_rx_bytes

    @property
    def total_tx_vlan_bytes(self) -> int:
        """Return total number of bytes transmitted in Layer2.5 VLAN header.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_tx_vlan_bytes

    @property
    def total_rx_vlan_bytes(self) -> int:
        """Return total number of bytes received in Layer2.5 VLAN header.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_rx_vlan_bytes

    @property
    def total_tx_packets(self) -> int:
        """Return total transmitted number of packets.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_tx_packets

    @property
    def total_rx_packets(self) -> int:
        """Return total received number of packets.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.

        .. note::
           Only returns the number of packets with "valid" latency tag.
        """
        return self._latency_analyser.final_packet_count_valid

    @property
    def timestamp_tx_first(self) -> Optional[Timestamp]:
        """Return the timestamp of the first transmitted packet."""
        return self._framecount_analyser.timestamp_tx_first

    @property
    def timestamp_tx_last(self) -> Optional[Timestamp]:
        """Return the timestamp of the last transmitted packet."""
        return self._framecount_analyser.timestamp_tx_last

    @property
    def timestamp_rx_first(self) -> Optional[Timestamp]:
        """Return the timestamp of the first received packet.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.timestamp_rx_first

    @property
    def timestamp_rx_last(self) -> Optional[Timestamp]:
        """Return the timestamp of the last received packet.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.timestamp_rx_last

    @property
    def final_min_latency(self) -> Optional[float]:
        """Return the minimum latency in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_analyser.final_min_latency

    @property
    def final_max_latency(self) -> Optional[float]:
        """Return the maximum latency in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_analyser.final_max_latency

    @property
    def final_avg_latency(self) -> Optional[float]:
        """Return the average latency in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_analyser.final_avg_latency

    @property
    def final_avg_jitter(self) -> Optional[float]:
        """Return the average jitter in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_analyser.final_avg_jitter


class LatencyFrameLossAnalyser(BaseLatencyFrameLossAnalyser):
    """Analyse latency and frame count over time.

    The analyser also provides the RX and TX frame count and byte loss
    over the duration of the test.
    For the latency results you will also have the average, minimum and
    maximum latency and average latency jitter.

    This analyser is intended for use with a
    :class:`~.traffic.Flow` based on a
    :class:`~.traffic.FrameBlastingFlow`
    (for example :class:`~.traffic.GamingFlow`).

    Supports:

    * Analysis of a single flow
    * Usage in :class:`~.analysis.AnalyserAggregator`.
    """

    _DATA_GATHERER_CLASS = LatencyFrameCountDataGatherer

    __slots__ = ()

    def __init__(
        self,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        max_loss_percentage: float = DEFAULT_LOSS_PERCENTAGE,
        max_threshold_latency: float = DEFAULT_MAX_LATENCY_THRESHOLD
    ):
        """Create the latency and frame count over time analyser.

        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param max_loss_percentage: Maximum allowed byte loss in %,
           defaults to :const:`DEFAULT_LOSS_PERCENTAGE`
        :type max_loss_percentage: float, optional
        :param max_threshold_latency: Maximum allowed average latency in
           milliseconds, defaults to :const:`DEFAULT_MAX_LATENCY_THRESHOLD`
        :type max_threshold_latency: float, optional
        """
        super().__init__(
            'Frame latency and loss analyser',
            layer2_speed=layer2_speed,
            max_loss_percentage=max_loss_percentage,
            max_threshold_latency=max_threshold_latency
        )


class BaseLatencyCDFFrameLossAnalyser(FlowAnalyser):
    """Base class for analysis of latency CDF and total frame count.

    The analyser provides the latency CDF graph, RX and TX frame count
    and byte loss over the duration of the test.
    For the latency results you will also have the average, minimum and
    maximum latency and average latency jitter.

    This analyser is intended for use with a
    :class:`~.analysis.FlowAnalyser` based on a
    :class:`~.traffic.FrameBlastingFlow`
    (for example :class:`~.traffic.GamingFlow`).

    Supports:

    * Analysis of a single flow
    * Summary results for multiple flows
      (via :class:`~.analysis.AnalyserAggregator`)

    .. warning::
       Does not provide over time results for
       :class:`~.analysis.AnalyserAggregator`.
    """

    #: Data gatherer implementation
    #:
    #: Overwritten by the LatencyCDFFrameLossAnalyser implementation(s)
    _DATA_GATHERER_CLASS = BaseLatencyCDFFrameCountDataGatherer

    __slots__ = (
        '_data_framecount',
        '_data_latencydistribution',
        '_data_gatherer',
        '_framecount_analyser',
        '_latency_cdf_analyser',
        '_renderer',
        '_layer2_speed',
        '_max_loss_percentage',
        '_max_threshold_latency',
        '_quantile',
    )

    def __init__(
        self,
        _type: str,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        max_loss_percentage: float = DEFAULT_LOSS_PERCENTAGE,
        max_threshold_latency: float = DEFAULT_MAX_LATENCY_THRESHOLD,
        quantile: float = DEFAULT_QUANTILE
    ):
        """Create the latency CDF and total frame count analyser base.

        The latency for the CDF graph will be analysed over a range of
        ``[0, 50 * max_threshold_latency[``.

        :param _type: Descriptive type for the analyser implementation
        :type type: str
        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param max_loss_percentage: Maximum allowed byte loss in %,
           defaults to :const:`DEFAULT_LOSS_PERCENTAGE`
        :type max_loss_percentage: float, optional
        :param max_threshold_latency: Maximum allowed average latency in
           milliseconds, defaults to :const:`DEFAULT_MAX_LATENCY_THRESHOLD`
        :type max_threshold_latency: float, optional
        :param quantile: Quantile for which the latency must be less than the
           given maximum average latency, defaults to :const:`DEFAULT_QUANTILE`
        :type quantile: float, optional
        """
        super().__init__(_type)
        self._data_framecount = FrameCountData()
        self._data_latencydistribution = LatencyDistributionData()
        self._data_gatherer = None
        self._framecount_analyser = None
        self._latency_cdf_analyser = None
        self._renderer = None
        self._layer2_speed = layer2_speed
        self._max_loss_percentage = max_loss_percentage
        self._max_threshold_latency = max_threshold_latency
        self._quantile = quantile

    def _initialize(self) -> None:
        flow = self.flow
        flow.require_stream_data_gatherer()
        self._data_gatherer: DataGatherer = self._DATA_GATHERER_CLASS(
            self._data_framecount, self._data_latencydistribution,
            self._max_threshold_latency, self.flow
        )
        self._framecount_analyser = FrameCountAnalyser(
            flow.stream_frame_count_data, self._data_framecount,
            self._layer2_speed, self._max_loss_percentage
        )
        self._latency_cdf_analyser = LatencyCDFAnalyser(
            self._data_latencydistribution, self._max_threshold_latency,
            self._quantile
        )
        self._renderer = LatencyCDFRenderer(
            self._framecount_analyser, self._latency_cdf_analyser
        )

    def prepare_configure(self) -> None:
        self._data_gatherer.prepare_configure()

    def initialize(self) -> None:
        self._data_gatherer.initialize()

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        super().prepare_start()
        self._data_gatherer.prepare_start(maximum_run_time=maximum_run_time)
        self._framecount_analyser.prepare_start()
        self._latency_cdf_analyser.prepare_start()

    def process(self) -> None:
        self._data_gatherer.process()

    def updatestats(self) -> None:
        self._data_gatherer.updatestats()

    @property
    def finished(self):
        return self._data_gatherer.finished

    def analyse(self) -> None:
        self._data_gatherer.summarize()
        self._framecount_analyser.analyse()
        self._latency_cdf_analyser.analyse()

        if (self._framecount_analyser.has_passed is None
                and self._latency_cdf_analyser.has_passed is None):
            has_passed = None
        else:
            has_passed = (
                self._framecount_analyser.has_passed
                and self._latency_cdf_analyser.has_passed
            )

        self._set_result(has_passed)
        self._add_failure_causes(self._framecount_analyser.failure_causes)
        self._add_failure_causes(self._latency_cdf_analyser.failure_causes)

    def release(self) -> None:
        super().release()
        self._data_gatherer.release()

    def render(self) -> str:
        return self._renderer.render()

    def details(self) -> Optional[AnalysisDetails]:
        return self._renderer.details()

    @property
    def flow(self) -> FrameBlastingFlow:
        """Return Flow implementation.

        Useful for correct type hinting.
        """
        return self._flow

    @property
    def log(self) -> str:
        """Return the summary log text.

        .. note::
           Used for textual representation of the results in test reports.

        :return: Summary log text.
        :rtype: str
        """
        return '\n'.join(
            (self._framecount_analyser.log, self._latency_cdf_analyser.log)
        )

    @property
    def total_tx_bytes(self) -> int:
        """Return total transmitted number of bytes.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_tx_bytes

    @property
    def total_rx_bytes(self) -> int:
        """Return total received number of bytes.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_rx_bytes

    @property
    def total_tx_vlan_bytes(self) -> int:
        """Return total number of bytes transmitted in Layer2.5 VLAN header.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_tx_vlan_bytes

    @property
    def total_rx_vlan_bytes(self) -> int:
        """Return total number of bytes received in Layer2.5 VLAN header.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_rx_vlan_bytes

    @property
    def total_tx_packets(self) -> int:
        """Return total transmitted number of packets.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.total_tx_packets

    @property
    def timestamp_tx_first(self) -> Optional[Timestamp]:
        """Return the timestamp of the first transmitted packet."""
        return self._framecount_analyser.timestamp_tx_first

    @property
    def timestamp_tx_last(self) -> Optional[Timestamp]:
        """Return the timestamp of the last transmitted packet."""
        return self._framecount_analyser.timestamp_tx_last

    @property
    def timestamp_rx_first(self) -> Optional[Timestamp]:
        """Return the timestamp of the first received packet.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.timestamp_rx_first

    @property
    def timestamp_rx_last(self) -> Optional[Timestamp]:
        """Return the timestamp of the last received packet.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._framecount_analyser.timestamp_rx_last

    @property
    def total_rx_packets(self) -> int:
        """Return total received number of packets.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.

        .. note::
           Only returns the number of packets with "valid" latency tag.
        """
        return self._latency_cdf_analyser.final_packet_count_valid

    @property
    def final_min_latency(self) -> Optional[float]:
        """Return the minimum latency in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_cdf_analyser.final_min_latency

    @property
    def final_max_latency(self) -> Optional[float]:
        """Return the maximum latency in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_cdf_analyser.final_max_latency

    @property
    def final_avg_latency(self) -> Optional[float]:
        """Return the average latency in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_cdf_analyser.final_avg_latency

    @property
    def final_avg_jitter(self) -> Optional[float]:
        """Return the average jitter in milliseconds.

        .. note::
           Used by the :class:`~.analysis.AnalyserAggregator`.
        """
        return self._latency_cdf_analyser.final_avg_jitter


class LatencyCDFFrameLossAnalyser(BaseLatencyCDFFrameLossAnalyser):
    """Analyse latency CDF and total frame count.

    The analyser provides the latency CDF graph, RX and TX frame count
    and byte loss over the duration of the test.
    For the latency results you will also have the average, minimum and
    maximum latency and average latency jitter.

    This analyser is intended for use with a
    :class:`~.traffic.Flow` based on a
    :class:`~.traffic.FrameBlastingFlow`
    (for example :class:`~.traffic.GamingFlow`).

    Supports:

    * Analysis of a single flow
    * Summary results for multiple flows
      (via :class:`~.analysis.AnalyserAggregator`)

    .. warning::
       Does not provide over time results for
       :class:`~.analysis.AnalyserAggregator`.
    """

    _DATA_GATHERER_CLASS = LatencyCDFFrameCountDataGatherer

    __slots__ = ()

    def __init__(
        self,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        max_loss_percentage: float = DEFAULT_LOSS_PERCENTAGE,
        max_threshold_latency: float = DEFAULT_MAX_LATENCY_THRESHOLD,
        quantile: float = DEFAULT_QUANTILE
    ):
        """Create the latency CDF and total frame count analyser.

        The latency for the CDF graph will be analysed over a range of
        ``[0, 50 * max_threshold_latency[``.

        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param max_loss_percentage: Maximum allowed byte loss in %,
           defaults to :const:`DEFAULT_LOSS_PERCENTAGE`
        :type max_loss_percentage: float, optional
        :param max_threshold_latency: Maximum allowed average latency in
           milliseconds, defaults to :const:`DEFAULT_MAX_LATENCY_THRESHOLD`
        :type max_threshold_latency: float, optional
        :param quantile: Quantile for which the latency must be less than the
           given maximum average latency, defaults to :const:`DEFAULT_QUANTILE`
        :type quantile: float, optional
        """
        super().__init__(
            'Frame latency CDF and loss analyser',
            layer2_speed=layer2_speed,
            max_loss_percentage=max_loss_percentage,
            max_threshold_latency=max_threshold_latency,
            quantile=quantile
        )
