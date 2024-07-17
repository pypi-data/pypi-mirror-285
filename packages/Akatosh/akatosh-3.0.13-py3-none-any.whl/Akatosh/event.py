from __future__ import annotations
import asyncio
import time
from typing import Any, Callable, Optional
from . import logger
from .universe import Mundus


class Event:

    def __init__(
        self,
        at: float | Event,
        till: float | Event,
        action: Callable,
        step: float = Mundus.time_step,
        label: Optional[str] = None,
        once: bool = False,
        priority: int = 0,
    ) -> None:
        """Create an event which happens at a certain time and ends at a certain time.

        Args:
            at (float | Event): when the event should start.
            till (float | Event): when the event should end.
            action (Callable): what happens during the event.
            label (Optional[str], optional): Short description for the event. Defaults to None.
            once (bool, optional): whether this event should only happen once, regardless of at or till. Defaults to False.
            priority (int, optional): the priority of the event, event with lower value will happen before the events with a higher priority value. Defaults to 0.

        Raises:
            ValueError: _description_
        """
        self._at = at
        self._till = till
        self._action = action
        self._started = False
        self._acted = False
        self._ended = False
        self._paused = False
        self._label = label
        self._once = once
        self._priority = priority
        self._step = step
        self._next = 0
        Mundus.pending_events.append(self)
        if self.priority > Mundus.max_event_priority:
            Mundus._max_event_priority = self.priority

    async def __call__(self) -> Any:
        """Make the event callable, so it can be awaited like a coroutine."""
        while True:

            if self.ended == True:
                return

            while True:
                if self.priority == Mundus.current_event_priority:
                    break
                else:
                    await asyncio.sleep(0)

            if self.started == False:
                if isinstance(self.at, Event):
                    if self.at.ended == True:
                        self._started = True
                        self._next = Mundus.time
                        logger.debug(f"Event {self} started at {Mundus.time}.")
                else:
                    if self.at <= Mundus.time:
                        self._started = True
                        self._next = Mundus.time
                        logger.debug(f"Event {self} started at {Mundus.time}.")

            if (
                self.started == True
                and self.ended == False
                and self.paused == False
                and self.next <= Mundus.time
            ):
                if asyncio.iscoroutinefunction(self._action):
                    await self._action()
                else:
                    self._action()
                self._acted = True
                if Mundus.realtime:
                    if self.step != Mundus.time_step:
                        self._next = round(
                            Mundus.time + self.step,
                            Mundus.time_resolution,
                        )
                    else:
                        self._next = (
                            Mundus.time
                        )
                else:
                    self._next += max(Mundus.time_step, self.step)
                    self._next = round(self._next, Mundus.time_resolution)
                logger.debug(f"Event {self} acted at {Mundus.time}.")
                if self._once == True:
                    self._ended = True
                    logger.debug(f"Event {self} ended at {Mundus.time}.")
                    return

            if self.ended == False:
                if isinstance(self.till, Event):
                    if self.till.ended == True:
                        self._ended = True
                        logger.debug(f"Event {self} ended at {Mundus.time}.")
                        return
                else:
                    if self.till <= Mundus.time:
                        self._ended = True
                        logger.debug(f"Event {self} ended at {Mundus.time}.")
                        return
            await asyncio.sleep(0)

    def __str__(self) -> str:
        """Return the label of the event if it has one, otherwise return the id of the event."""
        if self.label is None:
            return f"Event {id(self)}"
        return self.label

    def cancel(self):
        """Cancel the event."""
        self._ended = True
        logger.debug(f"Event {self} cancelled.")

    def pause(self):
        """Pause the event."""
        self._paused = True
        logger.debug(f"Event {self} paused.")

    def resume(self):
        """Resume the event."""
        self._paused = False
        logger.debug(f"Event {self} resumed.")

    @property
    def at(self):
        """Return the time when the event should start."""
        return self._at

    @property
    def till(self):
        """Return the time when the event should end."""
        return self._till

    @property
    def started(self):
        """Return whether the event has started or not."""
        return self._started

    @property
    def ended(self):
        """Return whether the event has ended or not."""
        return self._ended

    @property
    def paused(self):
        """Return whether the event is paused or not."""
        return self._paused

    @property
    def label(self):
        """Return the label of the event."""
        return self._label

    @property
    def once(self):
        """Return whether the event should only happen once or not."""
        return self._once

    @property
    def priority(self):
        """Return the priority of the event."""
        return self._priority

    @property
    def next(self):
        """Return the next time the event acts."""
        return self._next

    @property
    def step(self):
        """Return the time step of the event, which overwrites the simulation time step."""
        return self._step


def event(
    at: float | Event,
    till: float | Event,
    step: float = Mundus.time_step,
    label: Optional[str] = None,
    once: bool = False,
    priority: int = 0,
):
    def _event(action: Callable) -> Event:
        return Event(
            at=at,
            till=till,
            step=step,
            action=action,
            label=label,
            once=once,
            priority=priority,
        )

    return _event
