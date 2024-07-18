class SchedulingError(Exception):
    pass


class ManualRunNotAllowedError(SchedulingError):
    pass
