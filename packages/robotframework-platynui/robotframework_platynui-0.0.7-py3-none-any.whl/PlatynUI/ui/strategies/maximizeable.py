from abc import abstractmethod

from ...core import StrategyBase

__all__ = ["HasCanMaximize", "Maximizable"]


class HasCanMaximize(StrategyBase):
    strategy_name = "org.platynui.strategies.HasCanMaximize"

    @property
    @abstractmethod
    def can_maximize(self) -> bool:
        pass

    @property
    @abstractmethod
    def is_maximized(self) -> bool:
        pass


class Maximizable(StrategyBase):
    strategy_name = "org.platynui.strategies.Maximizable"

    @abstractmethod
    def maximize(self) -> None:
        pass
