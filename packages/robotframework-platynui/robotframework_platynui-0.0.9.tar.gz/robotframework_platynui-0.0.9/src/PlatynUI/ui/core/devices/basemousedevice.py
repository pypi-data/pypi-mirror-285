from abc import abstractmethod

from ....core.strategybase import StrategyBase
from ....core.types import Point, Size
from .mousebutton import MouseButton

__all__ = ["BaseMouseDevice"]


class BaseMouseDevice(StrategyBase):
    strategy_name = "org.platynui.devices.Mouse"

    @property
    @abstractmethod
    def double_click_time(self) -> float: ...

    @property
    @abstractmethod
    def double_click_size(self) -> Size: ...

    @abstractmethod
    def get_position(self) -> Point: ...
    @abstractmethod
    def move_to(self, pos: Point) -> None: ...

    @abstractmethod
    def press(self, button: MouseButton) -> None: ...

    @abstractmethod
    def release(self, button: MouseButton) -> None: ...
