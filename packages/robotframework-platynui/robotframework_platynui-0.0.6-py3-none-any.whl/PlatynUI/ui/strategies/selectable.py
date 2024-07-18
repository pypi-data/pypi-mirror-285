from abc import *

from ...core import StrategyBase

__all__ = ["HasSelected", "Selectable"]


class HasSelected(StrategyBase):
    strategy_name = "org.platynui.strategies.HasSelected"

    @property
    @abstractmethod
    def is_selectable(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_selected(self) -> bool:
        pass


class Selectable(HasSelected):
    strategy_name = "org.platynui.strategies.Selectable"

    @abstractmethod
    def select(self):
        pass
