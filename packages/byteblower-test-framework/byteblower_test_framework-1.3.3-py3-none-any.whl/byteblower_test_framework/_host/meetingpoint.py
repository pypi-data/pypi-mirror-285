"""ByteBlower Meeting Point interface module."""
import logging
from contextlib import AbstractContextManager
from datetime import datetime
from types import TracebackType  # for type hinting
from typing import List, Optional, Type, cast  # for type hinting

from byteblowerll.byteblower import MeetingPointServiceInfo  # for type hinting
from byteblowerll.byteblower import ByteBlower
from byteblowerll.byteblower import (
    MeetingPoint as LLMeetingPoint,  # for type hinting
)
from byteblowerll.byteblower import (
    WirelessEndpoint as LLEndpoint,  # for type hinting
)


class MeetingPointConnection(AbstractContextManager):
    """Helper class to manage connections to a ByteBlower Meeting Point.

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """

    __slots__ = (
        "_host_ip",
        "_bb_meeting_point",
    )

    def __init__(self, ip_or_host: str) -> None:
        """
        Connect to the ByteBlower Meeting Point.

        :param ip_or_host: The connection address. This can be
           the hostname or IPv4/IPv6 address of the ByteBlower Meeting Point.
        """
        self._host_ip = ip_or_host
        self._bb_meeting_point: LLMeetingPoint

    def __enter__(self) -> LLMeetingPoint:
        """
        Return connected Meeting Point upon entering the runtime context.

        :return: ByteBlower Meeting Point to which we are connected.
        :rtype: LLMeetingPoint
        """
        bb_root: ByteBlower = ByteBlower.InstanceGet()
        self._bb_meeting_point = cast(
            LLMeetingPoint, bb_root.MeetingPointAdd(self._host_ip)
        )

        # No need to call super().__enter__()
        return self._bb_meeting_point

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> Optional[bool]:
        """Disconnect from the ByteBlower Meeting Point.

        :param exc_type: Type of Exception which occurred
        :type exc_type: Optional[Type[BaseException]]
        :param exc_value: Exception which occurred
        :type exc_value: Optional[BaseException]
        :param traceback: Traceback of the exception.
        :type traceback: Optional[TracebackType]
        :return: Whether the exception has been handled.
        :rtype: Optional[bool]
        """
        bb_root: ByteBlower = ByteBlower.InstanceGet()
        bb_meeting_point = self._bb_meeting_point
        del self._bb_meeting_point
        bb_root.MeetingPointRemove(bb_meeting_point)

        return super().__exit__(exc_type, exc_value, traceback)


def _machine_id(meeting_point_address: str) -> str:
    """Get the unique machine ID of the Meeting Point"""
    with MeetingPointConnection(meeting_point_address) as bb_meeting_point:
        service_info: MeetingPointServiceInfo = (
            bb_meeting_point.ServiceInfoGet()
        )
        return service_info.MachineIDGet()


class MeetingPoint(object):
    """
    ByteBlower Meeting Point interface.

    .. versionadded:: 1.2.0
       Added for ByteBlower Endpoint support.
    """

    __slots__ = (
        '_host_ip',
        '_bb_meeting_point',
        '_endpoint_devices',
    )
    _instances = {}

    def __new__(cls, ip_or_host: str):

        machine_id = _machine_id(ip_or_host)

        instance = cls._instances.get(machine_id)
        if not instance:
            # 1. Create a new instance
            #    (singleton for this machine ID)
            instance: MeetingPoint = super().__new__(cls)

            # 2. Initialize the new instance
            # NOTE: Do this here because `instance.__init__()`
            # is called on every instance returned by `__new__`,
            # also on existing (== already initialized) instances.
            instance._host_ip = ip_or_host

            bb_root: ByteBlower = ByteBlower.InstanceGet()
            instance._bb_meeting_point: LLMeetingPoint = (
                bb_root.MeetingPointAdd(instance._host_ip)
            )
            # NOTE: We can't use the LLEndpointList() here
            #       because .erase() does not work.
            #       That is required for `release_endpoint()`
            instance._endpoint_devices: List[LLEndpoint] = []

            # 3. Cache the newly created instance
            cls._instances[machine_id] = instance
        return instance

    def __init__(self, ip_or_host: str) -> None:
        """Connect to the ByteBlower Meeting Point.

        :param ip_or_host: The connection address. This can be
           the hostname or IPv4/IPv6 address of the ByteBlower Meeting Point.
        :type ip_or_host: str
        """

    @property
    def info(self) -> str:
        """Return connection address this Meeting Point."""
        return self._host_ip

    def release(self) -> None:
        """
        Release this host related resources used on the ByteBlower system.

        .. warning::
           Releasing resources related to traffic generation and analysis
           should be done *first* via the :meth:`Scenario.release()`
           and/or :meth:`Flow.release()`.

        .. warning::
           Releasing endpoint resources should be done *first*
           via :meth:`Port.release()`.
        """
        try:
            bb_meeting_point = self._bb_meeting_point
            del self._bb_meeting_point
        except AttributeError:
            logging.warning('MeetingPoint: Already destroyed?', exc_info=True)
        else:
            bb_root: ByteBlower = ByteBlower.InstanceGet()
            bb_root.MeetingPointRemove(bb_meeting_point)

    @property
    def timestamp(self) -> datetime:
        """Return the current time on the Meeting Point."""
        ts = self._bb_meeting_point.TimestampGet()  # pylint: disable=invalid-name
        return datetime.utcfromtimestamp(ts / 1e9)

    def reserve_endpoint(self, uuid: str) -> LLEndpoint:
        """Add device to the list of endpoints used in the test."""
        bb_endpoint: LLEndpoint = self._bb_meeting_point.DeviceGet(uuid)
        self._endpoint_devices.append(bb_endpoint)
        return bb_endpoint

    def release_endpoint(self, endpoint: LLEndpoint) -> None:
        """Release this endpoint resources used on the ByteBlower system.

        Removes this device from the list of endpoints used in the test
        and destroys it on the Meeting Point.

        :param endpoint: Endpoint to release
        :type endpoint: LLEndpoint
        """
        self._endpoint_devices.remove(endpoint)
        self._bb_meeting_point.DeviceDestroy(endpoint)

    @property
    def bb_meeting_point(self) -> LLMeetingPoint:
        """Object from the ByteBlower API."""
        return self._bb_meeting_point
