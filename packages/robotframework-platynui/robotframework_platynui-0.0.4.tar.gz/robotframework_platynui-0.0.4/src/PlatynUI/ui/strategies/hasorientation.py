from abc import *

from ...core import StrategyBase
from ..orientation import Orientation

__all__ = ["HasOrientation", "Orientation"]


class HasOrientation(StrategyBase):
    strategy_name = "org.platynui.strategies.HasOrientation"

    @property
    @abstractmethod
    def orientation(self) -> Orientation:
        pass
