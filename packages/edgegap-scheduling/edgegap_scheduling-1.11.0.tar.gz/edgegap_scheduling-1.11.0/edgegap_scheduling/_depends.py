from typing import Callable


class SchedulingDepends:
    def __init__(self, dependency: Callable):
        self.dependency = dependency
