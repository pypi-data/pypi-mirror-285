from datetime import datetime, timezone
from typing import Callable

from edgegap_logging import Color, Format
from pydantic import BaseModel, Field, computed_field
from pytimeparse import parse

from ._model import UndefinedParameters
from ._state import TaskState


class Task(BaseModel):
    identifier: str = Field(default=None, description='The identifier of the Task')
    name: str = Field(..., description='The name of the Task')
    every: str | None = Field(default=None, description='The interval to run the Task')
    delay: str | None = Field(default=None, description='Delay before starting the Task')
    state: TaskState = Field(default=TaskState.PENDING, description='The Current Task State')
    func: Callable = Field(..., description='The function to call', exclude=True)
    message: str | None = Field(default=None, description='The message from the Task or Runner')
    error: str | None = Field(default=None, description='The error message')
    started_at: datetime | None = Field(default=None, description='The start time of the Task')
    begin_at: datetime | None = Field(default=None, description='The last time of the Task began')
    sleep_at: datetime | None = Field(default=None, description='The last time where the Task slept')
    stopped_at: datetime | None = Field(default=None, description='The Time the Task stopped')
    continue_on_exception: bool = Field(default=True, description='If the Task continue after an exception')
    manual_run_allowed: bool = Field(default=False, description='If the Task can be manually run')
    remove_running_time: bool = Field(default=False, description='If the Sleep needs to remove the running time')
    parameters: BaseModel = Field(
        default=UndefinedParameters,
        description='The parameters of the Task to inject on runtime',
    )

    def __str__(self):
        return (
            f'Task {Format.squared(self.name, Color.GREEN)} - '
            f'Every {Format.squared(self.every, Color.GREEN)} - '
            f'Delay {Format.squared(self.delay, Color.GREEN)} - '
            f'State {Format.squared(self.state.value, self.state.color)}'
        )

    @property
    def every_in_seconds(self) -> float | int | None:
        return parse(self.every) if isinstance(self.every, str) else None

    @property
    def delay_in_seconds(self) -> float | int | None:
        return parse(self.delay) if isinstance(self.delay, str) else None

    @property
    def should_delay(self) -> bool:
        return isinstance(self.delay_in_seconds, (float, int))

    @property
    def need_to_loop(self) -> bool:
        return isinstance(self.every_in_seconds, (float, int))

    @computed_field(description='If the Task is safe to start')
    @property
    def safe_to_start(self) -> bool:
        return self.state in [TaskState.PENDING, TaskState.COMPLETED, TaskState.STOPPED, TaskState.ERROR]

    @computed_field(description='For how long the task did the processing before sleeping')
    @property
    def last_processing_duration(self) -> float | int | None:
        if self.begin_at and self.sleep_at:
            if self.begin_at < self.sleep_at:
                return (self.sleep_at - self.begin_at).total_seconds()

    @computed_field(description='If the task is currently processing or sleeping')
    @property
    def is_processing(self) -> bool:
        is_running = False

        if self.state == TaskState.RUNNING:
            if self.begin_at and self.sleep_at:
                is_running = self.begin_at > self.sleep_at
            elif self.begin_at and self.sleep_at is None:
                is_running = True

        return is_running

    @computed_field(description='If the task is currently sleeping (will be false if the task is not running)')
    @property
    def is_sleeping(self) -> bool:
        is_sleeping = False

        if self.begin_at and self.sleep_at:
            is_sleeping = self.sleep_at > self.begin_at

        return is_sleeping

    @computed_field(description='The Time to sleep remaining')
    @property
    def next_sleep_duration(self) -> float | int | None:
        if self.is_processing:
            time_since_start = (datetime.now(tz=timezone.utc) - self.begin_at).total_seconds()
            diff = max(self.every_in_seconds - time_since_start, 0)

            return self.every_in_seconds if not self.remove_running_time else diff
