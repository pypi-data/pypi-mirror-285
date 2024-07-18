from abc import abstractmethod

from ...core import StrategyBase

__all__ = ["HasCanClose", "Closeable"]


class HasCanClose(StrategyBase):
    strategy_name = "org.platynui.strategies.HasCanClose"

    @property
    @abstractmethod
    def can_close(self) -> bool:
        pass


class Closeable(StrategyBase):
    strategy_name = "org.platynui.strategies.Closeable"

    @abstractmethod
    def close(self) -> None:
        pass
