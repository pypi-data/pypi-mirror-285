"""Flow analysers for voice related analysis."""
from datetime import timedelta  # for type hinting
from typing import Optional  # for type hinting

from .._report.options import Layer2Speed
from .._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting
from .data_analysis.frameblasting import MosAnalyser
from .data_gathering.trigger import LatencyFrameCountDataGatherer
from .flow_analyser import AnalysisDetails, FlowAnalyser
from .render.frameblasting import MosRenderer
from .storage.frame_count import FrameCountData
from .storage.trigger import LatencyData

#: Default minimum MOS (range ``[0.0, 5.0]``)
#: used in the voice analyser.
DEFAULT_MINIMUM_MOS: float = 4


class VoiceAnalyser(FlowAnalyser):
    """Analyse the MOS of a voice flow.

    Calculates the Mean Opinion Score (MOS) over the duration of the test.

    The analyser also provides the RX and TX frame count and frame loss
    over the duration of the test.

    This analyser is intended for use with a :class:`~.traffic.VoiceFlow`.

    Supports:

    * Analysis of a single flow

    .. warning::
       Does not support usage in
       :class:`~.analysis.AnalyserAggregator`.
    """

    __slots__ = (
        '_data_framecount',
        '_data_latency',
        '_data_gatherer',
        '_data_analyser',
        '_renderer',
        '_layer2_speed',
        '_minimum_mos',
    )

    def __init__(
        self,
        layer2_speed: Layer2Speed = Layer2Speed.frame,
        minimum_mos: float = DEFAULT_MINIMUM_MOS
    ):
        """Create the voice analyser.

        :param layer2_speed: Configuration setting to select the layer 2
           speed reporting, defaults to :attr:`~.options.Layer2Speed.frame`
        :type layer2_speed: ~options.Layer2Speed, optional
        :param minimum_mos: Minimum required MOS value,
           defaults to :const:`DEFAULT_MINIMUM_MOS`
        :type minimum_mos: float, optional
        """
        super().__init__('VoIP Analyser')
        self._data_framecount = FrameCountData()
        self._data_latency = LatencyData()
        self._data_gatherer: LatencyFrameCountDataGatherer = None
        self._data_analyser: MosAnalyser = None
        self._renderer: MosRenderer = None
        self._layer2_speed = layer2_speed
        self._minimum_mos = minimum_mos

    @property
    def flow(self) -> FrameBlastingFlow:
        """Return Flow implementation.

        Useful for correct type hinting.
        """
        return self._flow

    def _initialize(self) -> None:
        flow = self.flow
        flow.require_stream_data_gatherer()
        self._data_gatherer = LatencyFrameCountDataGatherer(
            self._data_framecount, self._data_latency, self.flow
        )
        self._data_analyser = MosAnalyser(
            flow.stream_frame_count_data, self._data_framecount,
            self._data_latency, self._layer2_speed, self._minimum_mos
        )
        self._renderer = MosRenderer(self._data_analyser)

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
