from abc import abstractmethod

from ...core import StrategyBase

__all__ = ["Control"]


class Control(StrategyBase):
    strategy_name = "org.platynui.strategies.Control"

    @property
    @abstractmethod
    def has_focus(self) -> bool: ...

    @abstractmethod
    def try_ensure_focused(self) -> bool: ...
