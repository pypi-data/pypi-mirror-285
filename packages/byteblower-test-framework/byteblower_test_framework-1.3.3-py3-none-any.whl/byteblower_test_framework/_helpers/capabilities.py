from typing import NoReturn, Union  # for type hinting

from byteblowerll.byteblower import ConfigError

from .._endpoint.endpoint import Endpoint
from .._endpoint.port import Port
from ..exceptions import ByteBlowerTestFrameworkException, FeatureNotSupported

__all__ = (
    'CAPABILITY_TCP_L4S',
    'capability_supported',
)

#: Whether a traffic endpoint supports configuring TCP Prague.
#:
#: This is required to support L4S on TCP.
CAPABILITY_TCP_L4S = 'Tcp.L4S'
DESCRIPTION_CAPABILITY_TCP_L4S = 'L4S on TCP'


def capability_supported(
    endpoint: Union[Port, Endpoint], capability_name: str, description: str
) -> Union[NoReturn, None]:
    """Check whether this traffic endpoint supports the given capability.

    .. note::
       An exception with hint will be raised when the API does not support
       the capability.

    :param endpoint: Traffic endpoint to check the capability on
    :type endpoint: Union[Port, Endpoint]
    :param capability_name: Name of the capability to check
    :type capability_name: str
    :param description: Short description of the capability.
       Used for logging purposes
    :type description: str
    :raises ByteBlowerTestFrameworkException:
       When an invalid traffic endpoint is provided.
    :raises FeatureNotSupported: When the capability is not supported.
    """
    if isinstance(endpoint, Port):
        api_endpoint = endpoint.bb_port
    elif isinstance(endpoint, Endpoint):
        api_endpoint = endpoint.bb_endpoint
    else:
        raise ByteBlowerTestFrameworkException(
            f'Unsupported endpoint {endpoint!r}'
        )
    if not api_endpoint.CapabilityIsSupported(capability_name):
        try:
            api_endpoint.CapabilityGetByName(capability_name)
        except ConfigError:
            pass
        else:
            raise FeatureNotSupported(
                f'{endpoint.name} does not support {description}'
            )
        raise FeatureNotSupported(
            f'Cannot check whether {endpoint.name} supports {description}.'
            ' Please update your API.'
        )
