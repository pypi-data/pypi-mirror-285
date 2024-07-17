"""Command-line interface specific exceptions."""
from ..exceptions import ByteBlowerTestFrameworkException


class MaximumUdpPortExceeded(ByteBlowerTestFrameworkException):
    """Exceeded maximum allowed UDP port number (65535)."""
