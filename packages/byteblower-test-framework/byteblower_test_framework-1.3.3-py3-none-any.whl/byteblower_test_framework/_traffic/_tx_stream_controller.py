"""
Behavior module for transmit streams.

The TxStreamControllers extract device-specific API calls
to behavior interfaces for the test framework.
"""
from typing import Generator, Tuple  # for type hinting

from byteblowerll.byteblower import Stream as TxStream  # for type hinting
from byteblowerll.byteblower import (
    StreamMobile as TxStreamMobile,  # for type hinting
)
from byteblowerll.byteblower import StreamRuntimeStatus  # for type hinting
from byteblowerll.byteblower import TransmitErrorSource  # for type hinting
from byteblowerll.byteblower import TransmitErrorStatus  # for type hinting
from byteblowerll.byteblower import TransmitStatus

from .._endpoint.endpoint import Endpoint
from .._endpoint.port import Port
from .._traffic.stream import StreamErrorSource, StreamErrorStatus


class PortTxStreamController(object):
    """Transmit stream controller for Port interfaces."""

    @staticmethod
    def create(port: Port) -> TxStream:
        """Create a new transmit stream object.

        :param port: Port to create the stream for
        :type port: Port
        :return: Port-specific transmit stream
        :rtype: TxStream
        """
        return port.bb_port.TxStreamAdd()

    @staticmethod
    def finished(_port: Port, stream: TxStream) -> bool:
        """Check whether the transmit stream finished transmission.

        :param _port: Port where the stream was created for
        :type _port: Port
        :param stream: Port-specific transmit stream
        :type stream: TxStream
        :return: Whether transmission finished
        :rtype: bool
        """
        stream_status: StreamRuntimeStatus = stream.StatusGet()
        stream_status.Refresh()
        transmit_status = stream_status.StatusGet()
        return transmit_status == TransmitStatus.INACTIVE

    @staticmethod
    def prepare_start(stream: TxStream) -> Generator[TxStream, None, None]:
        """Return the objects for synchronized start of a stream.

        :param stream: Port-specific transmit stream
        :type stream: TxStream
        :yield: Transmit stream to schedule for start
        :rtype: Generator[TxStream, None, None]
        """
        yield stream

    @staticmethod
    def stop(stream: TxStream) -> None:
        """Stop the transmit stream.

        :param stream: Port-specific transmit stream
        :type stream: TxStream
        """
        stream.Stop()

    @staticmethod
    def error_status(
        stream: TxStream
    ) -> Tuple[StreamErrorStatus, StreamErrorSource]:
        """Get the error status for this transmit stream.

        :param stream: Port-specific transmit stream
        :type stream: TxStream
        :return: Transmit stream error status and source
        :rtype: Tuple[StreamErrorStatus, StreamErrorSource]
        """
        tx_status: StreamRuntimeStatus = stream.StatusGet()
        tx_error_status: TransmitErrorStatus = tx_status.ErrorStatusGet()
        tx_error_source: TransmitErrorSource = tx_status.ErrorSourceGet()
        return (
            StreamErrorStatus(tx_error_status),
            StreamErrorSource(tx_error_source),
        )

    @staticmethod
    def release(port: Port, stream: TxStream) -> None:
        """Destroy the transmit stream.

        .. warning::
           After release, the ``stream`` object is no longer usable.

        :param port: Port where the stream was created for
        :type port: Port
        :param stream: Port-specific transmit stream
        :type stream: TxStream
        """
        port.bb_port.TxStreamRemove(stream)


class EndpointTxStreamController(object):
    """Transmit stream controller for Endpoint interfaces."""

    @staticmethod
    def create(endpoint: Endpoint) -> TxStreamMobile:
        """Create a new transmit stream object.

        :param endpoint: Endpoint to create the stream for
        :type endpoint: Endpoint
        :return: Endpoint-specific transmit stream
        :rtype: TxStreamMobile
        """
        return endpoint.bb_endpoint.TxStreamAdd()

    @staticmethod
    def finished(endpoint: Endpoint, _stream: TxStreamMobile) -> bool:
        """Check whether the transmit stream finished transmission.

        :param endpoint: Endpoint where the stream was created for
        :type endpoint: Endpoint
        :param _stream: Endpoint-specific transmit stream
        :type _stream: TxStreamMobile
        :return: Whether transmission finished
        :rtype: bool
        """
        return not endpoint.active

    @staticmethod
    def prepare_start(
        _stream: TxStreamMobile
    ) -> Generator[TxStreamMobile, None, None]:
        """Return the objects for synchronized start of a stream.

        .. note::
           The Endpoint currently schedules start of everything together
           with the start of a scenario on the Endpoint.

        :param _stream: Endpoint-specific transmit stream
        :type _stream: TxStreamMobile
        :yield: Transmit stream to schedule for start
        :rtype: Generator[TxStreamMobile, None, None]
        """
        # NOTE: turn this function into an "empty" generator
        #
        # See also
        #   https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/61496399#61496399  # pylint: disable=line-too-long
        # for considerations regarding performance.
        yield from ()

    @staticmethod
    def stop(_stream: TxStreamMobile) -> None:
        """Stop the transmit stream.

        :param _stream: Endpoint-specific transmit stream
        :type _stream: TxStreamMobile
        """

    @staticmethod
    def error_status(_stream: TxStreamMobile) -> Tuple[None, None]:
        """Get the error status for this transmit stream.

        :param _stream: Endpoint-specific transmit stream
        :type _stream: TxStreamMobile
        :return: Transmit stream error status and source
        :rtype: Tuple[None, None]
        """
        return None, None

    @staticmethod
    def release(endpoint: Endpoint, stream: TxStreamMobile) -> None:
        """Destroy the transmit stream.

        .. warning::
           After release, the ``stream`` object is no longer usable.

        :param endpoint: Endpoint where the stream was created for
        :type endpoint: Endpoint
        :param stream: Endpoint-specific transmit stream
        :type stream: TxStreamMobile
        """
        endpoint.bb_endpoint.TxStreamRemove(stream)
