"""Containing the data gathering interface definition."""
from abc import ABC, abstractmethod
from datetime import timedelta  # for type hinting
from typing import Optional  # for type hinting


class DataGatherer(ABC):
    """Data gathering interface definition."""

    __slots__ = ()

    def __init__(self) -> None:
        """Make a new data gatherer."""

    def prepare_configure(self) -> None:
        """
        Prepare the configuration for the receivers.

        At this point, it is allowed to perform address resolution,
        port discovery, ...

        .. note::
           Virtual method.
        """

    def initialize(self) -> None:
        """
        Configure the receivers to process expected data.

        .. warning::
           No more activities (like address / port discovery, ...) allowed
           in the network under test.

        .. note::
           Virtual method.
        """

    def prepare_start(
        self, maximum_run_time: Optional[timedelta] = None
    ) -> None:
        """
        Prepare the receivers to process expected data.

        .. warning::
           No more activities (like address / port discovery, ...) allowed
           in the network under test.

        .. note::
           Virtual method.
        """

    def process(self) -> None:
        """
        .. note::
           Virtual method.
        """

    def updatestats(self) -> None:
        """
        .. note::
           Virtual method.
        """

    @property
    def finished(self) -> bool:
        """
        Return whether data gathering finished.

        .. note::
           Virtual method.
        """

    def summarize(self) -> None:
        """
        Store the final results.

        This can contain totals, summary, ...

        .. note::
           Virtual method.
        """

    @abstractmethod
    def release(self) -> None:
        """Release all resources used on the ByteBlower system."""
