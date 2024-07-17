"""
Timers with different use cases.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from contextlib import AbstractContextManager
from dataclasses import dataclass, field
import time
from typing import Any, ClassVar, Self, cast, final, override

from what2_time.counter import TimeCounter

__all__ = [
    "MetaTimer",
    "Timer",
]


@dataclass
class BaseTimer[SelfT](AbstractContextManager[SelfT, None]):
    """
    A basic stopwatch style timer.

    Notes
    -----
    Subclassing ContextManager is trixy. eg see microsoft/pyright#6624
    to avoid ignores, the type argument to the class should be the child
    class (or, as here, a template child class defaulted to the current class).
    """

    # TODO: make repr nicer
    __start_time: int = field(default=0, init=False, repr=False)

    total_time: TimeCounter = field(default_factory=TimeCounter.nano_counter, init=True, kw_only=True)

    is_running: bool = field(default=False, init=False, repr=True)

    def start(self) -> Self:
        """
        Start the timer.
        :returns: The timer.
        """
        self.__start_time = time.perf_counter_ns()
        self.is_running = True
        return self

    def as_seconds(self) -> float:
        """
        Get the current recorded time as seconds counted up to the last stop.
        :returns: The recorded time as seconds.
        """
        return self.total_time.as_seconds()

    def stop(self) -> float:
        """
        Stop the timer and return the accumulatd time as seconds.
        :returns: The recorded time as seconds.
        """
        now = time.perf_counter_ns()
        elapsed = now - self.__start_time
        self.is_running = False
        self.total_time.add(elapsed)
        return self.as_seconds()

    def reset(self) -> None:
        """Reset the accumulated time to zero."""
        self.total_time.reset()

    @override
    def __enter__(self: SelfT) -> SelfT:
        """Time the duration of a context block."""
        cast(BaseTimer[SelfT], self).start()
        return self

    @override
    def __exit__(self, *exc_info: object) -> None:
        """Stop the context manager timer."""
        self.stop()


type TimerT = Timer


@dataclass
@final
class Timer(BaseTimer[TimerT]):
    """
    Named timer which automatically logs time and resets when stopped.
    """

    name: str | None = field(default=None, repr=True)
    logger: Callable[[str], Any] | None = field(default=print, repr=False)

    @override
    def stop(self) -> float:
        """
        Stop the timer, reset and return the accumulatd time as seconds.
        :returns: The recorded time as seconds.
        """
        elapsed_time = super().stop()

        self.reset()
        if self.logger:
            message = f"Elapsed time: {elapsed_time:0.4f} seconds"
            if self.name:
                message = f"{self.name} - {message}"

            self.logger(message)

        return elapsed_time


type MetaTimerT = MetaTimer


class MetaTimer(BaseTimer[MetaTimerT]):
    """
    Timer that aggregates all durations for the same name.
    """

    __global_timers: ClassVar[dict[str, TimeCounter]] = defaultdict(TimeCounter.nano_counter)
    name: str

    def __init__(self, name: str) -> None:
        self.name = name
        total_time = self._get_meta_count(name)
        super().__init__(total_time=total_time)

    @classmethod
    def _get_meta_count(cls, name: str) -> TimeCounter:
        """
        Get counter for the given name.
        """
        return cls.__global_timers[name]

    @classmethod
    def get_meta_duration(cls, name: str) -> float:
        """
        Get total duration in seconds for a given name.
        :param name: The name of the timer being queried for.
        :returns: The total duration in seconds for the given name.
        """
        return cls._get_meta_count(name).as_seconds()
