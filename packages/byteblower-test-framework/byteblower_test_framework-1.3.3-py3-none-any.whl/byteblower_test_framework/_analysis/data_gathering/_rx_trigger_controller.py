"""
Behavior module for receiving triggers.

The RxTriggerControllers extract device-specific API calls
to behavior interfaces for the test framework.
"""
import logging
from datetime import timedelta  # for type hinting
from typing import Optional, Type, Union  # for type hinting

from byteblowerll.byteblower import (  # for type hinting
    LatencyBasic,
    LatencyBasicMobile,
    LatencyDistribution,
    LatencyDistributionMobile,
    TriggerBasic,
    TriggerBasicMobile,
)

from ..._endpoint.endpoint import Endpoint  # for type hinting
from ..._endpoint.port import Port  # for type hinting
from ..._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting
from ...exceptions import InvalidInput
from ._filter import EndpointFilterContent  # for type hinting
from ._filter import PortFilterContent  # for type hinting
from ._filter import EndpointFilterBuilder, FrameFilterBuilder


class PortRxTriggerController(object):

    @staticmethod
    def create_basic(port: Port) -> TriggerBasic:
        return port.bb_port.RxTriggerBasicAdd()

    @staticmethod
    def release_basic(port: Port, trigger: TriggerBasic) -> None:
        port.bb_port.RxTriggerBasicRemove(trigger)

    @staticmethod
    def create_basic_latency(port: Port) -> LatencyBasic:
        return port.bb_port.RxLatencyBasicAdd()

    @staticmethod
    def release_basic_latency(port: Port, trigger: LatencyBasic) -> None:
        port.bb_port.RxLatencyBasicRemove(trigger)

    @staticmethod
    def create_latency_distribution(port: Port) -> LatencyDistribution:
        return port.bb_port.RxLatencyDistributionAdd()

    @staticmethod
    def release_latency_distribution(
        port: Port, trigger: LatencyDistribution
    ) -> None:
        port.bb_port.RxLatencyDistributionRemove(trigger)

    @staticmethod
    def prepare_configure(
        flow: FrameBlastingFlow,
        filter_builder: Type[FrameFilterBuilder] = FrameFilterBuilder,
    ) -> PortFilterContent:
        """
        Prepare the filter for the trigger to receive the given flow's traffic.

        The returned filter content is based on the configuration of the flow.

        For ByteBlower port endpoints, filtering is done based on BPF filters.

        .. note::
           We take the ``filter_builder`` from the user.
           We can use a :class:`FrameFilterBuilder` hard-coded too, but this
           will allow to specify which filter builder the user likes to use.

        :param flow: Flow for which the filter content is prepared
        :type flow: FrameBlastingFlow
        :param filter_builder: User-provided builder for BPF filters,
           defaults to FrameFilterBuilder
        :type filter_builder: Type[FrameFilterBuilder]
        """
        return filter_builder.build_bpf_filter(flow)

    @staticmethod
    def initialize(
        trigger: Union[TriggerBasic, LatencyBasic, LatencyDistribution],
        flow: FrameBlastingFlow,
        filter_content: PortFilterContent,
    ) -> None:
        """Set the filter on the trigger to receive traffic of the given flow.

        The filter is based on the configuration of the flow.

        For ByteBlower port endpoints, filtering is done based on BPF filters.

        :param trigger: Trigger to set the filter on
        :type trigger: Union[TriggerBasic, LatencyBasic, LatencyDistribution]
        :param flow: Flow for which the filter was created for.
           Used for logging purposes.
        :type flow: FrameBlastingFlow
        :param filter_content: Content for configuring the filter, built
           by the filter builder in :meth:`prepare_configure`
        :type filter_content: PortFilterContent
        """
        logging.debug(
            'Flow: %r: Setting BPF filter to %r', flow.name, filter_content
        )
        trigger.FilterSet(filter_content)

    @staticmethod
    def prepare_start(
        trigger: Union[TriggerBasic, LatencyBasic, LatencyDistribution],  # pylint: disable=unused-argument
        duration: Optional[timedelta] = None,  # pylint: disable=unused-argument
    ) -> None:
        """Prepare the trigger to start processing.

        :param trigger: Trigger to prepare
        :type trigger: Union[TriggerBasic, LatencyBasic, LatencyDistribution]
        :param duration: Lifetime of the trigger, defaults to None
        :type duration: Optional[timedelta], optional
        """

    @staticmethod
    def finished(_port: Port) -> bool:
        """Return whether data gathering finished."""
        # Ports do not need extra time to process results.
        return True


class EndpointRxTriggerController(object):

    @staticmethod
    def create_basic(endpoint: Endpoint) -> TriggerBasicMobile:
        return endpoint.bb_endpoint.RxTriggerBasicAdd()

    @staticmethod
    def release_basic(endpoint: Endpoint, trigger: TriggerBasicMobile) -> None:
        endpoint.bb_endpoint.RxTriggerBasicRemove(trigger)

    @staticmethod
    def create_basic_latency(endpoint: Endpoint) -> LatencyBasicMobile:
        return endpoint.bb_endpoint.RxLatencyBasicAdd()

    @staticmethod
    def release_basic_latency(
        endpoint: Endpoint, trigger: LatencyBasicMobile
    ) -> None:
        endpoint.bb_endpoint.RxLatencyBasicRemove(trigger)

    @staticmethod
    def create_latency_distribution(
        endpoint: Endpoint
    ) -> LatencyDistributionMobile:
        return endpoint.bb_endpoint.RxLatencyDistributionAdd()

    @staticmethod
    def release_latency_distribution(
        endpoint: Endpoint, trigger: LatencyDistributionMobile
    ) -> None:
        endpoint.bb_endpoint.RxLatencyDistributionRemove(trigger)

    @staticmethod
    def prepare_configure(
        flow: FrameBlastingFlow,
        filter_builder: Type[EndpointFilterBuilder] = EndpointFilterBuilder,
    ) -> EndpointFilterContent:
        """
        Prepare the filter for the trigger to receive the given flow's traffic.

        The returned filter content is based on the configuration of the flow.

        For ByteBlower Endpoint endpoints, filtering is done based on IP source
        and UDP source/destination ports.

        .. note::
           We take the ``filter_builder`` from the user.
           We can use a :class:`EndpointFilterBuilder` hard-coded too, but this
           will allow to specify which filter builder the user likes to use.

        :param flow: Flow for which the filter content is prepared
        :type flow: FrameBlastingFlow
        :param filter_builder: User-provided builder for IP/UDP filters,
           defaults to EndpointFilterBuilder
        :type filter_builder: Type[EndpointFilterBuilder]
        """
        return filter_builder.build(flow)

    @staticmethod
    def initialize(
        trigger: Union[TriggerBasicMobile, LatencyBasicMobile,
                       LatencyDistributionMobile],
        flow: FrameBlastingFlow,  # pylint: disable=unused-argument
        filter_content: EndpointFilterContent,
    ) -> None:
        """Set the filter on the trigger to receive traffic of the given flow.

        :param trigger: Trigger to set the filter on
        :type trigger: Union[TriggerBasicMobile, LatencyBasicMobile,
            LatencyDistributionMobile]
        :param flow: Flow for which the filter was created for
           Used for logging purposes.
        :type flow: FrameBlastingFlow
        :param filter_content: Content for configuring the filter, built
           by the filter builder in :meth:`prepare_configure`
        :type filter_content: EndpointFilterContent
        """
        (
            ip_src_address,
            udp_src_port,
            udp_dest_port,
        ) = filter_content
        trigger.FilterSourceAddressSet(ip_src_address.compressed)
        trigger.FilterUdpSourcePortSet(udp_src_port)
        trigger.FilterUdpDestinationPortSet(udp_dest_port)

    @staticmethod
    def prepare_start(
        trigger: Union[TriggerBasicMobile, LatencyBasicMobile,
                       LatencyDistributionMobile],
        duration: Optional[timedelta] = None,
    ) -> None:
        """Prepare the trigger to start processing.

        :param trigger: Trigger to prepare
        :type trigger: Union[TriggerBasicMobile, LatencyBasicMobile,
           LatencyDistributionMobile]
        :param duration: Lifetime of the trigger, defaults to None
        :type duration: Optional[timedelta]
        """
        if duration is None:
            raise InvalidInput(
                'Duration is required to configure a Trigger'
                ' on a ByteBlower Endpoint'
            )
        trigger_duration = int(duration.total_seconds() * 1e9)
        logging.debug(
            'Setting the trigger duration to %r',
            trigger_duration,
        )
        trigger.DurationSet(trigger_duration)

    @staticmethod
    def finished(endpoint: Endpoint) -> bool:
        """Return whether data gathering finished."""
        return not endpoint.active
