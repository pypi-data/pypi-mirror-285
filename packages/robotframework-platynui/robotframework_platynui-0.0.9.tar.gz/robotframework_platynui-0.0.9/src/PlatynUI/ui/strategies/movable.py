from abc import *

from ...core import StrategyBase
from ...core.types import Point

__all__ = ["Movable"]


class Movable(StrategyBase):
    strategy_name = "org.platynui.strategies.Movable"

    @abstractmethod
    def move(self, point: Point) -> None:
        pass
