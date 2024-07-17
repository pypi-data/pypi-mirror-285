import logging
from datetime import timedelta  # for type hinting
from typing import Optional, Sequence, Type, Union  # for type hinting

import pandas
from byteblowerll.byteblower import (  # for type hinting
    ByteBlowerAPIException,
    DomainError,
    FrameTagTx,
    LatencyBasic,
    LatencyBasicMobile,
    LatencyBasicResultData,
    LatencyBasicResultHistory,
    LatencyDistribution,
    LatencyDistributionMobile,
    LatencyDistributionResultSnapshot,
    TriggerBasic,
    TriggerBasicMobile,
    TriggerBasicResultData,
    TriggerBasicResultHistory,
)
from pandas import Timestamp  # for type hinting

from ..._endpoint.endpoint import Endpoint
from ..._endpoint.helpers import vlan_header_length
from ..._endpoint.port import Port
from ..._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting
from ...exceptions import FeatureNotSupported
from ..storage.frame_count import FrameCountData  # for type hinting
from ..storage.trigger import (  # for type hinting
    LatencyData,
    LatencyDistributionData,
)
from ._filter import EndpointFilterBuilder, FrameFilterBuilder
from ._rx_trigger_controller import EndpointFilterContent  # for type hinting
from ._rx_trigger_controller import PortFilterContent  # for type hinting
from ._rx_trigger_controller import (
    EndpointRxTriggerController,
    PortRxTriggerController,
)
from .data_gatherer import DataGatherer


class BaseFrameCountDataGatherer(DataGatherer):
    """Base class for data gathering for latency and frame count over time."""

    __slots__ = (
        '_framecount_data',
        '_flow',
        '_filter_builder',
        '_rx_trigger_controller',
        '_trigger',
        '_filter_content',
        '_rx_vlan_header_size',
        '_rx_result',
    )

    def __init__(
        self,
        framecount_data: FrameCountData,
        flow: FrameBlastingFlow,
        frame_filter_builder: Type = FrameFilterBuilder,
        endpoint_filter_builder: Type = EndpointFilterBuilder
    ) -> None:
        super().__init__()

        self._framecount_data = framecount_data
        self._flow = flow

        destination = self._flow.destination
        if isinstance(destination, Endpoint):
            self._filter_builder = endpoint_filter_builder
            self._rx_trigger_controller = EndpointRxTriggerController
        elif isinstance(destination, Port):
            self._filter_builder = frame_filter_builder
            self._rx_trigger_controller = PortRxTriggerController
        else:
            raise FeatureNotSupported(
                'Unsupported source endpoint'
                f' type: {type(destination).__name__!r}'
            )
        self._trigger: Union[TriggerBasic,
                             TriggerBasicMobile]  # for typedef only
        self._filter_content = Union[PortFilterContent,
                                     EndpointFilterContent]  # for typedef only

        self._rx_vlan_header_size: int = 0
        self._rx_result: TriggerBasicResultHistory  # for typedef only

    def prepare_configure(self) -> None:
        self._filter_content = self._rx_trigger_controller.prepare_configure(
            self._flow,
            filter_builder=self._filter_builder,
        )

    def initialize(self) -> None:
        self._trigger = self._rx_trigger_controller.create_basic(
            self._flow.destination
        )
        self._rx_result = self._trigger.ResultHistoryGet()
        self._rx_trigger_controller.initialize(
            self._trigger,
            self._flow,
            self._filter_content,
        )
        del self._filter_content

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        self._rx_trigger_controller.prepare_start(
            self._trigger,
            duration=maximum_run_time,
        )

        # Clear all results: Reset totals & clear result history
        self._trigger.ResultClear()
        self._rx_result.Clear()
        # NOTE: We calculate the VLAN header sizes at start of the Flow,
        #       since this is the point where the filter was created.
        self._rx_vlan_header_size = vlan_header_length(self._flow.destination)

    def updatestats(self) -> None:
        # Refresh the history
        self._rx_result.Refresh()

        # Add all the history snapshots
        self._persist_history_snapshots()

        # Clear the history
        self._rx_result.Clear()

    @property
    def finished(self) -> bool:
        return self._rx_trigger_controller.finished(self._flow.destination)

    def summarize(self) -> None:
        # Refresh the history
        self._rx_result.Refresh()

        # Add remaining history snapshots
        self._persist_history_snapshots()

        cumulative_snapshot: TriggerBasicResultData = (
            self._rx_result.CumulativeLatestGet()
        )
        total_rx_bytes = cumulative_snapshot.ByteCountGet()
        total_rx_packets = cumulative_snapshot.PacketCountGet()
        if total_rx_packets:
            ts_rx_first_ns = cumulative_snapshot.TimestampFirstGet()
            ts_rx_last_ns = cumulative_snapshot.TimestampLastGet()
        else:
            ts_rx_first_ns = None
            ts_rx_last_ns = None

        self._framecount_data._total_bytes = total_rx_bytes
        self._framecount_data._total_vlan_bytes = (
            total_rx_packets * self._rx_vlan_header_size
        )
        self._framecount_data._total_packets = total_rx_packets
        self._framecount_data._timestamp_first = (
            pandas.to_datetime(ts_rx_first_ns, unit='ns', utc=True)
        )
        self._framecount_data._timestamp_last = (
            pandas.to_datetime(ts_rx_last_ns, unit='ns', utc=True)
        )

        # Persist latest/final snapshot
        timestamp_ns: int = cumulative_snapshot.TimestampGet()
        interval_snapshot: TriggerBasicResultData = (
            self._rx_result.IntervalGetByTime(timestamp_ns)
        )
        timestamp = pandas.to_datetime(timestamp_ns, unit='ns', utc=True)
        self._persist_history_snapshot(
            timestamp,
            cumulative_snapshot,
            interval_snapshot,
        )

    def release(self) -> None:
        super().release()
        try:
            del self._rx_result
        except AttributeError:
            pass
        try:
            trigger = self._trigger
            del self._trigger
        except AttributeError:
            pass
        else:
            self._rx_trigger_controller.release_basic(
                self._flow.destination, trigger
            )

    def _persist_history_snapshots(self) -> None:
        """Add all the history interval results."""
        cumulative_snapshot: TriggerBasicResultData = None  # for type hinting
        for cumulative_snapshot in self._rx_result.CumulativeGet()[:-1]:
            try:
                timestamp_ns: int = cumulative_snapshot.TimestampGet()
                interval_snapshot: TriggerBasicResultData = (
                    self._rx_result.IntervalGetByTime(timestamp_ns)
                )
                timestamp = pandas.to_datetime(
                    timestamp_ns, unit='ns', utc=True
                )
                self._persist_history_snapshot(
                    timestamp,
                    cumulative_snapshot,
                    interval_snapshot,
                )
            except ByteBlowerAPIException as error:
                logging.warning(
                    "Error during processing of RX frame count stats: %s",
                    error.getMessage(),
                    exc_info=True,
                )

    def _persist_history_snapshot(
        self, timestamp: Timestamp,
        cumulative_snapshot: TriggerBasicResultData,
        interval_snapshot: TriggerBasicResultData
    ) -> None:
        """Add a history snapshot."""
        self._framecount_data._over_time.loc[timestamp] = [
            cumulative_snapshot.IntervalDurationGet(),
            cumulative_snapshot.PacketCountGet(),
            cumulative_snapshot.ByteCountGet(),
            interval_snapshot.IntervalDurationGet(),
            interval_snapshot.PacketCountGet(),
            interval_snapshot.ByteCountGet(),
        ]


class FrameCountDataGatherer(BaseFrameCountDataGatherer):
    """Data gathering for frame count over time."""

    __slots__ = ()

    def __init__(
        self,
        framecount_data: FrameCountData,
        flow: FrameBlastingFlow,
    ) -> None:
        super().__init__(framecount_data, flow)


class BaseLatencyFrameCountDataGatherer(DataGatherer):
    """Base class for data gathering for latency and frame count over time."""

    __slots__ = (
        '_framecount_data',
        '_latency_data',
        '_flow',
        '_filter_builder',
        '_rx_trigger_controller',
        '_trigger',
        '_filter_content',
        '_rx_vlan_header_size',
        '_rx_result',
    )

    def __init__(
        self,
        framecount_data: FrameCountData,
        latency_data: LatencyData,
        flow: FrameBlastingFlow,
        frame_filter_builder: Type = FrameFilterBuilder,
        endpoint_filter_builder: Type = EndpointFilterBuilder
    ) -> None:
        super().__init__()

        self._framecount_data = framecount_data
        self._latency_data = latency_data
        self._flow = flow
        destination = self._flow.destination
        if isinstance(destination, Endpoint):
            self._filter_builder = endpoint_filter_builder
            self._rx_trigger_controller = EndpointRxTriggerController
        elif isinstance(destination, Port):
            self._filter_builder = frame_filter_builder
            self._rx_trigger_controller = PortRxTriggerController
        else:
            raise FeatureNotSupported(
                'Unsupported source endpoint'
                f' type: {type(destination).__name__!r}'
            )
        self._trigger: Union[LatencyBasic,
                             LatencyBasicMobile]  # for typedef only
        self._filter_content = Union[PortFilterContent,
                                     EndpointFilterContent]  # for typedef only

        self._rx_vlan_header_size: int = 0
        self._rx_result: LatencyBasicResultHistory  # for typedef only

    def prepare_configure(self) -> None:
        self._filter_content = self._rx_trigger_controller.prepare_configure(
            self._flow,
            filter_builder=self._filter_builder,
        )

    def initialize(self) -> None:
        self._trigger = self._rx_trigger_controller.create_basic_latency(
            self._flow.destination
        )
        self._rx_result = self._trigger.ResultHistoryGet()
        self._rx_trigger_controller.initialize(
            self._trigger,
            self._flow,
            self._filter_content,
        )
        del self._filter_content

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        self._rx_trigger_controller.prepare_start(
            self._trigger,
            duration=maximum_run_time,
        )

        # Set the time tag format and metrics
        # NOTE - Using the first frame
        #      - All frames are generated on the same server,
        #        so they should have the same format.
        #      - All frames "should have" been generated the same way,
        #        using the same tags, so should have the same metrics too.
        # TODO - We should do some sanity check on all Frames
        #      * whether the format and metrics are identical.
        frame_list = self._flow.frame_list
        if len(frame_list) > 0:
            first_bb_frame = frame_list[0]._frame
            tx_frame_tag: FrameTagTx = first_bb_frame.FrameTagTimeGet()
            self._trigger.FrameTagSet(tx_frame_tag)

        # Clear all results: Reset totals & clear result history
        self._trigger.ResultClear()
        self._rx_result.Clear()

        # NOTE: We calculate the VLAN header sizes at start of the Flow,
        #       since this is the point where the filter was created.
        self._rx_vlan_header_size = vlan_header_length(self._flow.destination)

    def updatestats(self) -> None:
        # Refresh the history
        self._rx_result.Refresh()

        # Add all the history snapshots
        self._persist_history_snapshots()

        # Clear the history
        self._rx_result.Clear()

    @property
    def finished(self) -> bool:
        return self._rx_trigger_controller.finished(self._flow.destination)

    def summarize(self) -> None:
        # Refresh the history
        self._rx_result.Refresh()

        # Add remaining history snapshots
        self._persist_history_snapshots()

        cumulative_snapshot: LatencyBasicResultData = (
            self._rx_result.CumulativeLatestGet()
        )

        total_rx_bytes = cumulative_snapshot.ByteCountGet()
        total_rx_packets = cumulative_snapshot.PacketCountGet()
        if total_rx_packets:
            ts_rx_first_ns = cumulative_snapshot.TimestampFirstGet()
            ts_rx_last_ns = cumulative_snapshot.TimestampLastGet()
        else:
            ts_rx_first_ns = None
            ts_rx_last_ns = None

        self._framecount_data._total_bytes = total_rx_bytes
        self._framecount_data._total_vlan_bytes = (
            total_rx_packets * self._rx_vlan_header_size
        )
        self._framecount_data._total_packets = total_rx_packets
        self._framecount_data._timestamp_first = (
            pandas.to_datetime(ts_rx_first_ns, unit='ns', utc=True)
        )
        self._framecount_data._timestamp_last = (
            pandas.to_datetime(ts_rx_last_ns, unit='ns', utc=True)
        )

        try:
            final_packet_count_valid = (
                cumulative_snapshot.PacketCountValidGet()
            )
        except DomainError as error:
            # NOTE: Issue with API/MeetingPoint < 2.21
            final_packet_count_valid = 0
            logging.warning(
                'Flow %r: Unable to get valid packet count: %r',
                self._flow.name,
                error.getMessage(),
                exc_info=True,
            )
        try:
            final_packet_count_invalid = (
                cumulative_snapshot.PacketCountInvalidGet()
            )
        except DomainError as error:
            # NOTE: Issue with API/MeetingPoint < 2.21
            final_packet_count_invalid = 0
            logging.warning(
                'Flow %r: Unable to get invalid packet count: %r',
                self._flow.name,
                error.getMessage(),
                exc_info=True,
            )
        self._latency_data._final_packet_count_valid = (
            final_packet_count_valid
        )
        self._latency_data._final_packet_count_invalid = (
            final_packet_count_invalid
        )
        if final_packet_count_valid:
            # NOTE - If we did not receive any data (with valid latency tag),
            #        we will not have latency values.
            self._latency_data._final_min_latency = (
                cumulative_snapshot.LatencyMinimumGet() / 1e6
            )
            self._latency_data._final_max_latency = (
                cumulative_snapshot.LatencyMaximumGet() / 1e6
            )
            self._latency_data._final_avg_latency = (
                cumulative_snapshot.LatencyAverageGet() / 1e6
            )
            self._latency_data._final_avg_jitter = (
                cumulative_snapshot.JitterGet() / 1e6
            )

        # Persist latest/final snapshot
        timestamp_ns: int = cumulative_snapshot.TimestampGet()
        interval_snapshot: LatencyBasicResultData = (
            self._rx_result.IntervalGetByTime(timestamp_ns)
        )
        timestamp = pandas.to_datetime(timestamp_ns, unit='ns', utc=True)
        self._persist_history_snapshot(
            timestamp,
            cumulative_snapshot,
            interval_snapshot,
        )

    def release(self) -> None:
        super().release()
        try:
            del self._rx_result
        except AttributeError:
            pass
        try:
            trigger = self._trigger
            del self._trigger
        except AttributeError:
            pass
        else:
            self._rx_trigger_controller.release_basic_latency(
                self._flow.destination, trigger
            )

    def _persist_history_snapshots(self) -> None:
        """Add all the history interval results."""
        cumulative_snapshot: LatencyBasicResultData
        for cumulative_snapshot in self._rx_result.CumulativeGet()[:-1]:
            try:
                timestamp_ns: int = cumulative_snapshot.TimestampGet()
                interval_snapshot: LatencyBasicResultData = (
                    self._rx_result.IntervalGetByTime(timestamp_ns)
                )

                timestamp = pandas.to_datetime(
                    timestamp_ns, unit='ns', utc=True
                )
                self._persist_history_snapshot(
                    timestamp,
                    cumulative_snapshot,
                    interval_snapshot,
                )
            except ByteBlowerAPIException as error:
                logging.warning(
                    "Error during processing of RX latency stats: %s",
                    error.getMessage(),
                    exc_info=True,
                )

    def _persist_history_snapshot(
        self, timestamp: Timestamp,
        cumulative_snapshot: LatencyBasicResultData,
        interval_snapshot: LatencyBasicResultData
    ) -> None:
        """Add a history snapshot."""
        self._framecount_data.over_time.loc[timestamp] = [
            cumulative_snapshot.IntervalDurationGet(),
            cumulative_snapshot.PacketCountGet(),
            cumulative_snapshot.ByteCountGet(),
            interval_snapshot.IntervalDurationGet(),
            interval_snapshot.PacketCountGet(),
            interval_snapshot.ByteCountGet(),
        ]
        if interval_snapshot.PacketCountGet():
            # NOTE - If we did not receive any data,
            #        we will not have latency values.
            self._latency_data.df_latency.loc[timestamp] = [
                interval_snapshot.LatencyMinimumGet() / 1e6,
                interval_snapshot.LatencyMaximumGet() / 1e6,
                interval_snapshot.LatencyAverageGet() / 1e6,
                interval_snapshot.JitterGet() / 1e6,
            ]


class LatencyFrameCountDataGatherer(BaseLatencyFrameCountDataGatherer):
    """Data gathering for latency and frame count over time."""

    __slots__ = ()

    def __init__(
        self, framecount_data: FrameCountData, latency_data: LatencyData,
        flow: FrameBlastingFlow
    ) -> None:
        super().__init__(framecount_data, latency_data, flow)


class BaseLatencyCDFFrameCountDataGatherer(DataGatherer):
    """Base class for data gathering for latency histogram and frame count."""

    __slots__ = (
        '_framecount_data',
        '_latency_distribution_data',
        '_flow',
        '_filter_builder',
        '_rx_trigger_controller',
        '_trigger',
        '_filter_content',
        '_rx_vlan_header_size',
        '_max_threshold_latency',
    )

    def __init__(
        self,
        framecount_data: FrameCountData,
        latency_distribution_data: LatencyDistributionData,
        max_threshold_latency: float,
        flow: FrameBlastingFlow,
        frame_filter_builder: Type = FrameFilterBuilder,
        endpoint_filter_builder: Type = EndpointFilterBuilder
    ) -> None:
        super().__init__()

        self._framecount_data = framecount_data
        self._latency_distribution_data = latency_distribution_data
        self._flow = flow

        destination = self._flow.destination
        if isinstance(destination, Endpoint):
            self._filter_builder = endpoint_filter_builder
            self._rx_trigger_controller = EndpointRxTriggerController
        elif isinstance(destination, Port):
            self._filter_builder = frame_filter_builder
            self._rx_trigger_controller = PortRxTriggerController
        else:
            raise FeatureNotSupported(
                'Unsupported source endpoint'
                f' type: {type(destination).__name__!r}'
            )
        self._trigger: Union[LatencyDistribution,
                             LatencyDistributionMobile]  # for typedef only
        self._filter_content = Union[PortFilterContent,
                                     EndpointFilterContent]  # for typedef only

        self._rx_vlan_header_size: int = 0

        self._max_threshold_latency = max_threshold_latency

    def prepare_configure(self) -> None:
        self._filter_content = self._rx_trigger_controller.prepare_configure(
            self._flow,
            filter_builder=self._filter_builder,
        )

    def initialize(self) -> None:
        self._trigger = (
            self._rx_trigger_controller.create_latency_distribution(
                self._flow.destination
            )
        )
        # TODO: Avoid hard-coded value(s).
        #     ! Also update LatencyCDFAnalyser accordingly !
        self._trigger.RangeSet(0, int(50 * self._max_threshold_latency * 1e6))
        self._rx_trigger_controller.initialize(
            self._trigger,
            self._flow,
            self._filter_content,
        )
        del self._filter_content

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        self._rx_trigger_controller.prepare_start(
            self._trigger,
            duration=maximum_run_time,
        )

        # Set the time tag format and metrics
        # NOTE - Using the first frame
        #      - All frames are generated on the same server,
        #        so they should have the same format.
        #      - All frames "should have" been generated the same way,
        #        using the same tags, so should have the same metrics too.
        # TODO - We should do some sanity check on all Frames
        #      * whether the format and metrics are identical.
        frame_list = self._flow.frame_list
        if len(frame_list) > 0:
            first_bb_frame = frame_list[0]._frame
            tx_frame_tag: FrameTagTx = first_bb_frame.FrameTagTimeGet()
            self._trigger.FrameTagSet(tx_frame_tag)

        # Clear all results: Reset totals & clear result history
        self._trigger.ResultClear()

        # NOTE: We calculate the VLAN header sizes at start of the Flow,
        #       since this is the point where the filter was created.
        self._rx_vlan_header_size = vlan_header_length(self._flow.destination)

    @property
    def finished(self) -> bool:
        return self._rx_trigger_controller.finished(self._flow.destination)

    def summarize(self) -> None:
        # Refresh the history
        self._trigger.Refresh()

        cumulative_snapshot: LatencyDistributionResultSnapshot = (
            self._trigger.ResultGet()
        )
        total_rx_bytes = cumulative_snapshot.ByteCountGet()
        total_rx_packets = cumulative_snapshot.PacketCountGet()
        if total_rx_packets:
            ts_rx_first_ns = cumulative_snapshot.TimestampFirstGet()
            ts_rx_last_ns = cumulative_snapshot.TimestampLastGet()
        else:
            ts_rx_first_ns = None
            ts_rx_last_ns = None

        # Frame count analysis
        self._framecount_data._total_bytes = total_rx_bytes
        self._framecount_data._total_vlan_bytes = (
            total_rx_packets * self._rx_vlan_header_size
        )
        # TODO - Do we need the "valid" packet count here ?
        #      ? Where does ``ByteCountGet()`` relate to ?
        self._framecount_data._total_packets = total_rx_packets
        self._framecount_data._timestamp_first = (
            pandas.to_datetime(ts_rx_first_ns, unit='ns', utc=True)
        )
        self._framecount_data._timestamp_last = (
            pandas.to_datetime(ts_rx_last_ns, unit='ns', utc=True)
        )

        # Latency (distribution) analysis
        try:
            final_packet_count_valid = (
                cumulative_snapshot.PacketCountValidGet()
            )
        except DomainError as error:
            # NOTE: Issue with API/MeetingPoint < 2.21
            final_packet_count_valid = 0
            logging.warning(
                'Flow %r: Unable to get valid packet count: %r',
                self._flow.name,
                error.getMessage(),
                exc_info=True,
            )
        try:
            final_packet_count_invalid = (
                cumulative_snapshot.PacketCountInvalidGet()
            )
        except DomainError as error:
            # NOTE: Issue with API/MeetingPoint < 2.21
            final_packet_count_invalid = 0
            logging.warning(
                'Flow %r: Unable to get invalid packet count: %r',
                self._flow.name,
                error.getMessage(),
                exc_info=True,
            )
        self._latency_distribution_data._final_packet_count_valid = (
            final_packet_count_valid
        )
        self._latency_distribution_data._final_packet_count_invalid = (
            final_packet_count_invalid
        )
        self._latency_distribution_data._final_packet_count_below_min = (
            cumulative_snapshot.PacketCountBelowMinimumGet()
        )
        self._latency_distribution_data._final_packet_count_above_max = (
            cumulative_snapshot.PacketCountAboveMaximumGet()
        )
        if final_packet_count_valid:
            # NOTE - If we did not receive any data (with valid latency tag),
            #        we will not have latency values.
            self._latency_distribution_data._final_min_latency = (
                cumulative_snapshot.LatencyMinimumGet() / 1e6
            )
            self._latency_distribution_data._final_max_latency = (
                cumulative_snapshot.LatencyMaximumGet() / 1e6
            )
            self._latency_distribution_data._final_avg_latency = (
                cumulative_snapshot.LatencyAverageGet() / 1e6
            )
            self._latency_distribution_data._final_avg_jitter = (
                cumulative_snapshot.JitterGet() / 1e6
            )

        bucket_count = cumulative_snapshot.BucketCountGet()
        packet_count_buckets: Sequence[int] = (
            cumulative_snapshot.PacketCountBucketsGet()
        )
        logging.debug(
            'Flow: %r: Got %r Packet count buckets', self._flow.name,
            bucket_count
        )
        # XXX - Not sure if we can directly use ``packet_count_buckets``.
        try:
            self._latency_distribution_data._packet_count_buckets = [
                packet_count_buckets[x] for x in range(0, bucket_count)
            ]
        except IndexError:
            # NOTE: Issue in Endpoint when no packets received at all
            self._latency_distribution_data._packet_count_buckets = []
        self._latency_distribution_data._bucket_width = (
            cumulative_snapshot.BucketWidthGet()
        )

    def release(self) -> None:
        super().release()
        try:
            trigger = self._trigger
            del self._trigger
        except AttributeError:
            pass
        else:
            self._rx_trigger_controller.release_latency_distribution(
                self._flow.destination, trigger
            )


class LatencyCDFFrameCountDataGatherer(BaseLatencyCDFFrameCountDataGatherer):
    """Data gathering for latency histogram, CDF and frame count."""

    __slots__ = ()

    def __init__(
        self,
        framecount_data: FrameCountData,
        latency_distribution_data: LatencyDistributionData,
        max_threshold_latency: float,
        flow: FrameBlastingFlow,
    ) -> None:
        super().__init__(
            framecount_data, latency_distribution_data, max_threshold_latency,
            flow
        )
