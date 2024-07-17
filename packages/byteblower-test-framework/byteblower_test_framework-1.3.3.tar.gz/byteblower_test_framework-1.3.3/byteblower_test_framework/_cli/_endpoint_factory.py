"""Factory functions to create and initialize :class:`~Endpoint` instances."""
import logging

from byteblower_test_framework.endpoint import Endpoint  # for type hinting
from byteblower_test_framework.endpoint import IPv4Endpoint, IPv6Endpoint
from byteblower_test_framework.exceptions import InvalidInput
from byteblower_test_framework.host import MeetingPoint  # for type hinting

from ._definitions import LOGGING_PREFIX as _LOGGING_PREFIX
from ._definitions import PortConfig  # for type hinting

__all__ = ('initialize_endpoint',)


class EndpointFactory(object):  # pylint: disable=too-few-public-methods
    """
    Factory for :class:`Endpoint` objects.

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """

    @staticmethod
    def build_endpoint(meeting_point: MeetingPoint, **port_config) -> Endpoint:
        """Create a :class:`Endpoint`.

        The function can create either :class:`IPv4Endpoint`
        or :class:`IPv6Endpoint` objects.

        :param meeting_point: The :class:`MeetingPoint` object to create
           the port on
        :type meeting_point: MeetingPoint
        :param port_config: The configuration for the port.
        :type port_config: PortConfig
        :return: The newly created endpoint
        :rtype: Endpoint
        """
        ipv4 = port_config.pop('ipv4', False)
        ipv6 = port_config.pop('ipv6', False)
        if ipv4 and ipv6:
            raise InvalidInput(
                'Please provide either IPv4 or IPv6 configuration,'
                ' but not both.'
            )
        if ipv4:
            endpoint_class = IPv4Endpoint
        elif ipv6:
            endpoint_class = IPv6Endpoint
        else:
            raise InvalidInput(
                'Please provide either IPv4 or IPv6 configuration'
            )
        endpoint = endpoint_class(meeting_point, **port_config)
        return endpoint


def initialize_endpoint(
    meeting_point: MeetingPoint,
    port_config: PortConfig,
) -> Endpoint:
    """Create a :class:`Endpoint`.

    The function can create either :class:`IPv4Endpoint`
    or :class:`IPv6Endpoint` objects.

    :param meeting_point: The :class:`MeetingPoint` object to create
       the endpoint on
    :type meeting_point: MeetingPoint
    :param port_config: The configuration for the port.
    :type port_config: PortConfig
    :return: The newly created Endpoint
    :rtype: Endpoint

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """
    logging.info('%sInitializing port', _LOGGING_PREFIX)
    endpoint: Endpoint = EndpointFactory.build_endpoint(
        meeting_point, **port_config
    )
    logging.info(
        '%sInitialized endpoint %r'
        ' with IP address %r, UUID %r', _LOGGING_PREFIX, endpoint.name,
        endpoint.ip, endpoint.uuid
    )

    return endpoint
