from __future__ import annotations

import asyncio
from collections.abc import Awaitable, Callable
from dataclasses import dataclass


JobHandler = Callable[[], Awaitable[None]]


@dataclass
class ScheduledJob:
    name: str
    interval_seconds: int
    handler: JobHandler


class AsyncScheduler:
    def __init__(self) -> None:
        self._jobs: list[ScheduledJob] = []
        self._tasks: list[asyncio.Task] = []
        self._stop_event = asyncio.Event()

    def add_interval_job(self, name: str, interval_seconds: int, handler: JobHandler) -> None:
        self._jobs.append(ScheduledJob(name=name, interval_seconds=interval_seconds, handler=handler))

    async def start(self) -> None:
        self._stop_event.clear()
        for job in self._jobs:
            self._tasks.append(asyncio.create_task(self._run_job(job)))

    async def stop(self) -> None:
        self._stop_event.set()
        for task in self._tasks:
            task.cancel()
        self._tasks.clear()

    async def _run_job(self, job: ScheduledJob) -> None:
        while not self._stop_event.is_set():
            await job.handler()
            try:
                await asyncio.wait_for(self._stop_event.wait(), timeout=job.interval_seconds)
            except asyncio.TimeoutError:
                continue
