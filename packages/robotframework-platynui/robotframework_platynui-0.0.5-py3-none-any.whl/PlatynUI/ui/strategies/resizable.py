from abc import *

from ...core import StrategyBase
from ...core.types import Size

__all__ = ["Resizable"]


class Resizable(StrategyBase):
    strategy_name = "org.platynui.strategies.Resizable"

    @abstractmethod
    def resize(self, size: Size) -> None: ...
