"""ByteBlower UDP frame blasting interface module."""
import logging
from datetime import timedelta  # for type hinting
from datetime import datetime
from statistics import mean
from time import sleep
from typing import (  # for type hinting
    TYPE_CHECKING,
    Iterable,
    List,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from byteblowerll.byteblower import Stream as TxStream  # for type hinting
from byteblowerll.byteblower import (
    StreamMobile as TxStreamMobile,  # for type hinting
)

from .._analysis.data_gathering.stream import (
    StreamDataGatherer,  # for type hinting
)
from .._analysis.data_gathering.stream import StreamFrameCountDataGatherer
from .._analysis.storage.frame_count import FrameCountData
from .._analysis.storage.stream import StreamStatusData
from .._endpoint.endpoint import Endpoint  # for type hinting
from .._endpoint.port import Port  # for type hinting
from .._helpers.syncexec import SynchronizedExecutable
from .._traffic.stream import StreamErrorSource  # for type hinting
from .._traffic.stream import StreamErrorStatus
from ..constants import (
    DEFAULT_FRAME_RATE,
    DEFAULT_NUMBER_OF_FRAMES,
    INFINITE_NUMBER_OF_FRAMES,
)
from ..exceptions import (
    ConflictingInput,
    FeatureNotSupported,
    InfiniteDuration,
)
from ._tx_stream_controller import (
    EndpointTxStreamController,
    PortTxStreamController,
)
from .flow import RuntimeErrorInfo  # for type hinting
from .flow import Flow
from .frame import Frame  # for type hinting
from .imix import Imix  # for type hinting
from .mobile_frame import MobileFrame  # for type hinting

if TYPE_CHECKING:
    # NOTE: Used in documentation
    from .._analysis.flow_analyser import FlowAnalyser


class FrameBlastingFlow(Flow):
    """Flow generating and analyzing stateless traffic, mostly UDP."""

    __slots__ = (
        '_tx_stream_controller',
        '_stream',
        '_stream_status_data',
        '_stream_frame_count_data',
        '_stream_data_gatherer',
        '_frame_rate',
        '_number_of_frames',
        '_initial_time_to_wait',
        '_imix',
        '_frame_list',
        '_frame_content',
    )

    _CONFIG_ELEMENTS = Flow._CONFIG_ELEMENTS + (
        'frame_rate',
        'number_of_frames',
        'initial_time_to_wait',
    )

    _stream_data_gatherer_class = StreamFrameCountDataGatherer

    def __init__(
        self,
        source: Union[Port, Endpoint],
        destination: Union[Port, Endpoint],
        name: Optional[str] = None,
        bitrate: Optional[float] = None,  # [bps]
        frame_rate: Optional[float] = None,  # [fps]
        number_of_frames: Optional[int] = None,
        duration: Optional[Union[timedelta, float, int]] = None,  # [seconds]
        initial_time_to_wait: Optional[Union[timedelta, float,
                                             int]] = None,  # [seconds]
        frame_list: Optional[Union[Sequence[Frame],
                                   Sequence[MobileFrame]]] = None,
        imix: Optional[Imix] = None,
        **kwargs
    ) -> None:
        """Create a Frame Blasting flow.

        :param source: Sending endpoint of the data stream
        :type source: Union[Port, Endpoint]
        :param destination: Receiving endpoint of the data stream
        :type destination: Union[Port, Endpoint]
        :param name: Name of this Flow, defaults to auto-generated name
           when set to ``None``.
        :type name: str, optional
        :param bitrate: Rate at which the bits are transmitted
           (in bit per second). Excludes the VLAN tag bytes
           (*when applicable*), mutual exclusive with ``frame_rate``,
           defaults to None.
        :type bitrate: float, optional
        :param frame_rate: Rate at which the frames are transmitted
           (in frames per second), mutual exclusive with ``bitrate``,
           defaults to :const:`DEFAULT_FRAME_RATE` when ``bitrate``
           is not provided.
        :type frame_rate: float, optional
        :param number_of_frames: Number of frames to transmit,
           defaults to :const:`DEFAULT_NUMBER_OF_FRAMES`
        :type number_of_frames: int, optional
        :param duration: Duration of the flow in seconds,
           defaults to None (use number_of_frames instead)
        :type duration: Union[timedelta, float, int], optional
        :param initial_time_to_wait: Initial time to wait to start the flow.
           In seconds, defaults to None (start immediately)
        :type initial_time_to_wait: Union[timedelta, float, int], optional
        :param frame_list: List of frames to transmit,
           mutual exclusive with ``imix``, defaults to None
        :type frame_list: Sequence[Frame], optional
        :param imix: Imix definition of frames to transmit,
           mutual exclusive with ``frame_list``, defaults to None
        :type imix: Imix, optional
        :raises FeatureNotSupported:
           When an unsupported source endpoint type is given.
        :raises ConflictingInput: When both ``frame_rate`` and ``bitrate`` are
           given.
        :raises ConflictingInput: When both ``imix`` and ``frame_list``
           are given or when none of both is given.
        """
        super().__init__(source, destination, name=name, **kwargs)

        if isinstance(self._source, Endpoint):
            self._tx_stream_controller = EndpointTxStreamController
        elif isinstance(self._source, Port):
            self._tx_stream_controller = PortTxStreamController
        else:
            raise FeatureNotSupported(
                'Unsupported source endpoint'
                f' type: {type(source).__name__!r}'
            )
        self._stream: Union[TxStream, TxStreamMobile]  # for typedef only

        self._frame_rate = frame_rate

        self._imix = imix

        if self._imix and frame_list:
            raise ConflictingInput(
                f'Flow {self._name!r}: Please provide'
                ' either IMIX or frame list but not both.'
            )
        if self._imix:
            frame_list = self._imix._generate(self._source)

        # Calculate average frame size
        frame_sizes = (frame.length for frame in frame_list)
        avg_frame_size = mean(frame_sizes)  # [Bytes]

        if bitrate and frame_rate:
            raise ConflictingInput(
                f'Flow {self._name!r}: Please provide'
                ' either bitrate or frame rate but not both.'
            )

        # Convert bitrate to frame rate
        if bitrate:
            self._frame_rate = (bitrate / 8) / avg_frame_size

        if not self._frame_rate:
            self._frame_rate = DEFAULT_FRAME_RATE

        if duration is not None:
            if isinstance(duration, timedelta):
                # Convert to float
                duration = duration.total_seconds()
            # else:
            #     # Already float/int:
            #     duration = duration or 0
            self._number_of_frames = int(duration * self._frame_rate)
        elif number_of_frames is not None:
            self._number_of_frames = number_of_frames
        else:
            self._number_of_frames = DEFAULT_NUMBER_OF_FRAMES

        if isinstance(initial_time_to_wait, (float, int)):
            # Convert to timedelta
            self._initial_time_to_wait = timedelta(
                seconds=initial_time_to_wait
            )
        else:
            # Either already timedelta or None:
            # Default to 0s
            self._initial_time_to_wait = initial_time_to_wait or timedelta()

        self._stream_status_data: Optional[StreamStatusData] = None
        self._stream_frame_count_data: Optional[FrameCountData] = None
        self._stream_data_gatherer: Optional[StreamDataGatherer] = None

        if isinstance(self._source, Endpoint):
            src_dest_udp_set = {
                (frame.udp_src, frame.udp_dest)
                for frame in frame_list
            }
            if len(src_dest_udp_set) > 1:
                raise FeatureNotSupported(
                    'Multiple UDP source/destination port combinations'
                    ' when using different frames is not supported yet'
                )

        self._frame_list: Union[List[Frame], List[MobileFrame]] = frame_list
        self._frame_content = []

    def require_stream_data_gatherer(self) -> None:
        """
        Make sure that the stream data gatherer is available for testing.

        Should be called by the :class:`FlowAnalyser` or the user *before*
        starting a test when he needs ByteBlower stream (packet count) data.
        """
        if self._stream_data_gatherer is None:
            self._stream_status_data = StreamStatusData()
            self._stream_frame_count_data = FrameCountData()
            self._stream_data_gatherer = self._stream_data_gatherer_class(
                self._stream_status_data, self._stream_frame_count_data, self
            )

    @property
    def stream_frame_count_data(self) -> Optional[FrameCountData]:
        """Get the frame count data from the stream analysis.

        .. note::
           Initially created by calling
           :meth:`require_stream_data_gatherer()`

        :return: Frame count data
        :rtype: FrameCountData
        """
        return self._stream_frame_count_data

    @property
    def frame_rate(self) -> float:
        return self._frame_rate

    @property
    def frame_list(self) -> Sequence[Frame]:
        return self._frame_list

    @property
    def number_of_frames(self) -> int:
        return self._number_of_frames

    @property
    def duration(self) -> timedelta:
        """Returns the duration of the FrameBlasting flow.

        :raises InfiniteDuration: If the flow duration is configured
           to run forever.
        :return: duration of the flow.
        :rtype: timedelta
        """
        if self._number_of_frames == INFINITE_NUMBER_OF_FRAMES:
            raise InfiniteDuration()
        duration = self._number_of_frames / self._frame_rate
        return timedelta(seconds=duration)

    @property
    def initial_time_to_wait(self) -> timedelta:
        """Return the time to wait before the flow starts."""
        return self._initial_time_to_wait

    @property
    def finished(self) -> bool:
        """Returns True if the flow is done."""
        # We added an extra check whether the "analysers finished"
        # because we also need to make sure that the analysers configured
        # on BB endpoint are done processing data.
        return self._tx_stream_controller.finished(
            self._source, self._stream
        ) and self._analysers_finished()

    def _analysers_finished(self) -> bool:
        """Return whether all flow analysers finished processing data."""
        for analyser in self._analysers:
            if not analyser.finished:
                return False
        return True

    @property
    def runtime_error_info(self) -> RuntimeErrorInfo:
        if self._stream_status_data is not None:
            error_status = self._stream_status_data.error_status
            error_source = self._stream_status_data.error_source
            if (error_status is not None
                    and error_status != StreamErrorStatus.NONE
                    or error_source is not None
                    and error_source != StreamErrorSource.NONE):
                return {
                    'status': error_status,
                    'source': error_source,
                }
        return {}

    # def add_frame(self, frame: Frame) -> None:
    #     frame._add(self._source, self._destination, self._stream)
    #     self._frame_list.append(frame)

    def prepare_configure(self) -> None:
        """Prepare Frames and perform proper address resolving."""
        for frame in self._frame_list:
            self._frame_content.append(
                frame.build_frame_content(self._source, self._destination)
            )

        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.prepare_configure()

        super().prepare_configure()

    def initialize(self) -> None:
        """Create the stream and add frames."""
        self._stream = self._tx_stream_controller.create(self._source)

        if self._initial_time_to_wait:
            self._stream.InitialTimeToWaitSet(
                int(self._initial_time_to_wait.total_seconds() * 1e9)
            )

        for frame, frame_content in zip(self._frame_list, self._frame_content):
            frame.add(frame_content, self._stream)

        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.initialize()

        super().initialize()

    def prepare_start(
        self,
        maximum_run_time: Optional[timedelta] = None
    ) -> Iterable[SynchronizedExecutable]:
        if maximum_run_time is not None:
            # If initial_time_to_wait is set, subtract this wait time
            # from the scenario duration
            duration: timedelta = maximum_run_time - self.initial_time_to_wait
            number_of_frames = int(duration.total_seconds() * self._frame_rate)
            if (self._number_of_frames == INFINITE_NUMBER_OF_FRAMES
                    or number_of_frames < self._number_of_frames):
                self._number_of_frames = number_of_frames

        self._stream.InterFrameGapSet(int(1e9 / self._frame_rate))
        self._stream.NumberOfFramesSet(self._number_of_frames)

        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.prepare_start(
                maximum_run_time=maximum_run_time
            )

        yield from super().prepare_start(maximum_run_time=maximum_run_time)
        yield from (
            SynchronizedExecutable(stream) for stream in
            self._tx_stream_controller.prepare_start(self._stream)
        )

    def process(self) -> None:
        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.process()
        super().process()

    def updatestats(self) -> None:
        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.updatestats()
        super().updatestats()

    def wait_until_finished(
        self, wait_for_finish: timedelta, result_timeout: timedelta
    ) -> None:
        """Wait until the flow finished traffic generation and processing.

        :param wait_for_finish: Time to wait for sessions closing
           and final packets being received.
        :type wait_for_finish: timedelta
        :param result_timeout: Time to wait for Endpoints to finalize
           and return their results to the Meeting Point.

        .. versionadded:: 1.2.0
           Added for ByteBlower Endpoint support.

        :type result_timeout: timedelta
        """
        finish_time = datetime.now() + wait_for_finish
        timeout = datetime.now() + result_timeout
        while datetime.now() <= finish_time:
            if self.finished:
                logging.debug(
                    'Endpoint %r finished transmission in time.'
                    ' Good job! 💪', self.source.name
                )
                return
            sleep(0.1)
        logging.warning(
            'Endpoint %r did not finish transmission in time.'
            ' Waiting for some extra time.', self.source.name
        )
        while datetime.now() <= timeout:
            if self.finished:
                logging.debug(
                    'Endpoint %r finished transmission after finish wait time.'
                    ' Could have done better. 😕', self.source.name
                )
                return
            sleep(0.5)
        logging.warning(
            'Endpoint %r did not finish transmission before timeout.'
            ' Results might not be available.', self.source.name
        )

    def stop(self) -> None:
        self._tx_stream_controller.stop(self._stream)
        super().stop()

    @property
    def error_status(
        self
    ) -> Tuple[Optional[StreamErrorStatus], Optional[StreamErrorSource]]:
        """Get the error status for this flow.

        :return: Error status and source of the transmit stream
        :rtype: Tuple[Optional[StreamErrorStatus], Optional[StreamErrorSource]]

        :meta private:
        """
        return self._tx_stream_controller.error_status(self._stream)

    def analyse(self) -> None:
        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.summarize()
        super().analyse()

    def release(self) -> None:
        super().release()
        if self._stream_data_gatherer is not None:
            self._stream_data_gatherer.release()
        try:
            bb_stream = self._stream
            del self._stream
        except AttributeError:
            pass
        else:
            for frame in self._frame_list:
                frame.release(bb_stream)
            self._tx_stream_controller.release(self._source, bb_stream)
