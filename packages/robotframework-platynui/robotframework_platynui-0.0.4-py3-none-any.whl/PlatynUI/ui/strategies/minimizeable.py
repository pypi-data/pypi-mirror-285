from abc import abstractmethod

from ...core import StrategyBase

__all__ = ["HasCanMinimize", "Minimizable"]


class HasCanMinimize(StrategyBase):
    strategy_name = "org.platynui.strategies.HasCanMinimize"

    @property
    @abstractmethod
    def can_minimize(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_minimized(self) -> bool:
        pass


class Minimizable(StrategyBase):
    strategy_name = "org.platynui.strategies.Minimizable"

    @abstractmethod
    def minimize(self) -> None:
        pass
