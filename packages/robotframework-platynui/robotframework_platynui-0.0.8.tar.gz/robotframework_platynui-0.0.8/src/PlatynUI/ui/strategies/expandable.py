from abc import abstractmethod

from ...core import StrategyBase

__all__ = ["HasExpanded", "Expandable"]


class HasExpanded(StrategyBase):
    strategy_name = "org.platynui.strategies.HasExpanded"

    @property
    @abstractmethod
    def can_expand(self) -> bool: ...

    @property
    @abstractmethod
    def is_expanded(self) -> bool: ...


class Expandable(HasExpanded):
    strategy_name = "org.platynui.strategies.Expandable"

    @abstractmethod
    def expand(self) -> None: ...

    @abstractmethod
    def collapse(self) -> None: ...
