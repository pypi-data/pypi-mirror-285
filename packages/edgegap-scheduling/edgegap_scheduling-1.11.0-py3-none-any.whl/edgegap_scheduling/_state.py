import enum

from edgegap_logging import Color


class TaskState(enum.Enum):
    PENDING = 'Pending'
    RUNNING = 'Running'
    STOPPING = 'Stopping'
    STOPPED = 'Stopped'
    COMPLETED = 'Completed'
    ERROR = 'Error'

    @property
    def color(self) -> Color:
        return self.__color_mapping__.get(self, Color.WHITE)

    __color_mapping__ = {
        PENDING: Color.WHITE,
        RUNNING: Color.GREEN,
        STOPPING: Color.LIGHTYELLOW_EX,
        STOPPED: Color.YELLOW,
        COMPLETED: Color.BLUE,
        ERROR: Color.RED,
    }
