from robot.utils import secs_to_timestr


class TimeSpan:
    def __init__(self, seconds: float):
        self.seconds = seconds

    def __str__(self) -> str:
        return secs_to_timestr(self.seconds)
