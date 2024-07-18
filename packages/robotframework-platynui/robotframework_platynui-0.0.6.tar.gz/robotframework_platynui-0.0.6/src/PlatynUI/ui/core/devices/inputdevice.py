import abc
import time
from typing import Optional

from ....core.settings import Settings

__all__ = ["InputDevice"]


class InputDevice(metaclass=abc.ABCMeta):
    __after_input_delay: Optional[float] = None

    @property
    def after_input_delay(self) -> float:
        if self.__after_input_delay is None:
            return Settings.current().input_after_input_delay
        return self.__after_input_delay

    @after_input_delay.setter
    def after_input_delay(self, value: float) -> None:
        self.__after_input_delay = value

    def delay(self, seconds: float) -> None:
        time.sleep(seconds)
