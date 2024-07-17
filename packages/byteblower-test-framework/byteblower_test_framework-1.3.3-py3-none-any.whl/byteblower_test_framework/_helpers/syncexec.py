"""Helpers to support synchronized execution of certain functions."""
import logging
from typing import Any, Callable, Iterable, List, Set  # for type hinting

from byteblowerll.byteblower import DeviceInfo  # for type hinting
from byteblowerll.byteblower import SchedulableObject  # for type hinting
from byteblowerll.byteblower import ScheduleGroup  # for type hinting
from byteblowerll.byteblower import (
    WirelessEndpoint as LLEndpoint,  # for type hinting
)
from byteblowerll.byteblower import (
    WirelessEndpointList as LLEndpointList,  # for type hinting
)

__all__ = (
    'SynchronizedExecutable',
    'SynchronizedExecution',
    'fill_schedule_group',
    'fill_endpoint_list',
    'lock_devices',
    'unlock_devices',
)

_LOGGER = logging.getLogger(__name__)


class SynchronizedDevice(object):  # pylint: disable=too-few-public-methods
    """Device which can be used for synchronized operations."""

    __slots__ = ('_schedulable_device',)

    def __init__(self, schedulable_device: LLEndpoint) -> None:
        """Create a synchronized executable.

        :param schedulable_device: Schedulable device. Can be used
           for example for synchronized start.
        :type schedulable_device: LLEndpoint
        """
        self._schedulable_device = schedulable_device

    @property
    def schedulable_device(self) -> LLEndpoint:
        """Return our schedulable device."""
        return self._schedulable_device


class SynchronizedExecutable(object):  # pylint: disable=too-few-public-methods
    """Executable which can be used for synchronized operations."""

    __slots__ = ('_schedulable_object',)

    def __init__(self, schedulable_object: SchedulableObject) -> None:
        """Create a synchronized executable.

        :param schedulable_object: Schedulable object. Can be used
           for example for synchronized start.
        :type schedulable_object: SchedulableObject
        """
        self._schedulable_object = schedulable_object

    @property
    def schedulable_object(self) -> SchedulableObject:
        """Return our schedulable object."""
        return self._schedulable_object


class SynchronizedExecution(object):
    """Performs synchronized operations on an synchronized executable."""

    __slots__ = (
        '_sync_devices',
        '_sync_executables',
    )

    def __init__(self) -> None:
        """Create the synchronized execution helper."""
        self._sync_devices: Set[LLEndpoint] = set()
        self._sync_executables: List[SchedulableObject] = []

    def add_devices(self, sync_dev_iter: Iterable[SynchronizedDevice]) -> None:
        """Add synchronized devices.

        :param sync_dev_iter: Synchronized device to add
        :type sync_dev_iter: Iterable[SynchronizedDevice]
        """
        for sync_dev in sync_dev_iter:
            self._sync_devices.add(sync_dev.schedulable_device)

    def add_executables(
        self, sync_exe_iter: Iterable[SynchronizedExecutable]
    ) -> None:
        """Add synchronized executables.

        :param sync_exe_iter: Synchronized executable to add
        :type sync_exe_iter: Iterable[SynchronizedExecutable]
        """
        for sync_exe in sync_exe_iter:
            self._sync_executables.append(sync_exe.schedulable_object)

    def execute_devices(
        self, func: Callable[[Iterable[LLEndpoint]], Any]
    ) -> None:
        """Call the given function on our synchronized devices.

        :param func: Function to execute
        :type func: Callable[[Iterable[LLEndpoint]], Any]
        """
        func(self._sync_devices)

    def execute_executables(
        self, func: Callable[[Iterable[SchedulableObject]], Any]
    ) -> None:
        """Call the given function on our synchronized executables.

        :param func: Function to execute
        :type func: Callable[[Iterable[SchedulableObject]], Any]
        """
        func(self._sync_executables)


def fill_schedule_group(
    schedule_group: ScheduleGroup
) -> Callable[[Iterable[SchedulableObject]], None]:
    """Fill the ScheduleGroup with SchedulableObjects.

    The returned function can be used with
    :meth:`SynchronizedExecution.execute_executables`.

    :param schedule_group: Schedule group to where ``SchedulableObject``s
       will be added to.
    :type schedule_group: ScheduleGroup
    :return: Function to fill the :class:`ScheduleGroup`.
    :rtype: Callable[[Iterable[SchedulableObject]], None]
    """

    def fill_list(schedulable_objects: Iterable[SchedulableObject]) -> None:
        for schedulable_object in schedulable_objects:
            _LOGGER.debug(
                'ScheduleGroup %r: Adding %r', schedule_group,
                schedulable_object
            )
            schedule_group.MembersAdd(schedulable_object)

    return fill_list


def fill_endpoint_list(
    endpoint_list: LLEndpointList
) -> Callable[[Iterable[LLEndpoint]], None]:
    """Fill the LLEndpointList with LLEndpoints.

    The returned function can be used with
    :meth:`SynchronizedExecution.execute_devices`.

    :param endpoint_list: Endpoint list to where ``LLEndpoint``s
       will be added to.
    :type endpoint_list: LLEndpointList
    :return: Function to fill the :class:`LLEndpointList`.
    :rtype: Callable[[Iterable[LLEndpoint]], None]
    """

    def fill_list(schedulable_devices: Iterable[LLEndpoint]) -> None:
        for schedulable_device in get_device_by_uuid(schedulable_devices):
            _LOGGER.debug(
                'EndpointList %r: Adding %r', endpoint_list, schedulable_device
            )
            endpoint_list.append(schedulable_device)

    return fill_list


def lock_devices(schedulable_devices: Iterable[LLEndpoint]) -> None:
    """Lock the Endpoint devices.

    This function can be used with
    :meth:`SynchronizedExecution.execute_devices`.

    :param schedulable_devices: Endpoint devices to lock
    :type schedulable_devices: Iterable[LLEndpoint]
    """

    for device in get_device_by_uuid(schedulable_devices):
        device_info: DeviceInfo = device.DeviceInfoGet()
        logging.debug('Locking Endpoint %r', device_info.GivenNameGet())
        device.Lock(True)


def unlock_devices(schedulable_devices: Iterable[LLEndpoint]) -> None:
    """Unlock the Endpoint devices.

    This function can be used with
    :meth:`SynchronizedExecution.execute_devices`.

    :param schedulable_devices: Endpoint devices to unlock
    :type schedulable_devices: Iterable[LLEndpoint]
    """
    for device in get_device_by_uuid(schedulable_devices):
        device_info: DeviceInfo = device.DeviceInfoGet()
        logging.debug('Unlocking Endpoint %r', device_info.GivenNameGet())
        device.Lock(False)


def get_device_by_uuid(
    schedulable_devices: Iterable[LLEndpoint]
) -> Iterable[LLEndpoint]:
    """Ensure that the endpoint is only locked/prepared once.

    This function can be used with
    :meth:`SynchronizedExecution.execute_devices`.

    :param schedulable_devices: Endpoint devices to check
    :type schedulable_devices: Iterable[LLEndpoint]
    :yield: Yields the device to be locked/prepared
    :rtype: Iterable[LLEndpoint]
    """
    uuids = set()
    for device in schedulable_devices:
        if device.DeviceIdentifierGet() not in uuids:
            yield device
            uuids.add(device.DeviceIdentifierGet())
