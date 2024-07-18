from abc import *

from ...core import StrategyBase

__all__ = ["Title"]


class Title(StrategyBase):
    strategy_name = "org.platynui.strategies.Title"

    @property
    @abstractmethod
    def title(self) -> str:
        pass
