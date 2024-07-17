import logging
from abc import ABC, abstractmethod
from datetime import timedelta
from itertools import count
from typing import (  # for type hinting
    TYPE_CHECKING,
    Any,
    Iterable,
    List,
    Mapping,
    Optional,
    Sequence,
    Union,
)

from .._endpoint.endpoint import Endpoint  # for type hinting
from .._endpoint.port import Port  # for type hinting
from .._helpers.syncexec import SynchronizedDevice
from .._helpers.taggable import Taggable
from ..exceptions import InvalidInput

if TYPE_CHECKING:
    # NOTE: Import does not work at runtime: cyclic import dependencies
    # See also: https://mypy.readthedocs.io/en/stable/runtime_troubles.html#import-cycles, pylint: disable=line-too-long
    from .._analysis.flow_analyser import FlowAnalyser  # for type hinting

    # NOTE: Used for type hinting only
    from .._helpers.syncexec import SynchronizedExecutable

# Type aliases
# TODO - Make the RuntimeErrorInfo a real (base) object ?
#: Flow-specific information about runtime errors
RuntimeErrorInfo = Mapping[str, Any]


class Flow(Taggable, ABC):
    """Base class of a flow between one and one or more endpoints.

    .. versionchanged:: 1.2.0
       Initialization behavior change with addition of
       ByteBlower Endpoint support.

       Address resolution and NAT/NAPT discovery now happens in the
       "*prepare flow configuration*" step (see :meth:`prepare_configure()`)
       instead of during "*flow creation*" (:meth:`__init__()`).
    """

    __slots__ = (
        '_source',
        '_destination',
        '_name',
        '_analysers',
    )

    _number = count(start=1)

    _CONFIG_ELEMENTS = (
        'source',
        'destination',
        'name',
        'analysers',
        'type',
    )

    def __init__(
        self,
        source: Union[Port, Endpoint],
        destination: Union[Port, Endpoint],
        # *args,
        name: Optional[str] = None,
        **kwargs
    ) -> None:
        super().__init__()

        self._source = source
        self._destination = destination

        # NOTE: Always increment, even with given name
        flow_number = next(Flow._number)
        if name is not None:
            self._name = name
        else:
            self._name = f'Flow {flow_number}'

        if kwargs:
            logging.error(
                'Unsupported keyword arguments for Flow %r: %r', self._name,
                [f'{key}={value!r}' for key, value in kwargs.items()]
            )
            raise ValueError(
                'Unsupported configuration parameters'
                f' for Flow {self._name!r}: {[key for key in kwargs]!r}'
            )

        if self._source.failed:
            raise ValueError(
                f'Cannot send from ByteBlower Port {self._source.name!r}'
                ' because address configuration failed.'
            )

        if self._destination.failed:
            raise ValueError(
                'Cannot send to ByteBlower Port {self._destination.name!r}'
                ' because address configuration failed.'
            )

        if (self._source.require_nat_discovery
                and self._destination.require_nat_discovery):
            raise ValueError(
                'Cannot send between two traffic endpoints'
                f' ({self._source.name!r} <> {self._destination.name!r})'
                ' behind a NAT/NAPT gateway.'
            )

        self._analysers: List['FlowAnalyser'] = []

        self.add_tag('from_' + self._source.name)
        for tag in self._source.tags:
            self.add_tag('from_' + tag)
        self.add_tag('to_' + self._destination.name)
        for tag in self._destination.tags:
            self.add_tag('to_' + tag)

    @property
    def source(self) -> Union[Port, Endpoint]:
        """Return this flow source."""
        return self._source

    @property
    def destination(self) -> Union[Port, Endpoint]:
        """Return this flow destination."""
        return self._destination

    @property
    def name(self) -> str:
        """Return this flow name."""
        return self._name

    @property
    @abstractmethod
    def initial_time_to_wait(self) -> timedelta:
        """Return the time to wait before the flow starts."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def duration(self) -> timedelta:
        """Returns the duration of the flow.

        :raises NotDurationBased: If the Flow is sized based.
        :raises InfiniteDuration: If the flow duration is not set.
        :return: duration of the flow.
        :rtype: timedelta
        """
        raise NotImplementedError()

    @property
    def type(self) -> str:
        return self.__class__.__name__

    @property
    def analysers(self) -> Sequence['FlowAnalyser']:
        """Return the list of flow analysers added to this Flow.

        :return: List of added flow analysers
        :rtype: Sequence[FlowAnalyser]
        """
        return self._analysers

    @property
    def config(self) -> Sequence[str]:
        configs = []

        for k in self._CONFIG_ELEMENTS:
            if k == 'analysers':
                continue

            if k in ('source', 'destination'):
                port: Union[Port, Endpoint] = getattr(self, k)
                v = port.ip
            else:
                v = getattr(self, k)
            configs.append(f"{k!s} = {v!s}")
        return configs

    @property
    @abstractmethod
    def finished(self) -> bool:
        """Returns True if the flow is done."""
        raise NotImplementedError()

    @property
    @abstractmethod
    def runtime_error_info(self) -> RuntimeErrorInfo:
        """Returns implementation-specific runtime error info."""
        raise NotImplementedError()

    def add_analyser(self, analyser: 'FlowAnalyser') -> None:
        analyser._add_to_flow(self)
        self._analysers.append(analyser)

    def prepare_configure(self) -> None:
        """
        Prepare the flow and its analysers to be configured.

        At this point, it is allowed to perform address resolution,
        port discovery, ...

        .. note::
           Virtual method with implementation.
           Should be called by child implementations.
        """
        for analyser in self._analysers:
            analyser.prepare_configure()

    def initialize(self) -> None:
        """
        Configure the flow and its analysers.

        .. warning::
           No more activities (like address / port discovery, ...) allowed
           in the network under test.

        .. note::
           Virtual method with implementation.
           Should be called by child implementations.
        """
        for analyser in self._analysers:
            analyser.initialize()

    def prepare_start(
        self,
        maximum_run_time: Optional[timedelta] = None
    ) -> Iterable['SynchronizedExecutable']:
        """
        Prepare the flow and its analysers to start traffic and analysis.

        .. warning::
           No more activities (like address / port discovery, ...) allowed
           in the network under test.

        .. note::
           Virtual method with implementation.
           Should be called by child implementations.
        """
        if isinstance(self._source, Endpoint):
            if maximum_run_time is None:
                raise InvalidInput(
                    'Maximum run time is required to configure a Scenario'
                    ' on a ByteBlower Endpoint'
                )
            self._source.bb_endpoint.ScenarioDurationSet(
                int(maximum_run_time.total_seconds() * 1e9)
            )
        if isinstance(self._destination, Endpoint):
            if maximum_run_time is None:
                raise InvalidInput(
                    'Maximum run time is required to configure a Scenario'
                    ' on a ByteBlower Endpoint'
                )
            self._destination.bb_endpoint.ScenarioDurationSet(
                int(maximum_run_time.total_seconds() * 1e9)
            )
        for analyser in self._analysers:
            analyser.prepare_start(maximum_run_time=maximum_run_time)
        # NOTE: turn this function into an "empty" generator
        #
        # See also
        #   https://stackoverflow.com/questions/13243766/how-to-define-an-empty-generator-function/61496399#61496399  # pylint: disable=line-too-long
        # for considerations regarding performance.
        yield from ()

    def synchronized_devices(self) -> Iterable[SynchronizedDevice]:
        """
        Gather the devices which can be prepared and started simultaneously.

        :return: Devices to prepare/start synchronized.
        :yield: Synchronized device object
        :rtype: Iterable[SynchronizedDevice]
        """
        if isinstance(self._source, Endpoint):
            yield SynchronizedDevice(self._source.bb_endpoint)
        if isinstance(self._destination, Endpoint):
            yield SynchronizedDevice(self._destination.bb_endpoint)

    def process(self) -> None:
        """
        .. note::
           Virtual method with implementation.
           Should be called by child implementations.
        """
        for analyser in self._analysers:
            analyser.process()

    def updatestats(self) -> None:
        """
        .. note::
           Virtual method with implementation.
           Should be called by child implementations.
        """
        for analyser in self._analysers:
            analyser.updatestats()

    @abstractmethod
    def wait_until_finished(
        self, wait_for_finish: timedelta, result_timeout: timedelta
    ) -> None:
        """Wait until the flow finished traffic generation and processing.

        .. note::
           Virtual method.

        :param wait_for_finish: Time to wait for sessions closing
           and final packets being received.
        :type wait_for_finish: timedelta
        :param result_timeout: Time to wait for Endpoints to finalize
           and return their results to the Meeting Point.

        .. versionadded:: 1.2.0
           Added for ByteBlower Endpoint support.

        :type result_timeout: timedelta
        """

    def stop(self) -> None:
        """
        Stop all traffic generation and analysis for this flow.

        .. note::
            Virtual hook method for child implementations.

        .. versionadded:: 1.1.0
        """

    def analyse(self) -> None:
        """
        .. note::
           Virtual method with implementation.
           Should be called by child implementations.
        """
        for analyser in self._analysers:
            analyser.analyse()

    @abstractmethod
    def release(self) -> None:
        """
        Release all resources used on the ByteBlower system.

        Releases all resources related to traffic generation and analysis.

        .. note::
           Virtual method with implementation.
           Should be called by child implementations.

        .. note::
           The resources related to endpoints and server themselves
           are not released.
        """
        for analyser in self._analysers:
            analyser.release()
