"""Helpers for the ByteBlower Test Framework."""
from typing import List, Optional, Sequence  # for type hinting

__all__ = ('Taggable',)


class Taggable(object):
    """
    Base/helper class for managing object tags.

    .. versionadded:: 1.2.0
       Generic interface for *taggable* items.
    """

    __slots__ = ('_tags',)

    def __init__(self, tags: Optional[Sequence[str]] = None) -> None:
        """Initialize the taggable object.

        :param tags: List of tags to assign, defaults to None
        :type tags: Optional[Sequence[str]], optional
        """
        self._tags: List[str] = []

        if tags is not None:
            for tag in tags:
                self.add_tag(tag)

    @property
    def tags(self) -> Sequence[str]:
        """Return the list of assigned tags."""
        return self._tags

    def add_tag(self, new_tag: str) -> None:
        """Add a tag to this object.

        :param new_tag: Tag to add
        :type new_tag: str
        """
        new_tag = new_tag.lower()
        if new_tag not in self._tags:
            self._tags.append(new_tag)
