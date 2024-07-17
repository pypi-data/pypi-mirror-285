"""
Module to handle basic representation of seconds.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import partialmethod
from typing import ClassVar, Self, override

__all__ = [
    "TimeCounter",
]


@dataclass
class TimeCounter:
    """
    Class to count time.
    """

    base: int
    count: int = field(default=0, init=False)

    second_base: ClassVar[int] = 1
    millisecond_base: ClassVar[int] = 1000
    microsecond_base: ClassVar[int] = 1000000
    nanosecond_base: ClassVar[int] = 1000000000

    @classmethod
    def nano_counter(cls) -> Self:
        """
        Create a counter instance that counts nanoseconds.
        :returns: A counter instance that counts nanoseconds.
        """
        return cls(base=TimeCounter.nanosecond_base)

    @classmethod
    def second_counter(cls) -> Self:
        """
        Create a counter instance that counts seconds.
        :returns: A counter instance that counts seconds.
        """
        return cls(base=TimeCounter.second_base)

    def as_unit(self, base: int) -> float:
        """
        Get the value of the counter in the given base units.
        :param base: The base to convert the held time to, as units per second.
        :returns: The held time in the base units.
        """
        if base == self.base:
            return self.count
        return (self.count * base) / self.base

    as_seconds = partialmethod(as_unit, second_base)
    as_milli = partialmethod(as_unit, millisecond_base)
    as_micro = partialmethod(as_unit, microsecond_base)
    as_nano = partialmethod(as_unit, nanosecond_base)

    def add(self, other: int) -> None:
        """
        Add a value to the current count, assuming it's in the correct base.
        :param other: The unit count to add.
        """
        self.count += other

    def add_timer(self, other: TimeCounter) -> None:
        """
        Combine the duration recorded in other to self.
        :param other: The timer count to add.
        """
        if self.base == other.base:
            self.count += other.count
            return

        self.count += int(other.as_unit(self.base))

    def add_unsafe_timer(self, other: TimeCounter) -> None:
        """
        Combine the duration recorded in other to self, assuming it's the same base.
        :param other: The timer count to add, assumed to be of the same base.
        """
        self.count += other.count

    def reset(self) -> None:
        """
        Reset the current duration to zero.
        """
        self.count = 0

    def __lt__(self, other: TimeCounter) -> bool:
        return self.as_nano() < other.as_nano()

    @override
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TimeCounter):
            return False
        return self.as_nano() == other.as_nano()
