"""Factory functions to create and initialize :class:`~Flow` instances."""
import logging
from typing import Any, Dict, Optional, Tuple, Union  # for type hinting

from byteblower_test_framework.analysis import (
    FrameLossAnalyser,
    HttpAnalyser,
    L4SHttpAnalyser,
    LatencyCDFFrameLossAnalyser,
    LatencyFrameLossAnalyser,
)
from byteblower_test_framework.endpoint import (  # for type hinting
    Endpoint,
    Port,
)
from byteblower_test_framework.exceptions import InvalidInput
from byteblower_test_framework.factory import create_frame
from byteblower_test_framework.report import Layer2Speed  # for type hinting
from byteblower_test_framework.traffic import Flow  # for type hinting
from byteblower_test_framework.traffic import (
    UDP_DYNAMIC_PORT_START,
    FrameBlastingFlow,
    HTTPFlow,
    string_array_to_int,
)

from .exceptions import MaximumUdpPortExceeded

__all__ = ('initialize_flow',)

FlowConfiguration = Dict[str, Any]


class FlowFactory(object):
    """Collection of factory methods for :class:`Flow` creation."""

    udp_dynamic_port = UDP_DYNAMIC_PORT_START

    @staticmethod
    def create_udp_flow(
        flow_config: FlowConfiguration,
        layer2_speed: Layer2Speed,
        source: Union[Port, Endpoint],
        destination: Union[Port, Endpoint],
    ) -> FrameBlastingFlow:
        """Create a UDP frame blasting flow.

        :param flow_config: Configuration parameters for the flow
        :type flow_config: FlowConfiguration
        :param layer2_speed: Layer 2 speed to report
        :type layer2_speed: Layer2Speed
        :param source: Transmitter of the data traffic
        :type source: Union[Port, Endpoint]
        :param destination: Receiver of the data traffic
        :type destination: Union[Port, Endpoint]
        :return: Newly generated flow
        :rtype: FrameBlastingFlow
        """
        # Parse arguments
        # NOTE - Create a copy before altering.
        #      * It is shared with other function (calls) !

        name = flow_config.pop("name", None)
        udp_src = flow_config.pop("udp_src", FlowFactory.udp_dynamic_port)
        udp_dest = flow_config.pop("udp_dest", FlowFactory.udp_dynamic_port)
        # Using default configuration if no frame_length given:
        frame_length = flow_config.pop("frame_size", None)

        udp_analysis = flow_config.pop("analysis", {})
        enable_latency = udp_analysis.pop('latency', False)

        ip_ecn, ip_dscp = FlowFactory._ip_traffic_class_fields_getter(
            flow_config
        )

        # Determine flow version and create frame
        frame = create_frame(
            source,
            length=frame_length,
            udp_src=udp_src,
            udp_dest=udp_dest,
            ip_ecn=ip_ecn,
            ip_dscp=ip_dscp,
            latency_tag=enable_latency
        )

        # Increment default UDP source port for each flow
        FlowFactory._advance_udp_port()

        # Configure frame blasting flow
        flow = FrameBlastingFlow(
            source, destination, name=name, frame_list=[frame], **flow_config
        )

        logging.info(
            "Created flow %s from %s to %s", flow.name, source.name,
            destination.name
        )

        if enable_latency:
            flow.add_analyser(
                LatencyCDFFrameLossAnalyser(
                    layer2_speed=layer2_speed,
                    **udp_analysis,
                )
            )

            # remove unsupported parameter by LatencyFrameLossAnalyser
            udp_analysis.pop("quantile", None)
            flow.add_analyser(
                LatencyFrameLossAnalyser(
                    layer2_speed=layer2_speed, **udp_analysis
                )
            )
            logging.info("Latency analysers created")
        else:
            flow.add_analyser(
                FrameLossAnalyser(layer2_speed=layer2_speed, **udp_analysis)
            )
            logging.info("Frame Loss analyser created")

        return flow

    @staticmethod
    def create_http_flow(
        flow_config: FlowConfiguration,
        source: Union[Port, Endpoint],
        destination: Union[Port, Endpoint],
    ) -> HTTPFlow:
        """Create a HTTP (TCP) flow.

        :param flow_config: Configuration parameters for the flow
        :type flow_config: FlowConfiguration
        :param source: Transmitter of the data traffic
        :type source: Union[Port, Endpoint]
        :param destination: Receiver of the data traffic
        :type destination: Union[Port, Endpoint]
        :return: Newly created flow
        :rtype: HTTPFlow
        """
        name = flow_config.pop("name", None)
        duration = flow_config.pop("duration", None)
        ip_ecn, ip_dscp = FlowFactory._ip_traffic_class_fields_getter(
            flow_config
        )
        enable_l4s = flow_config.pop("enable_l4s", None)

        flow = HTTPFlow(
            source,
            destination,
            name=name,
            ip_dscp=ip_dscp,
            ip_ecn=ip_ecn,
            request_duration=duration,
            enable_tcp_prague=enable_l4s,
            **flow_config
        )

        logging.info(
            "Created flow %s from %s to %s", flow.name, source.name,
            destination.name
        )

        if enable_l4s:
            flow.add_analyser(L4SHttpAnalyser())
        else:
            flow.add_analyser(HttpAnalyser())
        return flow

    @staticmethod
    def _ip_traffic_class_fields_getter(
        flow_config: FlowConfiguration
    ) -> Tuple[Optional[int], Optional[int]]:
        # Retrieve ECN:
        ecn = flow_config.pop("ecn", None)
        if ecn is not None:
            ecn = string_array_to_int(ecn)
        # Retrieve DSCP:
        dscp = flow_config.pop("dscp", None)
        if dscp is not None:
            dscp = string_array_to_int(dscp)
        return ecn, dscp

    @classmethod
    def _advance_udp_port(cls) -> None:
        if cls.udp_dynamic_port < 65535:
            cls.udp_dynamic_port += 1
        else:
            raise MaximumUdpPortExceeded('Exceeded Max. UDP port Number')


def initialize_flow(
    flow_config: FlowConfiguration,
    layer2_speed: Layer2Speed,
    source: Union[Port, Endpoint],
    destination: Union[Port, Endpoint],
) -> Flow:
    """Create a data traffic flow.

    We currently support:

    * UDP frame blasting (type: ``frame_blasting``)
    * HTTP (stateful TCP) (type: ``http``)

    :param flow_config: Configuration parameters for the flow
    :type flow_config: FlowConfiguration
    :param layer2_speed: Layer 2 speed to report
    :type layer2_speed: Layer2Speed
    :param source: Transmitter of the data traffic
    :type source: Union[Port, Endpoint]
    :param destination: Receiver of the data traffic
    :type destination: Union[Port, Endpoint]
    :raises InvalidInput: When an unknown flow type was requested.
    :return: Newly created flow
    :rtype: Flow
    """
    flow_type = flow_config.pop("type")

    if flow_type.lower() == "frame_blasting":
        # UDP (Frame Blasting) flows
        flow = FlowFactory.create_udp_flow(
            flow_config, layer2_speed, source, destination
        )
    elif flow_type.lower() == "http":
        #TCP (HTTP) flow
        flow = FlowFactory.create_http_flow(flow_config, source, destination)
    else:
        raise InvalidInput(f'Unsupported Flow type: {flow_type!r}')
    return flow
