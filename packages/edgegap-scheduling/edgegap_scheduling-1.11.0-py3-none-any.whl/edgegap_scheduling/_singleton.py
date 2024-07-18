import logging

from ._scheduler import Scheduler


class SchedulingSingleton:
    __instance: Scheduler = None
    __logger: logging.Logger = None

    @classmethod
    def scheduler(cls) -> Scheduler:
        if cls.__instance is None:
            cls.__logger = logging.getLogger('scheduling.Singleton')
            cls.__logger.info('First Invocation of the Scheduling Singleton, creating a new instance')
            cls.__instance = Scheduler()

        return cls.__instance
