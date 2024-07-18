from abc import *

from ...core import StrategyBase
from ..togglestate import ToggleState

__all__ = ["HasToggleState", "Toggleable", "ToggleState"]


class HasToggleState(StrategyBase):
    strategy_name = "org.platynui.strategies.HasToggleState"

    @property
    @abstractmethod
    def state(self) -> ToggleState:
        pass


class Toggleable(StrategyBase):
    strategy_name = "org.platynui.strategies.Toggleable"

    @abstractmethod
    def toggle(self) -> None:
        pass
